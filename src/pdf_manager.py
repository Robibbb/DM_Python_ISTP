from constants import FICHIER_CLIENTS

# import platform
from fpdf import FPDF
from datetime import datetime
from csv_manager import CSVManager


class PDFManager:
    def __init__(self, csv_manager: CSVManager):
        self.csv_manager = csv_manager

    def generer_pdf(self, devis):
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
        clients = self.csv_manager.read_csv(FICHIER_CLIENTS)
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

        fichier_pdf = f"datas/outputs_pdf/devis_{devis['Nom Client']}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
        pdf.output(fichier_pdf)
        return fichier_pdf
