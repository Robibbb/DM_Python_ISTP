import os
import csv
import platform
import tkinter as tk
from tkinter import messagebox
from fpdf import FPDF
import matplotlib.pyplot as plt
from datetime import datetime
from pathlib import Path

Output_Path = Path(__file__).parent
def importimage(path: str) -> Path:
    filepath = Output_Path / Path(path)
    return filepath

# =======================
# Constantes et données
# =======================
TVA = 0.2
COUT_ADMIN = 7          # € par devis
COUT_TRANSPORT = 0.5    # € par pièce
AUTRES_COUTS = 0.03     # € par pièce
COUT_MACHINE = 0.3      # €/heure
COUT_OPERATEUR = 45     # €/heure

DONNEES_MATERIAUX = {
    "Fonte": {"Lame": "Diamanté", "Vitesse": 200, "Prix": 0.15},
    "Acier": {"Lame": "Carbure", "Vitesse": 200, "Prix": 0.05},
    "Cuivre": {"Lame": "Carbure", "Vitesse": 350, "Prix": 0.05},
    "Inox": {"Lame": "Carbure", "Vitesse": 140, "Prix": 0.05},
    "Titane": {"Lame": "Carbure revêtue TiN", "Vitesse": 100, "Prix": 0.10},
    "Aluminium": {"Lame": "TCT", "Vitesse": 800, "Prix": 0.05}
}

FICHIER_CLIENTS = "clients.csv"
FICHIER_DEVIS = "devis.csv"

# =======================
# Fonctions utilitaires
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
        en_tetes = list(donnees[0].keys()) if isinstance(donnees, list) else list(donnees.keys())
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

    # Bloc des coordonnées du client (affiché à droite, **au-dessus** du numéro de devis)
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
        # Préfixe "Tel:" ajouté devant le numéro de téléphone
        pdf.cell(60, 6, txt="Tel: " + client_found["Téléphone"], align="R", ln=1)
        pdf.ln(10)

    # Numéro de devis (centré)
    numero_devis = ''.join(filter(str.isdigit, f"devis_{devis['Nom Client']}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"))
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
        # On ignore la clé "Marge"
        if key == "Marge":
            continue
        # On affiche la remise uniquement si elle est différente de 0
        if key == "Remise" and float(value) == 0:
            continue
        pdf.cell(50, 10, txt=key, border=1)
        pdf.cell(140, 10, txt=str(value), border=1)
        pdf.ln()

    # Mention en bas de page
    pdf.set_y(-31)
    pdf.set_font("Arial", "I", size=10)
    pdf.cell(0, 10, txt="Créé par CutSharp", ln=True, align="C")

    fichier_pdf = f"devis_{devis['Nom Client']}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
    pdf.output(fichier_pdf)
    return fichier_pdf

def ajouter_client(nom, adresse, code_postal, telephone):
    clients = lire_csv(FICHIER_CLIENTS)
    clients.append({
        "Nom": nom.upper(),
        "Adresse": adresse.upper(),
        "Code Postal": code_postal,
        "Téléphone": telephone.replace(" ", "")
    })
    ecrire_csv(FICHIER_CLIENTS, clients, en_tetes=["Nom", "Adresse", "Code Postal", "Téléphone"])

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
        "Prix Total": prix_total
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
        "Date": datetime.now().strftime("%Y-%m-%d")
    }
    ajouter_csv(FICHIER_DEVIS, donnees_devis)
    return donnees_devis

def generer_histogramme():
    devis_list = lire_csv(FICHIER_DEVIS)
    try:
        montants = [float(devis["Prix Total"]) for devis in devis_list]
    except KeyError:
        messagebox.showerror("Erreur", "Aucun devis trouvé ou format CSV incorrect.")
        return

    intervalles = ["0-1000", "1000-5000", "5000-10000", ">10000"]
    comptes = [
        sum(1 for montant in montants if 0 <= montant <= 1000),
        sum(1 for montant in montants if 1000 < montant <= 5000),
        sum(1 for montant in montants if 5000 < montant <= 10000),
        sum(1 for montant in montants if montant > 10000)
    ]
    plt.bar(intervalles, comptes)
    plt.title("Histogramme des devis par intervalle de prix")
    plt.xlabel("Intervalle de prix (€)")
    plt.ylabel("Nombre de devis")
    plt.show()

# =======================
# Interface graphique
# =======================
class CutSharpApp(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.title("CutSharp - Gestion des Clients et Devis")
        self.geometry("600x700")
        # --- Fond d'écran ---
        self.bg_image = tk.PhotoImage(file=str(importimage("background.PNG")))
        bg_label = tk.Label(self, image=self.bg_image)
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        # Conteneur principal pour les frames
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (LoginFrame, AuthFrame, MainFrame):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        self.show_frame("LoginFrame")

    def show_frame(self, page_name):
        background = tk.PhotoImage(file=str(importimage("background.png")))
        frame = self.frames[page_name]
        frame.tkraise()

class LoginFrame(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        lbl = tk.Label(self, text="Bienvenue sur CutSharp", font=("Arial", 18))
        lbl.pack(pady=50)
        btn_connexion = tk.Button(self, text="Se connecter", font=("Arial", 14),
                                  command=lambda: controller.show_frame("AuthFrame"))
        btn_connexion.pack(pady=20)

class AuthFrame(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        lbl = tk.Label(self, text="Veuillez vous authentifier", font=("Arial", 16))
        lbl.pack(pady=20)
        tk.Label(self, text="Nom d'utilisateur:").pack()
        self.username_entry = tk.Entry(self)
        self.username_entry.pack(pady=5)
        tk.Label(self, text="Mot de passe:").pack()
        self.password_entry = tk.Entry(self, show="*")
        self.password_entry.pack(pady=5)
        btn_auth = tk.Button(self, text="Se connecter", font=("Arial", 14), command=self.valider_auth)
        btn_auth.pack(pady=20)

    def valider_auth(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        if username == "Jean" and password == "TEST":
            self.controller.show_frame("MainFrame")
        else:
            messagebox.showerror("Erreur", "Nom d'utilisateur ou mot de passe incorrect")

class MainFrame(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        # ----------------------------
        # Menu en haut avec deux boutons centrés
        # ----------------------------
        menu_frame = tk.Frame(self)
        menu_frame.pack(side=tk.TOP, fill=tk.X)
        btn_clients = tk.Button(menu_frame, text="Gestion des Clients", command=self.show_clients)
        btn_clients.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        btn_devis = tk.Button(menu_frame, text="Gestion des Devis", command=self.show_devis)
        btn_devis.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        menu_frame.grid_columnconfigure(0, weight=1)
        menu_frame.grid_columnconfigure(1, weight=1)

        # ----------------------------
        # Conteneur pour les frames de contenu
        # ----------------------------
        self.content_frame = tk.Frame(self)
        self.content_frame.pack(fill=tk.BOTH, expand=True)

        self.frame_clients = tk.Frame(self.content_frame)
        self.frame_devis = tk.Frame(self.content_frame)
        for frame in (self.frame_clients, self.frame_devis):
            frame.grid(row=0, column=0, sticky="nsew")

        self.build_client_ui(self.frame_clients)
        self.build_devis_ui(self.frame_devis)

        # On démarre par la gestion des clients
        self.show_clients()

    def build_client_ui(self, parent):
        inner_frame = tk.Frame(parent)
        inner_frame.pack(expand=True)
        lbl_clients = tk.Label(inner_frame, text="Gestion des Clients", font=("Arial", 14))
        lbl_clients.grid(row=0, column=0, columnspan=2, pady=10)
        tk.Label(inner_frame, text="Nom:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.nom_entry = tk.Entry(inner_frame)
        self.nom_entry.grid(row=1, column=1, padx=5, pady=5)
        tk.Label(inner_frame, text="Adresse:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.adresse_entry = tk.Entry(inner_frame)
        self.adresse_entry.grid(row=2, column=1, padx=5, pady=5)
        tk.Label(inner_frame, text="Code Postal:").grid(row=3, column=0, sticky="e", padx=5, pady=5)
        self.code_postal_entry = tk.Entry(inner_frame)
        self.code_postal_entry.grid(row=3, column=1, padx=5, pady=5)
        tk.Label(inner_frame, text="Téléphone:").grid(row=4, column=0, sticky="e", padx=5, pady=5)
        self.telephone_entry = tk.Entry(inner_frame)
        self.telephone_entry.grid(row=4, column=1, padx=5, pady=5)
        btn_ajouter_client = tk.Button(inner_frame, text="Ajouter Client", command=self.soumettre_client)
        btn_ajouter_client.grid(row=5, column=0, columnspan=2, pady=10)

    def build_devis_ui(self, parent):
        # Nouvelle organisation de la grille pour inclure la recherche du client
        inner_frame = tk.Frame(parent)
        inner_frame.pack(expand=True)
        lbl_devis = tk.Label(inner_frame, text="Gestion des Devis", font=("Arial", 14))
        lbl_devis.grid(row=0, column=0, columnspan=2, pady=10)
        
        # Saisie du nom du client et bouton de recherche
        tk.Label(inner_frame, text="Nom Client:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.nom_client_entry = tk.Entry(inner_frame)
        self.nom_client_entry.grid(row=1, column=1, padx=5, pady=5)
        
        btn_rechercher_client = tk.Button(inner_frame, text="Rechercher Client", command=self.rechercher_client)
        btn_rechercher_client.grid(row=2, column=0, columnspan=2, padx=5, pady=5)
        
        # Label pour afficher les coordonnées du client
        self.detail_client_label = tk.Label(inner_frame, text="", font=("Arial", 10), fg="blue")
        self.detail_client_label.grid(row=3, column=0, columnspan=2, padx=5, pady=5)
        
        # Les autres champs du devis (décalés de 2 lignes)
        tk.Label(inner_frame, text="Matériau:").grid(row=4, column=0, sticky="e", padx=5, pady=5)
        self.materiau_var = tk.StringVar(inner_frame)
        self.materiau_var.set(list(DONNEES_MATERIAUX.keys())[0])
        self.materiau_menu = tk.OptionMenu(inner_frame, self.materiau_var, *DONNEES_MATERIAUX.keys())
        self.materiau_menu.grid(row=4, column=1, padx=5, pady=5)
        
        tk.Label(inner_frame, text="Longueur (mm):").grid(row=5, column=0, sticky="e", padx=5, pady=5)
        self.longueur_entry = tk.Entry(inner_frame)
        self.longueur_entry.grid(row=5, column=1, padx=5, pady=5)
        
        tk.Label(inner_frame, text="Pièces:").grid(row=6, column=0, sticky="e", padx=5, pady=5)
        self.pieces_entry = tk.Entry(inner_frame)
        self.pieces_entry.grid(row=6, column=1, padx=5, pady=5)
        
        tk.Label(inner_frame, text="Marge (%):").grid(row=7, column=0, sticky="e", padx=5, pady=5)
        self.marge_entry = tk.Entry(inner_frame)
        self.marge_entry.grid(row=7, column=1, padx=5, pady=5)
        
        tk.Label(inner_frame, text="Remise (€):").grid(row=8, column=0, sticky="e", padx=5, pady=5)
        self.remise_entry = tk.Entry(inner_frame)
        self.remise_entry.grid(row=8, column=1, padx=5, pady=5)
        
        btn_ajouter_devis = tk.Button(inner_frame, text="Ajouter Devis", command=self.soumettre_devis)
        btn_ajouter_devis.grid(row=9, column=0, columnspan=2, pady=10)
        
        btn_histogramme = tk.Button(inner_frame, text="Générer Histogramme", command=generer_histogramme)
        btn_histogramme.grid(row=10, column=0, columnspan=2, pady=10)

    def rechercher_client(self):
        """Recherche le client dans le fichier clients.csv et affiche ses coordonnées."""
        nom = self.nom_client_entry.get().strip()
        if not nom:
            messagebox.showerror("Erreur", "Veuillez entrer un nom de client.")
            return
        clients = lire_csv(FICHIER_CLIENTS)
        found = None
        for client in clients:
            if client["Nom"].strip().upper() == nom.upper():
                found = client
                break
        if found:
            details = (f"Adresse: {found['Adresse']}\n"
                       f"Code Postal: {found['Code Postal']}\n"
                       f"Téléphone: {found['Téléphone']}")
            self.detail_client_label.config(text=details)
        else:
            self.detail_client_label.config(text="")
            messagebox.showerror("Erreur", "Le client n'est pas encore enregistré. Veuillez l'enregistrer au préalable.")

    def show_clients(self):
        self.frame_clients.tkraise()

    def show_devis(self):
        self.frame_devis.tkraise()

    def soumettre_client(self):
        try:
            # Ajoute le client dans le CSV
            ajouter_client(
                self.nom_entry.get(),
                self.adresse_entry.get(),
                self.code_postal_entry.get(),
                self.telephone_entry.get()
            )
            # Met à jour le champ "Nom Client" de la gestion des devis
            self.nom_client_entry.delete(0, tk.END)
            self.nom_client_entry.insert(0, self.nom_entry.get())
            messagebox.showinfo("Succès", "Client ajouté avec succès !")
        except Exception as e:
            messagebox.showerror("Erreur", str(e))

    def soumettre_devis(self):
        try:
            devis = ajouter_devis(
                self.nom_client_entry.get(),
                self.materiau_var.get(),
                float(self.longueur_entry.get()),
                int(self.pieces_entry.get()),
                float(self.marge_entry.get()),
                float(self.remise_entry.get())
            )
            fichier_pdf = generer_pdf(devis)
            messagebox.showinfo("Succès", f"Devis ajouté avec succès !\nPrix Total: {devis['Prix Total']:.2f} €\nPDF généré: {fichier_pdf}")
            systeme = platform.system()
            if systeme == "Windows":
                os.startfile(fichier_pdf)
            elif systeme == "Darwin":
                os.system(f"open '{fichier_pdf}'")
            elif systeme == "Linux":
                os.system(f"xdg-open '{fichier_pdf}'")
            else:
                messagebox.showwarning("Attention", f"Système non reconnu : {systeme}\nLe fichier PDF n'a pas été ouvert automatiquement.")
        except Exception as e:
            messagebox.showerror("Erreur", str(e))

# =======================
# Programme principal
# =======================
if __name__ == "__main__":
    app = CutSharpApp()
    app.mainloop()
