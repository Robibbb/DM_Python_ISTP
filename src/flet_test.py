from pathlib import Path
import flet as ft
from constants import (
    METAL_PROPERTIES,
    FORME_COEFFICIENT,
    FICHIER_CLIENTS,
)
from csv_manager import CSVManager
from pdf_manager import PDFManager
from devis_manager import DevisManager
from client_manager import ClientManager
from histogramme_manager import HistogrammeManager

# --- Chemin et import d'image ---
output_Path = Path(__file__).parent


def importimage(path: str) -> Path:
    filepath = output_Path / Path(path)
    return filepath


# ---- Main.py ----


class Main:
    def __init__(self):
        # Instanciation de vos managers
        self.csv_manager = CSVManager()
        self.pdf_manager = PDFManager(csv_manager=self.csv_manager)
        self.devis_manager = DevisManager(csv_manager=self.csv_manager)
        self.client_manager = ClientManager(csv_manager=self.csv_manager)
        self.histogramme_manager = HistogrammeManager(csv_manager=self.csv_manager)

        # Les champs et contrôles seront initialisés dans self.main(...)
        # afin d'être accessibles dans les méthodes de rappel (event handlers).
        self.page = None

        # Champs pour la vue Clients
        self.client_nom = None
        self.client_adresse = None
        self.client_code_postal = None
        self.client_telephone = None
        self.client_message = None

        # Champs pour la vue Devis
        self.devis_nom_client = None
        self.devis_detail_client = None
        self.metal_dropdown = None
        self.devis_quantite = None
        self.forme_dropdown = None
        self.devis_remise = None
        self.devis_message = None
        self.histogram_image = None

        # Conteneur principal pour alterner entre Clients et Devis
        self.content_container = None

        # Vues
        self.login_view = None
        self.auth_view = None
        self.main_view = None

        # Éléments d'authentification
        self.username_field = None
        self.password_field = None

    def on_ajouter_client(self, e):
        """Gère l'ajout d'un client."""
        try:
            self.client_manager.add_client(
                self.client_nom.value,
                self.client_adresse.value,
                self.client_code_postal.value,
                self.client_telephone.value,
            )
            self.client_message.value = "Client ajouté avec succès !"

            # Mise à jour du champ Nom Client dans la vue Devis
            self.devis_nom_client.value = self.client_nom.value

            # Réinitialisation des champs
            self.client_nom.value = ""
            self.client_adresse.value = ""
            self.client_code_postal.value = ""
            self.client_telephone.value = ""
            self.page.snack_bar = ft.SnackBar(ft.Text("Client ajouté avec succès !"))
            self.page.snack_bar.open = True
            self.page.update()

        except Exception as ex:
            self.page.snack_bar = ft.SnackBar(ft.Text(f"Erreur: {ex}"))
            self.page.snack_bar.open = True
            self.page.update()

    def on_rechercher_client(self, e):
        """Recherche un client à partir de son nom."""
        nom = self.devis_nom_client.value.strip()
        if not nom:
            self.page.snack_bar = ft.SnackBar(
                ft.Text("Veuillez entrer un nom de client.")
            )
            self.page.snack_bar.open = True
            self.page.update()
            return

        # Lecture du CSV via CSVManager
        clients = self.csv_manager.read_csv(FICHIER_CLIENTS)
        found = None
        for client in clients:
            if client["Nom"].strip().upper() == nom.upper():
                found = client
                break

        if found:
            # Affiche les détails du client et rend la saisie du devis visible
            self.devis_detail_client.value = (
                f"Adresse: {found['Adresse']}\n"
                f"Code Postal: {found['Code Postal']}\n"
                f"Téléphone: {found['Téléphone']}"
            )
            self.devis_form_container.visible = True
        else:
            self.devis_detail_client.value = ""
            self.devis_form_container.visible = False
            self.page.snack_bar = ft.SnackBar(
                ft.Text(
                    "Le client n'est pas encore enregistré. Veuillez l'enregistrer au préalable."
                )
            )
            self.page.snack_bar.open = True
        self.page.update()

    def on_ajouter_devis(self, e):
        """Gère l'ajout d'un devis et la génération du PDF."""
        try:
            metal = self.metal_dropdown.value
            quantite_ml = float(self.devis_quantite.value)
            forme = self.forme_dropdown.value
            remise = float(self.devis_remise.value)

            # Appel de la méthode en fixant la marge à 50 % (si c'est prévu ainsi)
            devis_data = self.devis_manager.ajouter_devis(
                self.devis_nom_client.value, metal, quantite_ml, forme, remise
            )

            pdf_file = self.pdf_manager.generer_pdf(devis_data)
            self.devis_message.value = (
                "Devis ajouté avec succès !\n"
                f"Prix Total: {devis_data['Prix Total']:.2f} €\n"
                f"PDF généré: {pdf_file}"
            )

            # Configuration et affichage de la SnackBar
            self.page.snack_bar = ft.SnackBar(ft.Text("Devis ajouté et PDF généré."))
            self.page.snack_bar.open = True
            self.page.update()

        except Exception as ex:
            # Afficher une SnackBar pour l'erreur
            self.page.snack_bar = ft.SnackBar(ft.Text(f"Erreur: {ex}"))
            self.page.snack_bar.open = True
            self.page.update()

    def on_generer_histogramme(self, e):
        """Génère l'histogramme depuis les données du CSV."""
        image_path = self.histogramme_manager.generer_histogramme_image()
        if image_path:
            self.histogram_image.src = image_path
            self.histogram_image.visible = True
            self.page.update()
        else:
            self.page.snack_bar = ft.SnackBar(
                ft.Text("Aucun devis trouvé ou format CSV incorrect.")
            )
            self.page.snack_bar.open = True
            self.page.update()

    def switch_tab(self, tab: str):
        """Permet de basculer entre la gestion des Clients et la gestion des Devis."""
        if tab == "clients":
            self.content_container.content = self._build_client_view()
        else:
            self.content_container.content = self._build_devis_view()
        self.page.update()

    def switch_view(self, view_name: str):
        """Permet de changer de vue (login, auth, main)."""
        self.login_view.visible = view_name == "login"
        self.auth_view.visible = view_name == "auth"
        self.main_view.visible = view_name == "main"
        self.page.update()

    def validate_auth(self, e):
        """Valide les identifiants de connexion."""
        if self.username_field.value == "" and self.password_field.value == "":
            self.switch_view("main")
        else:
            self.page.snack_bar = ft.SnackBar(
                ft.Text("Nom d'utilisateur ou mot de passe incorrect")
            )
            self.page.snack_bar.open = True
            self.page.update()

    # ----------------------------------------------------------------
    # Méthodes de construction des vues / UI
    # ----------------------------------------------------------------

    def _build_login_view(self) -> ft.Column:
        """Construit la vue de bienvenue (login)."""
        login_button = ft.ElevatedButton(
            text="Se connecter",
            on_click=lambda e: self.switch_view("auth"),
        )
        return ft.Column(
            [
                ft.Text("Bienvenue sur CutSharp", size=24),
                login_button,
            ],
            alignment="center",
            horizontal_alignment="center",
            spacing=10,
        )

    def _build_auth_view(self) -> ft.Column:
        """Construit la vue d'authentification (saisie identifiants)."""
        self.username_field = ft.TextField(label="Nom d'utilisateur", width=300)
        self.password_field = ft.TextField(
            label="Mot de passe", password=True, can_reveal_password=True, width=300
        )
        auth_button = ft.ElevatedButton("Se connecter", on_click=self.validate_auth)

        return ft.Column(
            [
                ft.Text("Veuillez vous authentifier", size=20),
                self.username_field,
                self.password_field,
                auth_button,
            ],
            alignment="center",
            horizontal_alignment="center",
            spacing=10,
        )

    def _build_client_view(self) -> ft.Column:
        """Construit la vue pour la gestion des clients."""
        # On (ré)initialise les champs ici
        self.client_nom = ft.TextField(label="Nom", width=300)
        self.client_adresse = ft.TextField(label="Adresse", width=300)
        self.client_code_postal = ft.TextField(label="Code Postal", width=300)
        self.client_telephone = ft.TextField(label="Téléphone", width=300)
        self.client_message = ft.Text()

        return ft.Column(
            [
                ft.Text("Gestion des Clients", size=20),
                self.client_nom,
                self.client_adresse,
                self.client_code_postal,
                self.client_telephone,
                ft.ElevatedButton("Ajouter Client", on_click=self.on_ajouter_client),
                self.client_message,
            ],
            spacing=10,
            alignment="center",
            horizontal_alignment="center",
        )

    def _build_devis_view(self) -> ft.Column:
        """Construit la vue pour la gestion des devis."""
        # --- Partie recherche du client ---
        self.devis_nom_client = ft.TextField(label="Nom Client", width=300)
        self.devis_detail_client = ft.Text("", color="blue")

        client_search_container = ft.Column(
            [
                self.devis_nom_client,
                ft.ElevatedButton(
                    "Rechercher Client", on_click=self.on_rechercher_client
                ),
                self.devis_detail_client,
            ],
            spacing=10,
            alignment="center",
            horizontal_alignment="center",
        )

        # --- Partie création du devis ---
        self.metal_dropdown = ft.Dropdown(
            label="Métal",
            options=[
                ft.dropdown.Option(key=metal, text=metal)
                for metal in METAL_PROPERTIES.keys()
            ],
            value=list(METAL_PROPERTIES.keys())[0],
            width=300,
        )
        self.devis_quantite = ft.TextField(label="Quantité à découper (mm)", width=300)
        self.forme_dropdown = ft.Dropdown(
            label="Forme de découpe",
            options=[
                ft.dropdown.Option(key=forme, text=forme)
                for forme in FORME_COEFFICIENT.keys()
            ],
            value="Droite",
            width=300,
        )
        self.devis_remise = ft.TextField(label="Remise client (%)", width=300)
        self.devis_message = ft.Text()

        # L'image de l'histogramme sera initialement masquée
        self.histogram_image = ft.Image(src="", width=400, visible=False)

        # Colonne pour les caractéristiques de création du devis (à gauche)
        devis_characteristics = ft.Column(
            [
                self.metal_dropdown,
                self.devis_quantite,
                self.forme_dropdown,
                self.devis_remise,
                ft.ElevatedButton("Ajouter Devis", on_click=self.on_ajouter_devis),
                ft.ElevatedButton(
                    "Générer Histogramme", on_click=self.on_generer_histogramme
                ),
                self.devis_message,
            ],
            spacing=10,
            alignment="center",
            horizontal_alignment="center",
        )

        # Colonne pour l'histogramme (à droite)
        histogram_container = ft.Column(
            [
                self.histogram_image,
            ],
            alignment="center",
            horizontal_alignment="center",
        )

        # Row qui place côte à côte les caractéristiques et l'histogramme
        devis_form_container = ft.Row(
            [
                devis_characteristics,
                histogram_container,
            ],
            spacing=20,
            alignment="center",
        )
        # La saisie complète du devis (Row) reste masquée tant que le client n'est pas trouvé
        devis_form_container.visible = False
        # Gardez une référence pour pouvoir modifier sa visibilité depuis l'event handler
        self.devis_form_container = devis_form_container

        return ft.Column(
            [
                ft.Text("Gestion des Devis", size=20),
                client_search_container,
                devis_form_container,
            ],
            spacing=10,
            alignment="center",
            horizontal_alignment="center",
        )

    def _build_main_menu(self) -> ft.Row:
        """Construit le menu principal permettant de basculer entre Clients/Devis."""
        return ft.Row(
            [
                ft.ElevatedButton(
                    "Gestion des Clients", on_click=lambda e: self.switch_tab("clients")
                ),
                ft.ElevatedButton(
                    "Gestion des Devis", on_click=lambda e: self.switch_tab("devis")
                ),
            ],
            alignment="center",
            spacing=20,
        )

    def _build_main_view(self) -> ft.Column:
        """Construit la vue principale (avec les onglets Clients / Devis)."""
        # Conteneur qui affichera soit le client_view soit le devis_view
        self.content_container = ft.Container(content=self._build_client_view())

        main_menu = self._build_main_menu()

        return ft.Column(
            [
                main_menu,
                self.content_container,
            ],
            spacing=20,
            alignment="center",
            horizontal_alignment="center",
            visible=False,
        )

    # ----------------------------------------------------------------
    # Méthode main pour Flet
    # ----------------------------------------------------------------
    def main(self, page: ft.Page):
        """Point d'entrée de l'application Flet."""
        self.page = page
        page.title = "CutSharp - Gestion des Clients et Devis"

        # Définir la taille de la fenêtre en 16:9
        page.window_width = 1280
        page.window_height = 720

        # Construit les différentes vues
        self.login_view = self._build_login_view()
        self.auth_view = self._build_auth_view()
        self.main_view = self._build_main_view()
        ################################# Ajout de l'image de fond #################################
        # # Conteneur principal avec image de fond
        # background_image_path = (
        #     "assets/background.PNG"  # Remplacez par le chemin de votre image
        # )
        # background_image = ft.Image(
        #     src=background_image_path,
        #     fit="cover",
        #     width=page.window_width,
        #     height=page.window_height,
        # )

        # # Conteneur pour le contenu de l'application
        # content_container = ft.Container(
        #     content=ft.Column(
        #         [
        #             self.login_view,
        #             self.auth_view,
        #             self.main_view,
        #         ],
        #         alignment="center",
        #         horizontal_alignment="center",
        #         spacing=20,
        #     ),
        #     expand=True,
        # )

        # # Conteneur principal combinant l'image de fond et le contenu
        # main_container = ft.Stack(
        #     [
        #         background_image,
        #         content_container,
        #     ],
        #     expand=True,
        # )

        # # Ajout du conteneur principal sur la page
        # page.add(main_container)
        content_container = ft.Container(
            content=ft.Column(
                [
                    self.login_view,
                    self.auth_view,
                    self.main_view,
                ],
                alignment="center",
                horizontal_alignment="center",
                spacing=20,
            ),
            expand=True,
            bgcolor=ft.colors.with_opacity(0.5, "#deeeed"),  # background color
        )

        # Ajout du conteneur principal sur la page
        page.add(content_container)
        # Ajout des vues sur la page
        page.add(self.login_view, self.auth_view, self.main_view)

        # Affiche la vue de login par défaut
        self.switch_view("login")


# Instanciation de la classe et démarrage de l'application
if __name__ == "__main__":
    main_object = Main()
    ft.app(target=main_object.main)
