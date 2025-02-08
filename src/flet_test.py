import os
import csv
import matplotlib.pyplot as plt
from fpdf import FPDF
from datetime import datetime
from pathlib import Path
import flet as ft
from constants import (
    TVA,
    TARIF_MACHINE,
    TARIF_OPERATEUR,
    FRAIS_FIXES,
    METAL_PROPERTIES,
    FORME_COEFFICIENT,
    FICHIER_CLIENTS,
    FICHIER_DEVIS,
)

# --- Chemin et import d'image ---
output_Path = Path(__file__).parent


def importimage(path: str) -> Path:
    filepath = output_Path / Path(path)
    return filepath


def lire_csv(chemin_fichier):
    if not os.path.exists(chemin_fichier):
        return []
    with open(chemin_fichier, "r", newline="", encoding="utf-8") as fichier:
        lecteur = csv.DictReader(fichier)
        return list(lecteur)


def ecrire_csv(chemin_fichier, donnees, en_tetes):
    with open(chemin_fichier, "w", newline="", encoding="utf-8") as fichier:
        ecrivain = csv.DictWriter(fichier, fieldnames=en_tetes)
        ecrivain.writeheader()
        ecrivain.writerows(donnees)


def ajouter_csv(chemin_fichier, donnees):
    if not os.path.exists(chemin_fichier) or os.stat(chemin_fichier).st_size == 0:
        if isinstance(donnees, list):
            en_tetes = donnees[0].keys()
        else:
            en_tetes = donnees.keys()
        with open(chemin_fichier, "w", newline="", encoding="utf-8") as fichier:
            ecrivain = csv.DictWriter(fichier, fieldnames=en_tetes)
            ecrivain.writeheader()
            if isinstance(donnees, list):
                ecrivain.writerows(donnees)
            else:
                ecrivain.writerow(donnees)
    else:
        en_tetes = (
            list(donnees[0].keys())
            if isinstance(donnees, list)
            else list(donnees.keys())
        )
        with open(chemin_fichier, "a", newline="", encoding="utf-8") as fichier:
            ecrivain = csv.DictWriter(fichier, fieldnames=en_tetes)
            if isinstance(donnees, list):
                ecrivain.writerows(donnees)
            else:
                ecrivain.writerow(donnees)


def generer_pdf(devis):
    pdf = FPDF()
    pdf.add_page()

    # Titre de l'entreprise (centré)
    pdf.set_font("Arial", "B", size=16)
    pdf.cell(0, 10, txt="CutSharp", ln=True, align="C")
    pdf.ln(5)

    # Titre "DEVIS" (centré)
    pdf.set_font("Arial", "B", size=16)
    pdf.cell(0, 10, txt="DEVIS", ln=True, align="C")
    pdf.ln(10)

    # Coordonnées de l'entreprise (affichées à gauche)
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 5, txt="CutSharp", ln=True, align="L")
    pdf.cell(0, 5, txt="Rue Copernic", ln=True, align="L")
    pdf.cell(0, 5, txt="42100 SAINT-ETIENNE", ln=True, align="L")
    pdf.cell(0, 5, txt="Tel : 04.78.78.00.00", ln=True, align="L")
    pdf.cell(0, 5, txt="contact@cutsharp.fr - www.cutsharp", ln=True, align="L")
    date_devis = datetime.now().strftime("%d-%m-%Y")
    pdf.cell(0, 5, txt=f"Date : {date_devis}", ln=True, align="L")
    pdf.ln(10)

    # Bloc des coordonnées du client (affiché à droite)
    clients = lire_csv(FICHIER_CLIENTS)
    client_found = None
    for client in clients:
        if client["Nom"].strip().upper() == devis["Nom Client"].strip().upper():
            client_found = client
            break
    if client_found is not None:
        y_client = pdf.get_y()
        pdf.set_xy(130, y_client)
        pdf.set_font("Arial", "", 12)
        pdf.cell(60, 6, txt=client_found["Nom"], align="R", ln=1)
        pdf.set_x(130)
        pdf.cell(60, 6, txt=client_found["Adresse"], align="R", ln=1)
        pdf.set_x(130)
        pdf.cell(60, 6, txt=client_found["Code Postal"], align="R", ln=1)
        pdf.set_x(130)
        pdf.cell(60, 6, txt="Tel: " + client_found["Téléphone"], align="R", ln=1)
        pdf.ln(10)

    # Numéro de devis (centré)
    numero_devis = "".join(
        filter(
            str.isdigit,
            f"devis_{devis['Nom Client']}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf",
        )
    )
    pdf.set_font("Arial", "B", size=12)
    pdf.cell(0, 10, txt=f"Devis n° {numero_devis}", ln=True, align="C")
    pdf.ln(10)

    # Tableau récapitulatif du devis
    pdf.set_font("Arial", size=12)
    pdf.set_fill_color(200, 220, 255)
    pdf.cell(50, 10, txt="Champ", border=1, align="C", fill=True)
    pdf.cell(140, 10, txt="Valeur", border=1, align="C", fill=True)
    pdf.ln()
    for key, value in devis.items():
        if key in ["Marge (%)"]:  # la marge n'est plus modifiable
            continue
        if key == "Prix Total" and float(value) == 0:
            continue
        pdf.cell(50, 10, txt=key, border=1)
        pdf.cell(140, 10, txt=str(value), border=1)
        pdf.ln()

    pdf.set_y(-31)
    pdf.set_font("Arial", "I", size=10)
    pdf.cell(0, 10, txt="Créé par CutSharp", ln=True, align="C")

    fichier_pdf = (
        f"devis_{devis['Nom Client']}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
    )
    pdf.output(fichier_pdf)
    return fichier_pdf


def ajouter_client(nom, adresse, code_postal, telephone):
    clients = lire_csv(FICHIER_CLIENTS)
    clients.append(
        {
            "Nom": nom.upper(),
            "Adresse": adresse.upper(),
            "Code Postal": code_postal,
            "Téléphone": telephone.replace(" ", ""),
        }
    )
    ecrire_csv(
        FICHIER_CLIENTS,
        clients,
        en_tetes=["Nom", "Adresse", "Code Postal", "Téléphone"],
    )


# =======================
# Nouveau calcul de devis
# =======================
def calculer_devis(metal, quantite_ml, forme, remise_client):
    # Marge fixe de 50 %
    marge = 50 / 100
    # Conversion de la remise client en décimal (entrée en %)
    remise_client = remise_client / 100

    # Constantes

    # Propriétés du métal sélectionné
    props = METAL_PROPERTIES.get(metal)
    if not props:
        raise ValueError("Métal non trouvé")
    coef_metal = props["coef"]
    usure_lame = props["usure"]
    vitesse = props["vitesse"]
    cout_materiaux_unit = props["cout_materiaux"]

    # Coefficient de la forme de découpe
    coef_forme = FORME_COEFFICIENT.get(forme)
    if coef_forme is None:
        raise ValueError("Forme de découpe non valide")

    # Calcul du temps de découpe (en heures)
    temps_decoupe = (quantite_ml / vitesse) / 60

    # Coût de découpe
    cout_decoupe = (
        temps_decoupe * (TARIF_MACHINE + TARIF_OPERATEUR + usure_lame) * coef_forme
    )

    # Coût des matériaux (conversion mm -> m)
    cout_materiaux = (quantite_ml / 1000) * cout_materiaux_unit * coef_metal

    base_cost = cout_materiaux + cout_decoupe + FRAIS_FIXES

    # Application de la marge fixe et de la remise client
    prix_general = base_cost + (base_cost * marge) - (base_cost * remise_client)
    prix_total = round(prix_general * (1 + TVA), 3)

    return {
        "Coût Matériaux": round(cout_materiaux, 3),
        "Coût Découpe": round(cout_decoupe, 3),
        "Frais Fixes": FRAIS_FIXES,
        "Prix Total": prix_total,
    }


def ajouter_devis(nom_client, metal, quantite_ml, forme, remise_client):
    devis = calculer_devis(metal, quantite_ml, forme, remise_client)
    donnees_devis = {
        "Nom Client": nom_client.upper(),
        "Métal": metal,
        "Quantité (mm)": quantite_ml,
        "Forme": forme,
        "Remise (%)": remise_client,  # valeur saisie par l'utilisateur (en %)
        "Prix Total": devis["Prix Total"],
        "Coût Matériaux": devis["Coût Matériaux"],
        "Coût Découpe": devis["Coût Découpe"],
        "Frais Fixes": devis["Frais Fixes"],
        "Date": datetime.now().strftime("%Y-%m-%d"),
    }
    ajouter_csv(FICHIER_DEVIS, donnees_devis)
    return donnees_devis


def generer_histogramme_image():
    devis_list = lire_csv(FICHIER_DEVIS)
    try:
        montants = [float(devis["Prix Total"]) for devis in devis_list]
    except KeyError:
        return None

    intervalles = ["0-1000", "1000-5000", "5000-10000", ">10000"]
    comptes = [
        sum(1 for montant in montants if 0 <= montant <= 1000),
        sum(1 for montant in montants if 1000 < montant <= 5000),
        sum(1 for montant in montants if 5000 < montant <= 10000),
        sum(1 for montant in montants if montant > 10000),
    ]
    plt.figure()
    plt.bar(intervalles, comptes)
    plt.title("Histogramme des devis par intervalle de prix")
    plt.xlabel("Intervalle de prix (€)")
    plt.ylabel("Nombre de devis")
    image_path = "histogram.png"
    plt.savefig(image_path)
    plt.close()
    return image_path


# =======================
# Interface graphique avec Flet
# =======================
def main(page: ft.Page):
    page.title = "CutSharp - Gestion des Clients et Devis"
    page.window_width = 600
    page.window_height = 700

    # --- Création des vues ---
    # 1. Vue Login
    login_button = ft.ElevatedButton("Se connecter")
    login_view = ft.Column(
        [
            ft.Text("Bienvenue sur CutSharp", size=24),
            login_button,
        ],
        alignment="center",
        horizontal_alignment="center",
        spacing=20,
        visible=True,
    )

    # 2. Vue Authentification
    username_field = ft.TextField(label="Nom d'utilisateur", width=300)
    password_field = ft.TextField(
        label="Mot de passe", password=True, can_reveal_password=True, width=300
    )
    auth_button = ft.ElevatedButton("Se connecter")
    auth_view = ft.Column(
        [
            ft.Text("Veuillez vous authentifier", size=20),
            username_field,
            password_field,
            auth_button,
        ],
        alignment="center",
        horizontal_alignment="center",
        spacing=20,
        visible=False,
    )

    # 3. Vue principale avec onglets Clients / Devis
    # --- Onglet Clients ---
    client_nom = ft.TextField(label="Nom", width=300)
    client_adresse = ft.TextField(label="Adresse", width=300)
    client_code_postal = ft.TextField(label="Code Postal", width=300)
    client_telephone = ft.TextField(label="Téléphone", width=300)
    client_message = ft.Text()

    def on_ajouter_client(e):
        try:
            ajouter_client(
                client_nom.value,
                client_adresse.value,
                client_code_postal.value,
                client_telephone.value,
            )
            client_message.value = "Client ajouté avec succès !"
            # Mise à jour du champ Nom Client dans la vue Devis
            devis_nom_client.value = client_nom.value
            client_nom.value = ""
            client_adresse.value = ""
            client_code_postal.value = ""
            client_telephone.value = ""
            page.show_snack_bar(ft.SnackBar(ft.Text("Client ajouté avec succès !")))
            page.update()
        except Exception as ex:
            page.show_snack_bar(ft.SnackBar(ft.Text(f"Erreur: {ex}")))
            page.update()

    client_view = ft.Column(
        [
            ft.Text("Gestion des Clients", size=20),
            client_nom,
            client_adresse,
            client_code_postal,
            client_telephone,
            ft.ElevatedButton("Ajouter Client", on_click=on_ajouter_client),
            client_message,
        ],
        spacing=10,
        alignment="center",
        horizontal_alignment="center",
    )

    # --- Onglet Devis ---
    devis_nom_client = ft.TextField(label="Nom Client", width=300)
    devis_detail_client = ft.Text("", color="blue")
    # Dropdown pour sélectionner le métal
    metal_dropdown = ft.Dropdown(
        label="Métal",
        options=[
            ft.dropdown.Option(key=metal, text=metal)
            for metal in METAL_PROPERTIES.keys()
        ],
        value=list(METAL_PROPERTIES.keys())[0],
        width=300,
    )
    # Champ pour la quantité à découper en mm
    devis_quantite = ft.TextField(label="Quantité à découper (mm)", width=300)
    # Dropdown pour la forme de découpe
    forme_dropdown = ft.Dropdown(
        label="Forme de découpe",
        options=[
            ft.dropdown.Option(key=forme, text=forme)
            for forme in FORME_COEFFICIENT.keys()
        ],
        value="Droite",
        width=300,
    )
    # Le champ de marge a été supprimé puisque la marge est imposée à 50 %
    devis_remise = ft.TextField(label="Remise client (%)", width=300)
    devis_message = ft.Text()
    histogram_image = ft.Image(src="", width=400, visible=False)

    def on_rechercher_client(e):
        nom = devis_nom_client.value.strip()
        if not nom:
            page.show_snack_bar(
                ft.SnackBar(ft.Text("Veuillez entrer un nom de client."))
            )
            return
        clients = lire_csv(FICHIER_CLIENTS)
        found = None
        for client in clients:
            if client["Nom"].strip().upper() == nom.upper():
                found = client
                break
        if found:
            devis_detail_client.value = (
                f"Adresse: {found['Adresse']}\n"
                f"Code Postal: {found['Code Postal']}\n"
                f"Téléphone: {found['Téléphone']}"
            )
        else:
            devis_detail_client.value = ""
            page.show_snack_bar(
                ft.SnackBar(
                    ft.Text(
                        "Le client n'est pas encore enregistré. Veuillez l'enregistrer au préalable."
                    )
                )
            )
        page.update()

    def on_ajouter_devis(e):
        try:
            metal = metal_dropdown.value
            quantite_ml = float(devis_quantite.value)
            forme = forme_dropdown.value
            remise = float(devis_remise.value)
            # Appel de la fonction en fixant la marge à 50%
            devis_data = ajouter_devis(
                devis_nom_client.value, metal, quantite_ml, forme, remise
            )
            pdf_file = generer_pdf(devis_data)
            devis_message.value = f"Devis ajouté avec succès !\nPrix Total: {devis_data['Prix Total']:.2f} €\nPDF généré: {pdf_file}"
            page.show_snack_bar(ft.SnackBar(ft.Text("Devis ajouté et PDF généré.")))
            page.update()
        except Exception as ex:
            page.show_snack_bar(ft.SnackBar(ft.Text(f"Erreur: {ex}")))
            page.update()

    def on_generer_histogramme(e):
        image_path = generer_histogramme_image()
        if image_path:
            histogram_image.src = image_path
            histogram_image.visible = True
            page.update()
        else:
            page.show_snack_bar(
                ft.SnackBar(ft.Text("Aucun devis trouvé ou format CSV incorrect."))
            )
            page.update()

    devis_view = ft.Column(
        [
            ft.Text("Gestion des Devis", size=20),
            devis_nom_client,
            ft.ElevatedButton("Rechercher Client", on_click=on_rechercher_client),
            devis_detail_client,
            metal_dropdown,
            devis_quantite,
            forme_dropdown,
            devis_remise,
            ft.ElevatedButton("Ajouter Devis", on_click=on_ajouter_devis),
            ft.ElevatedButton("Générer Histogramme", on_click=on_generer_histogramme),
            histogram_image,
            devis_message,
        ],
        spacing=10,
        alignment="center",
        horizontal_alignment="center",
    )

    # Conteneur pour alterner entre la gestion des Clients et des Devis
    content_container = ft.Container(content=client_view)

    def switch_tab(tab: str):
        if tab == "clients":
            content_container.content = client_view
        else:
            content_container.content = devis_view
        page.update()

    main_menu = ft.Row(
        [
            ft.ElevatedButton(
                "Gestion des Clients", on_click=lambda e: switch_tab("clients")
            ),
            ft.ElevatedButton(
                "Gestion des Devis", on_click=lambda e: switch_tab("devis")
            ),
        ],
        alignment="center",
        spacing=20,
    )

    main_view = ft.Column(
        [main_menu, content_container],
        spacing=20,
        alignment="center",
        horizontal_alignment="center",
        visible=False,
    )

    # Gestion du changement de vue
    def switch_view(view_name: str):
        login_view.visible = view_name == "login"
        auth_view.visible = view_name == "auth"
        main_view.visible = view_name == "main"
        page.update()

    def validate_auth(e):
        if username_field.value == "Jean" and password_field.value == "TEST":
            switch_view("main")
        else:
            page.show_snack_bar(
                ft.SnackBar(ft.Text("Nom d'utilisateur ou mot de passe incorrect"))
            )
            page.update()

    # Assignation des événements aux boutons
    login_button.on_click = lambda e: switch_view("auth")
    auth_button.on_click = validate_auth

    page.add(login_view, auth_view, main_view)


# Lancez l'application Flet
ft.app(target=main)
