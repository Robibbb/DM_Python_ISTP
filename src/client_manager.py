from fpdf import FPDF
from datetime import datetime
from constants import FICHIER_CLIENTS
from csv_manager import CSVManager
import flet as ft


class ClientManager:
    def __init__(self, csv_manager: CSVManager):
        self.csv_manager = csv_manager

    def add_client(
        self, nom: str, adresse: str, code_postal, telephone, entreprise: str = ""
    ):
        """
        Adds a new client to the client list if the client's name is unique.

        Args:
            nom (str): The name of the client.
            adresse (str): The address of the client.
            code_postal (str): The postal code of the client.
            telephone (str): The phone number of the client.
            entreprise (str, optional): The company name of the client. Defaults to "".

        Returns:
            bool: True if the client was added successfully, False if a client with the same name already exists.
        """
        clients = self.csv_manager.read_csv(FICHIER_CLIENTS)
        # Vérifier si un client avec le même nom existe déjà (comparaison en majuscules)
        for client in clients:
            if client["Nom"].upper().strip() == nom.upper().strip():
                return False

        # Si le nom est unique, on ajoute le client
        clients.append(
            {
                "Nom": nom.upper(),
                "Adresse": adresse.upper(),
                "Code Postal": code_postal,
                "Téléphone": telephone.replace(" ", ""),
                "Entreprise": entreprise.replace(" ", ""),
            }
        )
        self.csv_manager.write_csv(
            FICHIER_CLIENTS,
            clients,
            en_tetes=["Nom", "Adresse", "Code Postal", "Téléphone", "Entreprise"],
        )
        return True

    def get_client(self, name: str):
        """
        Retrieves a client by name.

        Args:
            name (str): The name of the client to retrieve.

        Returns:
            dict or None: A dictionary containing the client's information if found,
                          otherwise None.
        """
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
        Avant de modifier, on vérifie que le nouveau nom n'est pas déjà utilisé
        par un autre client (si le nouveau nom diffère de l'ancien).
        """
        clients = self.csv_manager.read_csv(FICHIER_CLIENTS)
        # Vérifier que le nouveau nom n'est pas déjà utilisé par un autre client
        for client in clients:
            if (
                client["Nom"].strip() == new_nom.upper().strip()
                and client["Nom"].strip() != old_name.upper().strip()
            ):
                raise Exception("Le nom est déjà pris par un autre client")
        found = False
        for client in clients:
            if client["Nom"].strip() == old_name.strip():
                client["Nom"] = new_nom.upper()
                client["Adresse"] = new_adresse.upper()
                client["Code Postal"] = new_code_postal
                client["Téléphone"] = new_telephone.replace(" ", "")
                client["Entreprise"] = new_entreprise.upper()
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
        Deletes the client whose name matches the given name.

        Args:
            name (str): The name of the client to delete.

        Raises:
            Exception: If no client is found with the given name.
        """
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
