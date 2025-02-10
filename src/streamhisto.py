import streamlit as st
from histogramme_manager import (
    HistogrammeManager,
)  # Adaptation selon votre arborescence
from csv_manager import CSVManager
from constants import FICHIER_DEVIS

# Créer une instance du CSVManager (en fonction de votre implémentation)
csv_manager = CSVManager()

# Créer une instance du HistogrammeManager en lui passant le CSVManager
histogram_manager = HistogrammeManager(csv_manager)

# Titre de l'application
st.title("Application d'Histogramme des Devis")

# Bouton pour générer l'histogramme
if st.button("Générer l'histogramme"):
    # Génération de l'histogramme
    image_path = histogram_manager.generer_histogramme_image()
    if image_path:
        st.success("Histogramme généré avec succès !")
        # Affichage de l'image générée
        st.image(image_path, caption="Histogramme des devis par intervalle de prix")
    else:
        st.error(
            "Erreur lors de la génération de l'histogramme. Veuillez vérifier le fichier CSV."
        )
