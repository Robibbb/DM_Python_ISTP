# import platform

from fpdf import FPDF
from datetime import datetime

from constants import FICHIER_CLIENTS

# import platform
from fpdf import FPDF
from datetime import datetime
from csv_manager import CSVManager


class ClientManager:
    def __init__(self, csv_manager: CSVManager):
        self.csv_manager = csv_manager

    def add_client(self, nom, adresse, code_postal, telephone):
        clients = self.csv_manager.read_csv(FICHIER_CLIENTS)
        clients.append(
            {
                "Nom": nom.upper(),
                "Adresse": adresse.upper(),
                "Code Postal": code_postal,
                "Téléphone": telephone.replace(" ", ""),
            }
        )
        self.csv_manager.ecrire_csv(
            FICHIER_CLIENTS,
            clients,
            en_tetes=["Nom", "Adresse", "Code Postal", "Téléphone"],
        )

    def get_client(self):
        pass

    def update_client(self):
        pass

    def delete_client(self):
        pass
