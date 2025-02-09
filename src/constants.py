# =======================
# Constantes et données
# =======================

TVA = 0.2
TARIF_MACHINE = 0.3
TARIF_OPERATEUR = 45
FRAIS_FIXES = 7


# =======================
# Propriétés pour le calcul
# =======================
# Propriétés associées à chaque métal
METAL_PROPERTIES = {
    "Acier": {"coef": 1, "usure": 10, "vitesse": 200, "cout_materiaux": 20},
    "Alluminium": {"coef": 1.2, "usure": 5, "vitesse": 800, "cout_materiaux": 15},
    "Inox": {"coef": 1.5, "usure": 10, "vitesse": 140, "cout_materiaux": 30},
    "Titane": {"coef": 2, "usure": 20, "vitesse": 100, "cout_materiaux": 130},
    "Fonte": {"coef": 1.3, "usure": 20, "vitesse": 200, "cout_materiaux": 20},
    "Cuivre": {"coef": 1.4, "usure": 10, "vitesse": 350, "cout_materiaux": 60},
}

# Coefficient en fonction de la forme de découpe
FORME_COEFFICIENT = {
    "Droite": 1,
    "Ronde": 1.2,
    "Personnalisée": 1.3,
}

# =======================
# Fonctions utilitaires CSV / PDF
# =======================
FICHIER_CLIENTS = "datas/inputs_csv/clients.csv"
FICHIER_DEVIS = "datas/inputs_csv/devis.csv"
