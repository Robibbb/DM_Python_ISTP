from csv_manager import CSVManager
from matplotlib import pyplot as plt
from constants import FICHIER_DEVIS
from datetime import datetime


class HistogrammeManager:
    def __init__(self, csv_manager: CSVManager):
        self.csv_manager = csv_manager

    def generer_histogramme_image(self):
        devis_list = self.csv_manager.read_csv(FICHIER_DEVIS)
        print("len(devis_list)", len(devis_list))
        try:
            montants = [
                float(devis["Prix Total"])
                for devis in devis_list
                if "Prix Total" in devis and devis["Prix Total"] not in (None, "")
            ]
        except KeyError:
            return None

        intervalles = ["0-1000", "1000-5000", "5000-10000", ">10000"]
        comptes = [
            sum(1 for montant in montants if 0 <= montant <= 1000),
            sum(1 for montant in montants if 1000 < montant <= 5000),
            sum(1 for montant in montants if 5000 < montant <= 10000),
            sum(1 for montant in montants if montant > 10000),
        ]
        plt.figure()
        plt.bar(intervalles, comptes)
        plt.title("Histogramme des devis par intervalle de prix")
        plt.xlabel("Intervalle de prix (€)")
        plt.ylabel("Nombre de devis")
        image_path = (
            f"datas/outputs_png/histogram{datetime.now().strftime("%Y%m%d%H%M%S")}.png"
        )
        plt.savefig(image_path)
        plt.close()
        return image_path
