import os
import csv


class CSVManager:
    def __init__(self):
        pass

    def read_csv(self, file_path: str):
        if not os.path.exists(file_path):
            return []
        with open(file_path, "r", newline="", encoding="utf-8") as fichier:
            lecteur = csv.DictReader(fichier)
            rows = list(lecteur)
            return rows

    def write_csv(self, chemin_fichier: str, donnees, en_tetes):
        with open(chemin_fichier, "w", newline="", encoding="utf-8") as fichier:
            ecrivain = csv.DictWriter(fichier, fieldnames=en_tetes)
            ecrivain.writeheader()
            ecrivain.writerows(donnees)

    def ajouter_csv(self, chemin_fichier: str, donnees):
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
