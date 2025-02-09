from csv_manager import CSVManager
from constants import (
    METAL_PROPERTIES,
    TARIF_MACHINE,
    TARIF_OPERATEUR,
    FRAIS_FIXES,
    TVA,
    FORME_COEFFICIENT,
    FICHIER_DEVIS,
)
from datetime import datetime


class DevisManager:
    def __init__(self, csv_manager: CSVManager):
        self.csv_manager = csv_manager

    def calculer_devis(self, metal, quantite_ml, forme, remise_client):
        """
        Calcule le devis pour la découpe d'un métal donné en fonction de la quantité, de la forme et de la remise client.

        Args:
            metal (str): Le type de métal à découper.
            quantite_ml (float): La quantité de métal à découper en millimètres linéaires.
            forme (str): La forme de découpe.
            remise_client (float): La remise accordée au client en pourcentage.

        Returns:
            dict: Un dictionnaire contenant les coûts détaillés et le prix total avec TVA.
            - "Coût Matériaux" (float): Le coût des matériaux.
            - "Coût Découpe" (float): Le coût de la découpe.
            - "Frais Fixes" (float): Les frais fixes.
            - "Prix Total" (float): Le prix total incluant la TVA.

        Raises:
            ValueError: Si le métal ou la forme de découpe n'est pas valide.
        """
        # Marge fixe de 50 %
        marge = 50 / 100
        # Conversion de la remise client en décimal (entrée en %)
        remise_client = remise_client / 100

        # Constantes

        # Propriétés du métal sélectionné
        props = METAL_PROPERTIES.get(metal)
        if not props:
            raise ValueError("Métal non trouvé")
        coef_metal = props["coef"]
        usure_lame = props["usure"]
        vitesse = props["vitesse"]
        cout_materiaux_unit = props["cout_materiaux"]

        # Coefficient de la forme de découpe
        coef_forme = FORME_COEFFICIENT.get(forme)
        if coef_forme is None:
            raise ValueError("Forme de découpe non valide")

        # Calcul du temps de découpe (en heures)
        temps_decoupe = (quantite_ml / vitesse) / 60

        # Coût de découpe
        cout_decoupe = (
            temps_decoupe * (TARIF_MACHINE + TARIF_OPERATEUR + usure_lame) * coef_forme
        )

        # Coût des matériaux (conversion mm -> m)
        cout_materiaux = (quantite_ml / 1000) * cout_materiaux_unit * coef_metal

        base_cost = cout_materiaux + cout_decoupe + FRAIS_FIXES

        # Application de la marge fixe et de la remise client
        prix_general = base_cost + (base_cost * marge) - (base_cost * remise_client)
        prix_total = round(prix_general * (1 + TVA), 3)

        return {
            "Coût Matériaux": round(cout_materiaux, 3),
            "Coût Découpe": round(cout_decoupe, 3),
            "Frais Fixes": FRAIS_FIXES,
            "Prix Total": prix_total,
        }

    def ajouter_devis(
        self,
        nom_client: str,
        metal: str,
        quantite_ml: str,
        forme: str,
        remise_client: str,
    ) -> dict:

        devis = self.calculer_devis(metal, quantite_ml, forme, remise_client)
        donnees_devis = {
            "Nom Client": nom_client.upper(),
            "Métal": metal,
            "Quantité (mm)": quantite_ml,
            "Forme": forme,
            "Remise (%)": remise_client,  # valeur saisie par l'utilisateur (en %)
            "Prix Total": devis["Prix Total"],
            "Coût Matériaux": devis["Coût Matériaux"],
            "Coût Découpe": devis["Coût Découpe"],
            "Frais Fixes": devis["Frais Fixes"],
            "Date": datetime.now().strftime("%Y-%m-%d"),
        }
        self.csv_manager.ajouter_csv(FICHIER_DEVIS, donnees_devis)
        return donnees_devis
