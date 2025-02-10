# Structure des fichiers du projet

Ce projet est organisé de la manière suivante :


## Description des fichiers

- `client_manager.py` : Gère les opérations liées aux clients (ajout, mise à jour, suppression).
- `constants.py` : Contient les constantes utilisées dans le projet.
- `csv_manager.py` : Gère la lecture et l'écriture des fichiers CSV.
- `datas/inputs_csv/clients.csv` : Fichier CSV contenant les informations des clients.
- `datas/inputs_csv/devis.csv` : Fichier CSV contenant les informations des devis.
- `flet_test.py` : Contient le code pour l'interface utilisateur utilisant Flet.
- `histogramme_manager.py` : Gère la génération d'histogrammes à partir des données des devis.
- `pdf_manager.py` : Gère la génération de fichiers PDF pour les devis.
- `ProjetV6.py` : Contient le code principal du projet, y compris l'interface utilisateur Tkinter.
- `README.md` : Ce fichier, contenant la description et la structure du projet.
- `requirements.txt` : Liste des dépendances Python nécessaires pour exécuter le projet.

## Démarrage rapide

1. Installez les dépendances :
    ```sh
    pip install -r requirements.txt
    ```

2. Exécutez le projet :
    ```sh
    cd src && ./flet_test.py
    ```

3. Lancer Streamlit afin d'avoir l'histogramme :
    ```sh
    streamlit run streamhisto.py
    ```

## Utilisation

- Utilisez l'interface utilisateur pour gérer les clients et les devis.
- Les devis peuvent être ajoutés, mis à jour et supprimés.
- Les histogrammes peuvent être générés à partir des données des devis.
- Les devis peuvent être exportés en fichiers PDF.

## Dépendances

- [flet]() : Utilisé pour l'interface utilisateur.
- [matplotlib]() : Utilisé pour générer des histogrammes.
- [fpdf]() : Utilisé pour générer des fichiers PDF.

## Structure des dossiers

- [__pycache__]() : Contient les fichiers compilés Python.
- [assets]() : Contient les fichiers d'actifs (images, etc.).
- [datas]() : Contient les fichiers de données CSV.

N'hésitez pas à consulter chaque fichier pour plus de détails sur son contenu et son utilisation.

