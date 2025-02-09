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


class Main:
    def __init__(self):
        # Instanciation de vos managers
        self.csv_manager = CSVManager()
        self.pdf_manager = PDFManager(csv_manager=self.csv_manager)
        self.devis_manager = DevisManager(csv_manager=self.csv_manager)
        self.client_manager = ClientManager(csv_manager=self.csv_manager)
        self.histogramme_manager = HistogrammeManager(csv_manager=self.csv_manager)

        # Les champs et contrôles seront initialisés dans self.main(...)
        self.page = None

        # Champs pour la vue Clients
        self.client_nom = None
        self.client_adresse = None
        self.client_code_postal = None
        self.client_telephone = None
        self.client_entreprise = None
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
        self.devis_form_container = None

        # Conteneur principal pour alterner entre Clients et Devis
        self.content_container = None

        # Vues
        self.login_view = None
        self.auth_view = None
        self.main_view = None

        # Éléments d'authentification
        self.username_field = None
        self.password_field = None

        # Boutons de modification/suppression (admin)
        self.modify_button = None
        self.delete_button = None

        # Pour savoir si on est admin ou pas (optionnel)
        self.is_admin = False

    # ----------------------------------------------------------------
    # Méthodes de rappel (event handlers)
    # ----------------------------------------------------------------

    def on_ajouter_client(self, e):
        """Gère l'ajout d'un client."""
        try:
            self.client_manager.add_client(
                self.client_nom.value,
                self.client_adresse.value,
                self.client_code_postal.value,
                self.client_telephone.value,
                self.client_entreprise.value,
            )
            self.client_message.value = "Client ajouté avec succès !"

            # Mise à jour du champ Nom Client dans la vue Devis
            self.devis_nom_client.value = self.client_nom.value

            # Réinitialisation des champs
            self.client_nom.value = ""
            self.client_adresse.value = ""
            self.client_code_postal.value = ""
            self.client_telephone.value = ""
            self.client_entreprise.value = ""

            # Notification via SnackBar
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

        clients = self.csv_manager.read_csv(FICHIER_CLIENTS)
        found = None
        for client in clients:
            if client["Nom"].strip().upper() == nom.upper():
                found = client
                break

        if found:
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
                    "Le client n'est pas encore enregistré. "
                    "Veuillez l'enregistrer au préalable."
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

            devis_data = self.devis_manager.ajouter_devis(
                self.devis_nom_client.value, metal, quantite_ml, forme, remise
            )

            pdf_file = self.pdf_manager.generer_pdf(devis_data)
            self.devis_message.value = (
                "Devis ajouté avec succès !\n"
                f"Prix Total: {devis_data['Prix Total']:.2f} €\n"
                f"PDF généré: {pdf_file}"
            )

            self.page.snack_bar = ft.SnackBar(ft.Text("Devis ajouté et PDF généré."))
            self.page.snack_bar.open = True
            self.page.update()

        except Exception as ex:
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

    def on_reset_devis(self, e):
        """Réinitialise les champs de saisie pour la création de devis."""
        self.metal_dropdown.value = list(METAL_PROPERTIES.keys())[0]
        self.devis_quantite.value = ""
        self.forme_dropdown.value = "Droite"
        self.devis_remise.value = ""
        self.devis_message.value = ""
        self.page.update()

    def on_modifier_client(self, e):
        """Gère la modification d'un client (ADMIN)."""
        self.page.snack_bar = ft.SnackBar(
            ft.Text("Fonction de modification de client à implémenter")
        )
        self.page.snack_bar.open = True
        self.page.update()

    def on_supprimer_client(self, e):
        """Gère la suppression d'un client (ADMIN)."""
        self.page.snack_bar = ft.SnackBar(
            ft.Text("Fonction de suppression de client à implémenter")
        )
        self.page.snack_bar.open = True
        self.page.update()

    def on_login_admin(self, e):
        """Redirige vers la vue d'authentification."""
        self.switch_view("auth")

    def validate_auth(self, e):
        """
        Valide les identifiants.
        - Si vides => utilisateur simple => vue main
        - Si admin/password => admin => vue main + bouton suppr visible
        - Sinon => erreur
        """
        user = self.username_field.value
        pwd = self.password_field.value

        if user == "" and pwd == "":
            # Utilisateur standard
            self.is_admin = False
            self.switch_view("main")
            print("Après login user normal, is_admin =", self.is_admin)
        elif user == "1" and pwd == "1":
            # Admin
            self.is_admin = True
            self.switch_view("main")
            print("Après login admin, is_admin =", self.is_admin)  # <-- ICI
            # self.modify_button.visible = True  # si besoin
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
        """Vue de bienvenue (login)."""
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
        """Vue d'authentification (saisie identifiants)."""
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
        """Vue pour la gestion des clients."""
        self.client_nom = ft.TextField(label="Nom *", width=300)
        self.client_adresse = ft.TextField(label="Adresse *", width=300)
        self.client_code_postal = ft.TextField(label="Code Postal *", width=300)
        self.client_telephone = ft.TextField(label="Téléphone *", width=300)
        self.client_entreprise = ft.TextField(label="Entreprise", width=300)
        self.client_message = ft.Text()

        self.modify_button = ft.ElevatedButton(
            "Modifier Client", on_click=self.on_modifier_client, visible=False
        )
        self.delete_button = ft.ElevatedButton(
            "Supprimer Client", on_click=self.on_supprimer_client, visible=False
        )
        return ft.Column(
            [
                ft.Text("Gestion des Clients", size=20),
                ft.Text("Ajouter un nouveau client", size=16),
                (
                    ft.Text("Modifier Client", size=16)
                    if self.is_admin
                    else ft.Container()
                ),  # si admin
                (
                    ft.Text("Supprimer Client", size=16)
                    if self.is_admin
                    else ft.Container()
                ),  # si admin
                ft.Text("Les champs marqués d'une * sont obligatoires", color="red"),
                self.client_nom,
                self.client_adresse,
                self.client_code_postal,
                self.client_telephone,
                self.client_entreprise,
                ft.ElevatedButton("Ajouter Client", on_click=self.on_ajouter_client),
                self.client_message,
                self.modify_button,
                self.delete_button,
            ],
            spacing=10,
            alignment="center",
            horizontal_alignment="center",
        )

    def _build_devis_view(self) -> ft.Column:
        """Vue pour la gestion des devis."""
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
            alignment="start",
            horizontal_alignment="start",
        )

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
                ft.ElevatedButton("Reset", on_click=self.on_reset_devis),
                self.devis_message,
            ],
            spacing=10,
            alignment="start",
            horizontal_alignment="start",
        )

        self.devis_form_container = ft.Container(
            content=devis_characteristics, visible=False
        )
        left_side = ft.Column(
            [
                client_search_container,
                self.devis_form_container,
            ],
            spacing=20,
            alignment="start",
            horizontal_alignment="start",
        )

        self.histogram_image = ft.Image(src="", width=400, visible=False)
        right_side = ft.Column(
            [self.histogram_image],
            alignment="center",
            horizontal_alignment="center",
        )

        main_content = ft.Row(
            [left_side, right_side],
            spacing=20,
            alignment="center",
            expand=True,
        )

        return ft.Column(
            [
                ft.Text("Gestion des Devis", size=20),
                main_content,
            ],
            spacing=20,
            alignment="center",
            horizontal_alignment="center",
        )

    # 1) Construire le header (barre de navigation)
    def _build_header(self) -> ft.Row:
        """
        Header avec:
          - Bouton Clients
          - Bouton Devis
          - Bouton Logout => retour à la vue auth
        """
        return ft.Row(
            [
                ft.ElevatedButton(
                    "Gestion Clients", on_click=lambda e: self.switch_tab("clients")
                ),
                ft.ElevatedButton(
                    "Gestion Devis", on_click=lambda e: self.switch_tab("devis")
                ),
                ft.ElevatedButton(
                    "Logout", on_click=lambda e: self.switch_view("auth")
                ),
            ],
            alignment="center",
            spacing=20,
        )

    def _build_main_view(self) -> ft.Column:
        """Vue principale (avec onglets Clients / Devis)."""
        self.content_container = ft.Container(content=self._build_client_view())

        # 2) On place le header tout en haut
        header = self._build_header()

        return ft.Column(
            [
                header,  # Ajout du header
                self.content_container,  # Zone où on bascule Clients / Devis
            ],
            spacing=20,
            alignment="center",
            horizontal_alignment="center",
            visible=False,  # sera affiché après switch_view("main")
        )

    # ----------------------------------------------------------------
    # Méthodes pour changer de vue ou d'onglet
    # ----------------------------------------------------------------

    def switch_tab(self, tab: str):
        """Bascule entre la gestion des Clients et la gestion des Devis."""
        if tab == "clients":
            self.content_container.content = self._build_client_view()
        else:
            self.content_container.content = self._build_devis_view()
        self.page.update()

    def switch_view(self, view_name: str):
        """Change la vue visible: login, auth, main."""
        self.login_view.visible = view_name == "login"
        self.auth_view.visible = view_name == "auth"
        self.main_view.visible = view_name == "main"

        if view_name == "main":
            self.content_container.content = (
                self._build_client_view()
            )  # Reconstruire la vue des clients

        self.page.update()

    # ----------------------------------------------------------------
    # Méthode main (point d'entrée Flet)
    # ----------------------------------------------------------------

    def main(self, page: ft.Page):
        """Point d'entrée de l'application."""
        self.page = page
        page.title = "CutSharp - Gestion des Clients et Devis"

        # Dimension fenêtre
        page.window_width = 1280
        page.window_height = 720

        # Construit les différentes vues
        self.login_view = self._build_login_view()
        self.auth_view = self._build_auth_view()
        self.main_view = self._build_main_view()

        # On met les trois vues dans un conteneur
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
            bgcolor=ft.colors.with_opacity(0.5, "#deeeed"),
        )

        page.add(content_container)

        # Vue login par défaut
        self.switch_view("login")


# Lance l'app Flet
if __name__ == "__main__":
    main_object = Main()
    ft.app(target=main_object.main)
