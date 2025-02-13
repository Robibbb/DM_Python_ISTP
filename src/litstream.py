import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Import de votre manager et constantes
from csv_manager import CSVManager
from histogramme_manager import HistogrammeManager
from constants import FICHIER_CLIENTS, FICHIER_DEVIS


# 1) Instanciation des outils CSVManager et HistogrammeManager
csv_manager = CSVManager()
histogram_manager = HistogrammeManager(csv_manager)


# 2) Titre de l'application
st.title("Application de Visualisation")

# =====================================================================
# PARTIE A : Histogramme des devis (via HistogrammeManager)
# =====================================================================
st.header("Histogramme des devis")

if st.button("Générer l'histogramme des devis"):
    # Génération du diagramme via votre classe HistogrammeManager
    image_path = histogram_manager.generer_histogramme_image()

    if image_path:
        st.success("Histogramme généré avec succès !")
        st.image(image_path, caption="Histogramme des devis par intervalle de prix")
    else:
        st.error(
            "Erreur lors de la génération de l'histogramme (fichier CSV manquant ou invalide)."
        )


# =====================================================================
# PARTIE B : Diagramme en barres - Clients par département
# =====================================================================
st.header("Diagramme en barres - Clients par département")

if st.button("Générer le diagramme des clients"):
    # Lecture du fichier "clients.csv" (adaptez le chemin si besoin)
    try:
        df_clients = pd.read_csv(FICHIER_CLIENTS, sep=",", encoding="utf-8")
    except FileNotFoundError:
        st.error("Le fichier 'clients.csv' est introuvable.")
    else:
        # 1) Nettoyage : on enlève les lignes sans code postal
        df_clients = df_clients.dropna(subset=["Code Postal"])

        # 2) Convertir en chaîne de caractères et extraire les 2 premiers chiffres
        df_clients["Code Postal"] = df_clients["Code Postal"].astype(str)
        df_clients["Département"] = df_clients["Code Postal"].str[:2]

        # 3) Garder uniquement les départements numériques (ex. "42", "69", etc.)
        df_clients = df_clients[df_clients["Département"].str.isdigit()]

        # 4) Comptage du nombre de clients par département
        departement_counts = df_clients["Département"].value_counts()

        # 5) Création du diagramme en barres
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.bar(departement_counts.index, departement_counts.values)
        ax.set_xlabel("Département (2 premiers chiffres)")
        ax.set_ylabel("Nombre de clients")
        ax.set_title("Répartition des clients par département")

        # 6) Affichage dans Streamlit
        st.pyplot(fig)
