""" Module CSVManager"""

import csv
import os


class CSVManager:
    def __init__(self):
        pass

    def read_csv(self, file_path: str):
        """
        Reads a CSV file and returns its contents as a list of dictionaries.

        Args:
            file_path (str): The path to the CSV file.

        Returns:
            list: A list of dictionaries representing the rows in the CSV file.
                  Returns an empty list if the file does not exist.
        """
        if not os.path.exists(file_path):
            return []
        with open(file_path, "r", newline="", encoding="utf-8") as fichier:
            lecteur = csv.DictReader(fichier)
            rows = list(lecteur)
            return rows

    def write_csv(self, chemin_fichier: str, donnees: list, en_tetes):
        """
        Write data to a CSV file.
        Args:
            chemin_fichier (str): The path to the CSV file.
            donnees (list): A list of dictionaries containing the data to write.
            en_tetes (list): A list of strings representing the header row of the CSV file.
        Returns:
            None
        """

        with open(chemin_fichier, "w", newline="", encoding="utf-8") as fichier:
            ecrivain = csv.DictWriter(fichier, fieldnames=en_tetes)
            ecrivain.writeheader()
            ecrivain.writerows(donnees)

    def ajouter_csv(self, chemin_fichier: str, donnees: list):
        """
        Ajoute des données à un fichier CSV. Si le fichier n'existe pas ou est vide,
        les en-têtes sont également écrits.

        Args:
            chemin_fichier (str): Le chemin du fichier CSV.
            donnees (list): Les données à ajouter au
            fichier CSV. Peut être une liste de dictionnaires
                            ou un seul dictionnaire.

        Raises:
            OSError: Si une erreur se produit lors de
            l'ouverture ou de l'écriture dans le fichier.
        """
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
