import os
import csv
import platform
import matplotlib.pyplot as plt
from fpdf import FPDF
from datetime import datetime
from pathlib import Path
import flet as ft
from constants import (
    TVA,
    COUT_ADMIN,
    COUT_TRANSPORT,
    AUTRES_COUTS,
    COUT_MACHINE,
    COUT_OPERATEUR,
    DONNEES_MATERIAUX,
    FICHIER_CLIENTS,
    FICHIER_DEVIS,
)

# --- Chemin et import d'image ---
output_Path = Path(__file__).parent


def importimage(path: str) -> Path:
    filepath = output_Path / Path(path)
    return filepath


# =======================
# Fonctions utilitaires (CSV, PDF, calculs)
# =======================
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
    # Si le fichier n'existe pas ou est vide, on écrit également les en-têtes
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

    # Bloc des coordonnées du client (affiché à droite, au-dessus du numéro de devis)
    clients = lire_csv(FICHIER_CLIENTS)
    client_found = None
    for client in clients:
        if client["Nom"].strip().upper() == devis["Nom Client"].strip().upper():
            client_found = client
            break
    if client_found is not None:
        y_client = pdf.get_y()  # position actuelle
        pdf.set_xy(130, y_client)  # position à droite (x=130)
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

    # Tableau récapitulatif du devis (à gauche)
    pdf.set_font("Arial", size=12)
    pdf.set_fill_color(200, 220, 255)
    pdf.cell(50, 10, txt="Champ", border=1, align="C", fill=True)
    pdf.cell(140, 10, txt="Valeur", border=1, align="C", fill=True)
    pdf.ln()
    for key, value in devis.items():
        if key == "Marge":
            continue
        if key == "Remise" and float(value) == 0:
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


def calculer_temps_decoupe(longueur, vitesse):
    return (longueur / vitesse) / 60


def calculer_devis(materiau, longueur, pieces, marge, remise):
    donnees_materiau = DONNEES_MATERIAUX.get(materiau)
    if not donnees_materiau:
        raise ValueError("Matériau non trouvé")
    cout_materiau = longueur * donnees_materiau["Prix"] * pieces
    temps_decoupe = calculer_temps_decoupe(longueur, donnees_materiau["Vitesse"])
    cout_decoupe = temps_decoupe * (COUT_MACHINE + COUT_OPERATEUR)
    couts_fixes = COUT_ADMIN + (COUT_TRANSPORT * pieces) + (AUTRES_COUTS * pieces)
    cout_base = cout_materiau + cout_decoupe + couts_fixes
    prix = (cout_base * (1 + marge)) - remise
    prix_total = round(prix * (1 + TVA), 3)
    return {
        "Coût Matériau": round(cout_materiau, 3),
        "Coût Découpe": round(cout_decoupe, 3),
        "Coûts Fixes": round(couts_fixes, 3),
        "Coût Base": round(cout_base, 3),
        "Prix Total": prix_total,
    }


def ajouter_devis(nom_client, materiau, longueur, pieces, marge, remise):
    devis = calculer_devis(materiau, longueur, pieces, marge, remise)
    donnees_devis = {
        "Nom Client": nom_client.upper(),
        "Matériau": materiau,
        "Longueur": longueur,
        "Pièces": pieces,
        "Marge": marge,
        "Remise": remise,
        "Prix Total": devis["Prix Total"],
        "Date": datetime.now().strftime("%Y-%m-%d"),
    }
    ajouter_csv(FICHIER_DEVIS, donnees_devis)
    return donnees_devis


def generer_histogramme_image():
    """
    Génère l'histogramme des devis par intervalle de prix,
    l'enregistre dans 'histogram.png' et retourne le chemin du fichier.
    """
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
    materiau_dropdown = ft.Dropdown(
        label="Matériau",
        options=[
            ft.dropdown.Option(key=mat, text=mat) for mat in DONNEES_MATERIAUX.keys()
        ],
        value=list(DONNEES_MATERIAUX.keys())[0],
        width=300,
    )
    devis_longueur = ft.TextField(label="Longueur (mm)", width=300)
    devis_pieces = ft.TextField(label="Pièces", width=300)
    devis_marge = ft.TextField(label="Marge (%)", width=300)
    devis_remise = ft.TextField(label="Remise (€)", width=300)
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
            materiau = materiau_dropdown.value
            longueur = float(devis_longueur.value)
            pieces = int(devis_pieces.value)
            marge = float(devis_marge.value)
            remise = float(devis_remise.value)
            devis_data = ajouter_devis(
                devis_nom_client.value, materiau, longueur, pieces, marge, remise
            )
            pdf_file = generer_pdf(devis_data)
            devis_message.value = (
                f"Devis ajouté avec succès !\nPrix Total: {devis_data['Prix Total']:.2f} €\n"
                f"PDF généré: {pdf_file}"
            )
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
            materiau_dropdown,
            devis_longueur,
            devis_pieces,
            devis_marge,
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

    # Conteneur de contenu de l'onglet (on alterne entre client_view et devis_view)
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

    # --- Gestion du changement de vue ---
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

    # Assigner les événements aux boutons
    login_button.on_click = lambda e: switch_view("auth")
    auth_button.on_click = validate_auth

    # Ajouter les vues à la page
    page.add(login_view, auth_view, main_view)


# Lancez l'application Flet
ft.app(target=main)
