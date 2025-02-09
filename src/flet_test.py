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
        # afin d'être accessibles dans les méthodes de rappel (event handlers).
        self.page = None

        # Champs pour la vue Clients
        self.client_nom = None
        self.client_adresse = None
        self.client_code_postal = None
        self.client_telephone = None
        self.client_entreprise = None

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
        self.admin_view = None  # <-- Nouvelle vue pour l'admin

        # Pour la gestion d'un accès admin
        self.admin_username = None
        self.admin_password = None

        # Éléments d'authentification
        self.username_field = None
        self.password_field = None

        # Boutons de modification/suppression (admin)
        self.modify_button = None
        self.delete_button = None

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

            # Appel de la méthode en fixant la marge à 50 % (si c'est le choix)
            devis_data = self.devis_manager.ajouter_devis(
                self.devis_nom_client.value, metal, quantite_ml, forme, remise
            )

            pdf_file = self.pdf_manager.generer_pdf(devis_data)
            self.devis_message.value = (
                "Devis ajouté avec succès !\n"
                f"Prix Total: {devis_data['Prix Total']:.2f} €\n"
                f"PDF généré: {pdf_file}"
            )

            # Notification via SnackBar
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
        """
        Au lieu d'ouvrir uniquement une AlertDialog, on bascule ici
        vers la vue d'authentification pour l'admin.
        """
        self.switch_view("auth")

    def validate_auth(self, e):
        """
        Valide les identifiants de connexion.
        - Si vides => vue main
        - Si admin/password => vue admin
        - Sinon => erreur
        """
        user = self.username_field.value
        pwd = self.password_field.value

        if user == "" and pwd == "":
            # Utilisateur standard (vide dans cet exemple)
            self.switch_view("main")
        elif user == "1" and pwd == "1":
            # Identifiants Admin corrects
            self.switch_view("admin")  # On bascule sur la vue admin
        else:
            # Erreur d'authentification
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
            on_click=lambda e: self.switch_view("auth"),  # Vue d'authentification
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
        self.client_entreprise = ft.TextField(label="Entreprise", width=300)
        self.client_message = ft.Text()

        # Boutons pour modifier et supprimer des clients (visibles uniquement pour l'administrateur)
        # Par défaut, invisibles
        self.modify_button = ft.ElevatedButton(
            "Modifier Client", on_click=self.on_modifier_client, visible=False
        )
        self.delete_button = ft.ElevatedButton(
            "Supprimer Client", on_click=self.on_supprimer_client, visible=False
        )

        return ft.Column(
            [
                ft.Text("Gestion des Clients", size=20),
                self.client_nom,
                self.client_adresse,
                self.client_code_postal,
                self.client_telephone,
                self.client_entreprise,
                ft.ElevatedButton("Ajouter Client", on_click=self.on_ajouter_client),
                self.client_message,
                ft.ElevatedButton(
                    "Login Administrateur", on_click=self.on_login_admin
                ),  # Bouton Login Administrateur
                self.modify_button,
                self.delete_button,
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
                ft.ElevatedButton(
                    "Reset", on_click=self.on_reset_devis
                ),  # Bouton Reset
                self.devis_message,
            ],
            spacing=10,
            alignment="center",
            horizontal_alignment="center",
        )

        # Regrouper la recherche du client et le formulaire de devis dans une même colonne (côté gauche)
        # Le formulaire de devis reste masqué tant que le client n'est pas trouvé.
        self.devis_form_container = ft.Container(
            content=devis_characteristics, visible=False
        )
        left_side = ft.Column(
            [
                client_search_container,
                self.devis_form_container,
            ],
            spacing=20,
            alignment="center",
            horizontal_alignment="center",
        )

        # --- Partie Histogramme (affichée à droite) ---
        self.histogram_image = ft.Image(src="", width=400, visible=False)
        right_side = ft.Column(
            [self.histogram_image],
            alignment="center",
            horizontal_alignment="center",
        )

        # Disposition principale : deux colonnes côte à côte
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
        """
        Construit la vue principale (avec les onglets Clients / Devis).
        Par défaut, on commence par la vue clients.
        """
        # Conteneur qui affichera soit la client_view soit la devis_view
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
            visible=False,  # Masqué par défaut, jusqu'au switch_view("main")
        )

    def _build_admin_view(self) -> ft.Column:
        """
        Construit la vue dédiée à l'administrateur.
        Pour le moment, elle affiche seulement "ADMIN VIEW".
        """
        return ft.Column(
            [
                ft.Text("ADMIN VIEW", size=32, weight=ft.FontWeight.BOLD),
                ft.Text("Bienvenue dans la vue d'administration !"),
            ],
            alignment="center",
            horizontal_alignment="center",
            spacing=20,
            visible=False,  # On contrôle la visibilité via switch_view
        )

    # ----------------------------------------------------------------
    # Méthodes utilitaires pour changer de "vue" (login, auth, main, admin)
    # ----------------------------------------------------------------

    def switch_tab(self, tab: str):
        """Permet de basculer entre la gestion des Clients et la gestion des Devis."""
        if tab == "clients":
            self.content_container.content = self._build_client_view()
        else:
            self.content_container.content = self._build_devis_view()
        self.page.update()

    def switch_view(self, view_name: str):
        """
        Permet de changer de vue parmi:
          - "login"
          - "auth"
          - "main"
          - "admin"
        """
        self.login_view.visible = view_name == "login"
        self.auth_view.visible = view_name == "auth"
        self.main_view.visible = view_name == "main"
        self.admin_view.visible = view_name == "admin"
        self.page.update()

    # ----------------------------------------------------------------
    # Méthode main pour Flet (point d'entrée)
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
        self.admin_view = self._build_admin_view()  # Vue admin

        # On ajoute les quatre vues (login/auth/main/admin) dans un Container global
        content_container = ft.Container(
            content=ft.Column(
                [
                    self.login_view,
                    self.auth_view,
                    self.main_view,
                    self.admin_view,  # On l'ajoute aussi
                ],
                alignment="center",
                horizontal_alignment="center",
                spacing=20,
            ),
            expand=True,
            bgcolor=ft.colors.with_opacity(0.5, "#deeeed"),  # Couleur de fond
        )

        page.add(content_container)

        # Affiche la vue de login par défaut
        self.switch_view("login")


# Point d'entrée Flet
if __name__ == "__main__":
    main_object = Main()
    ft.app(target=main_object.main)
