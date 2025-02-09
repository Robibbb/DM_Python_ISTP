from fpdf import FPDF
from datetime import datetime
from constants import FICHIER_CLIENTS
from csv_manager import CSVManager


class ClientManager:
    def __init__(self, csv_manager: CSVManager):
        self.csv_manager = csv_manager

    def add_client(
        self, nom: str, adresse: str, code_postal, telephone, entreprise: str = ""
    ):
        clients = self.csv_manager.read_csv(FICHIER_CLIENTS)
        print("clients in add_client", clients)
        clients.append(
            {
                "Nom": nom.upper(),
                "Adresse": adresse.upper(),
                "Code Postal": code_postal,
                "Téléphone": telephone.replace(" ", ""),
                "Entreprise": entreprise.replace(" ", ""),
            }
        )
        print("clients after append", clients)
        self.csv_manager.write_csv(
            FICHIER_CLIENTS,
            clients,
            en_tetes=["Nom", "Adresse", "Code Postal", "Téléphone", "Entreprise"],
        )

    def get_client(self, name: str):
        """Retourne le client dont le nom correspond à 'name' ou None si non trouvé."""
        clients = self.csv_manager.read_csv(FICHIER_CLIENTS)
        for client in clients:
            if client["Nom"].strip() == name.strip():
                return client
        return None

    def modify_client(
        self,
        old_name: str,
        new_nom: str,
        new_adresse: str,
        new_code_postal,
        new_telephone: str,
        new_entreprise: str = "",
    ):
        """
        Modifie le client dont le nom est old_name avec les nouvelles valeurs.
        L'utilisation de .upper() et de .replace(" ", "") permet d'assurer une certaine cohérence.
        """
        clients = self.csv_manager.read_csv(FICHIER_CLIENTS)
        found = False
        for client in clients:
            if client["Nom"].strip() == old_name.strip():
                client["Nom"] = new_nom.upper()
                client["Adresse"] = new_adresse.upper()
                client["Code Postal"] = new_code_postal
                client["Téléphone"] = new_telephone.replace(" ", "")
                client["Entreprise"] = new_entreprise.replace(" ", "")
                found = True
                break
        if not found:
            raise Exception("Client non trouvé pour modification")
        self.csv_manager.write_csv(
            FICHIER_CLIENTS,
            clients,
            en_tetes=["Nom", "Adresse", "Code Postal", "Téléphone", "Entreprise"],
        )

    def delete_client(self, name: str):
        """
        Supprime le client dont le nom correspond à name.
        Si aucun client n'est supprimé, une exception est levée.
        """
        print("ok")
        clients = self.csv_manager.read_csv(FICHIER_CLIENTS)
        new_clients = [
            client for client in clients if client["Nom"].strip() != name.strip()
        ]
        if len(new_clients) == len(clients):
            raise Exception("Client non trouvé pour suppression")
        self.csv_manager.write_csv(
            FICHIER_CLIENTS,
            new_clients,
            en_tetes=["Nom", "Adresse", "Code Postal", "Téléphone", "Entreprise"],
        )
