# =======================
# Constantes et données
# =======================

TVA = 0.2
COUT_ADMIN = 7  # € par devis
COUT_TRANSPORT = 0.5  # € par pièce
AUTRES_COUTS = 0.03  # € par pièce
COUT_MACHINE = 0.3  # €/heure
COUT_OPERATEUR = 45  # €/heure

DONNEES_MATERIAUX = {
    "Fonte": {"Lame": "Diamanté", "Vitesse": 200, "Prix": 0.15},
    "Acier": {"Lame": "Carbure", "Vitesse": 200, "Prix": 0.05},
    "Cuivre": {"Lame": "Carbure", "Vitesse": 350, "Prix": 0.05},
    "Inox": {"Lame": "Carbure", "Vitesse": 140, "Prix": 0.05},
    "Titane": {"Lame": "Carbure revêtue TiN", "Vitesse": 100, "Prix": 0.10},
    "Aluminium": {"Lame": "TCT", "Vitesse": 800, "Prix": 0.05},
}

FICHIER_CLIENTS = "clients.csv"
FICHIER_DEVIS = "devis.csv"
