""" Application de gestion de clients et devis pour CutSharp. """

from pathlib import Path
import os
import flet as ft

from client_manager import ClientManager
from constants import FICHIER_CLIENTS, FORME_COEFFICIENT, METAL_PROPERTIES
from csv_manager import CSVManager
from devis_manager import DevisManager
from histogramme_manager import HistogrammeManager
from pdf_manager import PDFManager
from dotenv import load_dotenv

load_dotenv()
# --- Chemin et import d'image ---
output_Path = Path(__file__).parent


def importimage(path: str) -> Path:
    """Importe une image depuis le dossier 'images'."""
    filepath = output_Path / Path(path)
    return filepath


class Main:
    """Classe principale de l'application."""

    def __init__(self):
        """Initialisation de l'application."""
        # Instanciation de vos managers
        self.csv_manager = CSVManager()
        self.pdf_manager = PDFManager(csv_manager=self.csv_manager)
        self.devis_manager = DevisManager(csv_manager=self.csv_manager)
        self.client_manager = ClientManager(csv_manager=self.csv_manager)
        self.histogramme_manager = HistogrammeManager(csv_manager=self.csv_manager)

        # La page Flet
        self.page = None

        # Champs pour la vue Clients
        self.client_nom = None
        self.client_adresse = None
        self.client_code_postal = None
        self.client_telephone = None
        self.client_entreprise = None
        self.client_message = None

        # Pour mémoriser le client sélectionné (pour modification/suppression)
        self.selected_client_nom = None  # nous utilisons le nom comme identifiant

        # Pour la liste déroulante des clients (visible uniquement pour l'admin)
        self.client_dropdown = None

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

        # Boutons pour modification/suppression (admin)
        self.modify_button = None
        self.delete_button = None

        # Conteneur principal pour alterner entre Clients et Devis
        self.content_container = None

        # Vues
        self.login_view = None
        self.auth_view = None
        self.main_view = None

        # Éléments d'authentification
        self.username_field = None
        self.password_field = None

        # Pour savoir si on est admin ou pas (optionnel)
        self.is_admin = False
        self.ADMIN_LOGIN = os.getenv("ADMIN_LOGIN")
        self.ADMIN_PWD = os.getenv("ADMIN_PWD")

    # ----------------------------------------------------------------
    # MÉTHODES D'ACTION (event handlers)
    # ----------------------------------------------------------------

    def on_ajouter_client(self, e=None):
        """
        Handles the addition of a client.
        This method attempts to add a new client using the provided client details.
        If the client already exists, it sets an appropriate message. If the client
        is added successfully, it clears the client form and updates the client
        dropdown if it exists.
        Args:
            e: The event object (not used in this method).
        Raises:
            Exception: If an error occurs during the client addition process, an
            error message is set with the exception details.
        """
        try:
            created_client = self.client_manager.add_client(
                self.client_nom.value,
                self.client_adresse.value,
                self.client_code_postal.value,
                self.client_telephone.value,
                self.client_entreprise.value,
            )
            if not created_client:
                self.client_message.value = (
                    "Le nom que vous avez indiqué est déjà utilisé"
                )
                self.client_message.color = "red"
            else:
                self.client_message.value = "Client ajouté avec succès !"
                self.clear_client_form()
            # Actualiser la liste déroulante si elle existe (mode admin)
            if self.client_dropdown:
                self.load_client_dropdown()
            self.page.update()

        except Exception as ex:
            self.client_message.value = f"Erreur: {ex}"
            self.page.update()

    def on_rechercher_client(self, e=None):
        """
        Recherche un client par nom.
        Si le client est trouvé dans clients.csv, affiche ses informations,
        rend visible le formulaire de devis et charge le Dropdown des devis.
        """
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
                f"Téléphone: {found['Téléphone']}\n"
                f"Entreprise: {found['Entreprise']}"
            )
            self.devis_detail_container.visible = True
            self.devis_form_container.visible = True
            # Rendre visible le Dropdown et charger les devis correspondants
            self.devis_dropdown.visible = True
            self.load_devis_dropdown(found["Nom"])
        else:
            self.devis_detail_container.visible = False
            self.devis_detail_client.value = ""
            self.devis_form_container.visible = False
            self.devis_dropdown.visible = False
            self.page.snack_bar = ft.SnackBar(
                ft.Text(
                    "Le client n'est pas encore enregistré. Veuillez l'enregistrer au préalable."
                )
            )
            self.page.snack_bar.open = True
        self.page.update()

    def on_ajouter_devis(self, e=None):
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

    def on_generer_histogramme(self, e=None):
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

    def on_reset_devis(self, e=None):
        """Réinitialise les champs de saisie pour la création de devis."""
        self.metal_dropdown.value = list(METAL_PROPERTIES.keys())[0]
        self.devis_quantite.value = ""
        self.forme_dropdown.value = "Droite"
        self.devis_remise.value = ""
        self.devis_message.value = ""
        self.page.update()

    # --- MÉTHODES POUR LA GESTION DES CLIENTS (ADMIN) ---
    def on_modifier_client(self, e=None):
        """Modifie le client sélectionné dans la liste déroulante."""
        if not self.selected_client_nom:
            self.page.snack_bar = ft.SnackBar(
                ft.Text("Veuillez sélectionner un client à modifier dans la liste.")
            )
            self.page.snack_bar.open = True
            self.page.update()
            return
        try:
            new_nom = self.client_nom.value
            new_adresse = self.client_adresse.value
            new_code_postal = self.client_code_postal.value
            new_telephone = self.client_telephone.value
            new_entreprise = self.client_entreprise.value

            # On délègue la modification au client_manager en passant l'ancien nom comme identifiant
            self.client_manager.modify_client(
                self.selected_client_nom,
                new_nom,
                new_adresse,
                new_code_postal,
                new_telephone,
                new_entreprise,
            )
            self.page.snack_bar = ft.SnackBar(ft.Text("Client modifié avec succès."))
            self.page.snack_bar.open = True
            self.clear_client_form()
            # Actualiser la liste déroulante
            if self.client_dropdown:
                self.load_client_dropdown()
        except Exception as ex:
            self.page.snack_bar = ft.SnackBar(
                ft.Text(f"Erreur lors de la modification: {ex}")
            )
            self.page.snack_bar.open = True
        self.page.update()

    def on_supprimer_client(self, e=None):
        """Supprime le client actuellement affiché dans le formulaire (mode admin)."""
        if not self.selected_client_nom:
            self.page.snack_bar = ft.SnackBar(
                ft.Text("Veuillez sélectionner un client à supprimer dans la liste.")
            )
            self.page.snack_bar.open = True
            self.page.update()
            return
        # Pour confirmation, vous pouvez également
        # afficher une AlertDialog (cf. votre version précédente)
        try:
            self.client_manager.delete_client(self.selected_client_nom)
            self.page.snack_bar = ft.SnackBar(ft.Text("Client supprimé avec succès."))
            self.page.snack_bar.open = True
            self.clear_client_form()
            if self.client_dropdown:
                self.load_client_dropdown()
        except Exception as ex:
            self.page.snack_bar = ft.SnackBar(
                ft.Text(f"Erreur lors de la suppression: {ex}")
            )
            self.page.snack_bar.open = True
        self.page.update()

    def load_devis_dropdown(self, client_name: str):
        """
        Charge dans le Dropdown tous les devis enregistrés pour le client indiqué,
        en filtrant le fichier devis.csv par le champ 'Nom Client'.
        Chaque option est formatée avec la date, le métal et le prix total.
        """
        devis_list = self.csv_manager.read_csv("datas/inputs_csv/devis.csv")
        # Filtrer les devis dont le nom client correspond (en ignorant la casse)
        devis_for_client = [
            devis
            for devis in devis_list
            if devis["Nom Client"].strip().upper() == client_name.strip().upper()
        ]
        options = []
        for i, devis in enumerate(devis_for_client):
            # Format d'affichage : Date - Métal - Prix Total €
            option_text = (
                f"{devis['Date']} - {devis['Matériau']} - {devis['Prix Total']} €"
            )
            options.append(ft.dropdown.Option(key=f"devis_{i}", text=option_text))
        self.devis_dropdown.options = options
        if options:
            self.devis_dropdown.value = options[0].key  # sélection par défaut
        else:
            self.devis_dropdown.value = None
        self.page.update()

    def on_devis_dropdown_changed(self, e=None):
        """
        Affiche les infos du devis sélectionné (Matériau, Quantité, Prix total)
        dans un conteneur à droite du formulaire.
        """
        # Si rien n'est sélectionné
        if not self.devis_dropdown.value:
            self.devis_info_container.visible = False
            self.page.update()
            return

        # Ex: "devis_0" => on récupère l'indice à droite de l'underscore
        selected_key = self.devis_dropdown.value  # ex: "devis_0"
        index_str = selected_key.split("_")[1]  # ex: "0"
        index = int(index_str)

        # Récupération de tous les devis du fichier CSV
        devis_list = self.csv_manager.read_csv("datas/inputs_csv/devis.csv")

        # Nom du client actuellement dans le champ "Nom Client"
        client_name = self.devis_nom_client.value.strip().upper()

        # Filtrer les devis du client actuellement recherché
        devis_for_client = [
            d for d in devis_list if d["Nom Client"].strip().upper() == client_name
        ]

        # Vérifier que l'index est valide
        if index < 0 or index >= len(devis_for_client):
            self.devis_info_container.visible = False
            self.page.update()
            return

        # Extraire le devis correspondant
        selected_devis = devis_for_client[index]

        # Récupérer les infos
        # (Adaptez les noms de colonnes selon ceux définis dans votre CSV)
        material = selected_devis.get("Matériau", "N/A")
        quantite = selected_devis.get(
            "Quantité (mm)", selected_devis.get("Quantité", "")
        )
        prix = selected_devis.get("Prix Total", "0")
        forme = selected_devis.get("Forme", "")

        # Composer le texte à afficher
        self.devis_info_text.value = (
            f"Matériau : {material}\n"
            f"Longueur : {quantite} mm\n"
            f"Forme : {forme}\n"
            f"Prix total : {prix} €"
        )

        # Rendre le conteneur visible
        self.devis_info_container.visible = True
        self.page.update()

    def clear_client_form(self, e=None):
        """Réinitialise le formulaire de saisie client."""
        self.client_nom.value = ""
        self.client_adresse.value = ""
        self.client_code_postal.value = ""
        self.client_telephone.value = ""
        self.client_entreprise.value = ""
        self.selected_client_nom = None
        self.page.update()

    def load_client_dropdown(self, e=None):
        """Charge les options du Dropdown à partir des données du CSV."""
        clients = self.csv_manager.read_csv(FICHIER_CLIENTS)
        options = [
            ft.dropdown.Option(key=client["Nom"], text=client["Nom"])
            for client in clients
        ]
        self.client_dropdown.options = options
        self.client_dropdown.value = None  # pas de sélection par défaut
        self.page.update()

    def on_client_dropdown_changed(self, e=None):
        """Lorsqu'un client est sélectionné dans la liste déroulante, remplir le formulaire."""
        selected_name = self.client_dropdown.value
        if not selected_name:
            return
        clients = self.csv_manager.read_csv(FICHIER_CLIENTS)
        for client in clients:
            if client["Nom"].strip() == selected_name.strip():
                self.client_nom.value = client["Nom"]
                self.client_adresse.value = client["Adresse"]
                self.client_code_postal.value = client["Code Postal"]
                self.client_telephone.value = client["Téléphone"]
                self.client_entreprise.value = client["Entreprise"]
                self.selected_client_nom = client["Nom"]
                break
        self.page.update()

    # ----------------------------------------------------------------
    # Méthodes d'authentification et de navigation
    # ----------------------------------------------------------------

    def on_login_admin(self, e=None):
        """Redirige vers la vue d'authentification."""
        self.switch_view("auth")

    def validate_auth(self, e=None):
        """
        Valide les identifiants.
        - Si vides => utilisateur simple => vue main
        - Si admin/password => admin => vue main avec boutons admin visibles
        - Sinon => erreur
        """
        user = self.username_field.value
        pwd = self.password_field.value

        if user == "" and pwd == "":
            self.is_admin = False
            self.switch_view("main")
        elif user == self.ADMIN_LOGIN and pwd == self.ADMIN_PWD:
            self.is_admin = True
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

    def _build_login_view(self, e=None) -> ft.Column:
        """Vue de bienvenue (login)."""
        login_button = ft.ElevatedButton(
            text="Se connecter",
            on_click=lambda e: self.switch_view("auth"),
        )
        return ft.Column(
            [
                ft.Container(
                    ft.Text("Bienvenue sur CutSharp", size=24),
                    alignment=ft.alignment.center,
                ),
                ft.Container(
                    login_button,
                    alignment=ft.alignment.center,
                ),
            ],
            alignment="center",
            spacing=10,
        )

    def _build_auth_view(self, e=None) -> ft.Column:
        """Vue d'authentification (saisie identifiants)."""
        self.username_field = ft.TextField(label="Nom d'utilisateur", width=300)
        self.password_field = ft.TextField(
            label="Mot de passe", password=True, can_reveal_password=True, width=300
        )
        auth_button = ft.ElevatedButton("Se connecter", on_click=self.validate_auth)

        return ft.Column(
            [
                ft.Container(
                    ft.Text("Veuillez vous authentifier", size=20),
                    alignment=ft.alignment.center,
                ),
                ft.Container(
                    self.username_field,
                    alignment=ft.alignment.center,
                ),
                ft.Container(
                    self.password_field,
                    alignment=ft.alignment.center,
                ),
                ft.Container(
                    auth_button,
                    alignment=ft.alignment.center,
                ),
            ],
            alignment="center",
            spacing=10,
        )

    def _build_client_view(self, e=None) -> ft.Stack:
        """Vue pour la gestion des clients avec positionnement absolu par top et left."""
        # --- Création des champs de saisie et messages ---
        self.client_nom = ft.TextField(label="Nom *", width=300)
        self.client_adresse = ft.TextField(label="Adresse *", width=300)
        self.client_code_postal = ft.TextField(label="Code Postal *", width=300)
        self.client_telephone = ft.TextField(label="Téléphone *", width=300)
        self.client_entreprise = ft.TextField(label="Entreprise", width=300)
        self.client_message = ft.Text()

        add_client_button = ft.ElevatedButton(
            "Ajouter Client", on_click=self.on_ajouter_client
        )

        # --- Boutons de modification/suppression (affichés en mode admin) ---
        admin_buttons = []
        if self.is_admin:
            self.modify_button = ft.ElevatedButton(
                "Modifier Client", on_click=self.on_modifier_client
            )
            self.delete_button = ft.ElevatedButton(
                "Supprimer Client", on_click=self.on_supprimer_client
            )
            admin_buttons = [self.modify_button, self.delete_button]

        # --- Construction du Stack avec positionnement absolu ---
        controls = [
            # Titres et messages
            ft.Container(
                content=ft.Text("Gestion des Clients", size=20),
                top=0,
                left=455,
                border=ft.border.all(2, ft.colors.RED),
                padding=10,
            ),
            ft.Container(
                content=ft.Text(
                    "Les champs marqués d'une * sont obligatoires", color="red"
                ),
                top=80,
                left=410,
            ),
            # Champs de saisie du formulaire
            ft.Container(content=self.client_nom, top=120, left=410),
            ft.Container(content=self.client_adresse, top=170, left=410),
            ft.Container(content=self.client_code_postal, top=220, left=410),
            ft.Container(content=self.client_telephone, top=270, left=410),
            ft.Container(content=self.client_entreprise, top=320, left=410),
            # Bouton d'ajout et message d'information
            ft.Container(content=add_client_button, top=370, left=410),
            ft.Container(content=self.client_message, top=420, left=410),
        ]

        # --- Positionnement des éléments admin avec top et left ---
        if self.is_admin:

            # Affichage "Interface administrateur" encadré en rouge
            controls.append(
                ft.Container(
                    content=ft.Text("Interface administrateur", size=20),
                    top=50,
                    left=50,
                    border=ft.border.all(2, ft.colors.RED),
                    padding=10,
                )
            )

            # Dropdown "Liste des Clients"
            self.client_dropdown = ft.Dropdown(
                label="Liste des Clients",
                width=300,
                on_change=self.on_client_dropdown_changed,
            )
            self.load_client_dropdown()
            controls.append(
                ft.Container(content=self.client_dropdown, top=180, left=50)
            )
            # Bouton "Modifier Client"
            controls.append(ft.Container(content=self.modify_button, top=140, left=50))
            # Bouton "Supprimer Client"
            controls.append(ft.Container(content=self.delete_button, top=140, left=170))

        # Le Stack définit la zone totale de la vue
        return ft.Stack(controls=controls, width=800, height=600)

    def _build_devis_view(self, e=None) -> ft.Stack:
        """
        Vue pour la gestion des devis, en positionnant certains éléments
        dans un Stack (top, left).
        - Bouton 'Générer Histogramme' retiré
        - Ajout d'un conteneur (self.devis_info_container) pour afficher les infos du devis sélectionné
        - Le titre "Gestion des Devis" est placé dans un conteneur positionné absolument et encadré en rouge.
        """

        # 1) Champs pour saisir/rechercher le client
        self.devis_nom_client = ft.TextField(label="Nom Client", width=300)
        rechercher_client_button = ft.ElevatedButton(
            "Rechercher Client", on_click=self.on_rechercher_client
        )

        # 2) Conteneur d'information sur le client
        self.devis_detail_client = ft.Text("", color="blue")
        self.devis_detail_container = ft.Container(
            content=self.devis_detail_client,
            border=ft.border.all(1, ft.colors.BLACK),
            border_radius=5,
            padding=10,
            visible=False,  # Rendu visible après la recherche du client
        )

        # 3) Container pour la recherche de client (nom + bouton + infos)
        client_search_container = ft.Column(
            [
                self.devis_nom_client,
                rechercher_client_button,
                self.devis_detail_container,
            ],
            spacing=10,
            alignment="start",
            horizontal_alignment="start",
        )

        # 4) Dropdown pour sélectionner un devis
        self.devis_dropdown = ft.Dropdown(
            label="Liste des devis",
            width=300,
            visible=False,  # Rendu visible dans on_rechercher_client
            on_change=self.on_devis_dropdown_changed,
        )

        # 5) Conteneur qui affichera les informations du devis sélectionné
        self.devis_info_text = ft.Text("")
        self.devis_info_container = ft.Container(
            content=self.devis_info_text,
            border=ft.border.all(1, ft.colors.BLACK),
            border_radius=5,
            padding=10,
            visible=False,  # Deviendra visible lorsque le dropdown change
        )

        # 6) Champs pour créer un devis
        self.metal_dropdown = ft.Dropdown(
            label="Métal",
            options=[
                ft.dropdown.Option(key=m, text=m) for m in METAL_PROPERTIES.keys()
            ],
            value=list(METAL_PROPERTIES.keys())[0],
            width=300,
        )
        self.devis_quantite = ft.TextField(label="Quantité à découper (mm)", width=300)
        self.forme_dropdown = ft.Dropdown(
            label="Forme de découpe",
            options=[
                ft.dropdown.Option(key=f, text=f) for f in FORME_COEFFICIENT.keys()
            ],
            value="Droite",
            width=300,
        )
        self.devis_remise = ft.TextField(label="Remise client (%)", width=300)
        self.devis_message = ft.Text("")

        # 7) Colonne regroupant les champs du formulaire (sans le bouton histogramme)
        devis_characteristics = ft.Column(
            [
                self.metal_dropdown,
                self.devis_quantite,
                self.forme_dropdown,
                self.devis_remise,
                ft.ElevatedButton("Ajouter Devis", on_click=self.on_ajouter_devis),
                ft.ElevatedButton("Reset", on_click=self.on_reset_devis),
                self.devis_message,
            ],
            spacing=10,
            alignment="start",
            horizontal_alignment="start",
        )

        # 8) Container du formulaire (caché tant que le client n'est pas trouvé)
        self.devis_form_container = ft.Container(
            content=devis_characteristics,
            visible=False,
        )

        # 9) Stack regroupant les différents éléments avec positionnement absolu
        inner_stack = ft.Stack(
            controls=[
                ft.Container(
                    content=client_search_container,
                    top=10,
                    left=40,
                ),
                ft.Container(
                    content=self.devis_form_container,
                    top=10,
                    left=380,
                ),
                ft.Container(
                    content=self.devis_dropdown,
                    top=10,
                    left=730,
                ),
                ft.Container(
                    content=self.devis_info_container,
                    top=70,
                    left=730,
                ),
            ],
            width=1200,
            height=900,
        )

        # 10) Titre "Gestion des Devis" dans un conteneur positionné absolument et encadré en rouge.
        title_container = ft.Container(
            content=ft.Text("Gestion des Devis", size=20),
            top=10,  # Modifiez cette valeur pour changer la position verticale du titre
            left=40,  # Modifiez cette valeur pour changer la position horizontale du titre
            border=ft.border.all(2, ft.colors.RED),
            padding=10,
        )

        # 11) Retourne un Stack principal qui contient le titre et le reste de l'interface,
        #      le inner_stack est positionné en dessous du titre.
        return ft.Stack(
            controls=[
                title_container,
                ft.Container(
                    content=inner_stack,
                    top=70,  # Décalage vertical pour placer le inner_stack sous le titre
                    left=0,
                ),
            ],
            width=1200,
            height=1000,
        )

    def _build_header(self) -> ft.Container:
        """
        Header avec :
        - Bouton Gestion Clients
        - Bouton Gestion Devis
        - Bouton Logout (retour à la vue auth)

        Le header est positionné à 20px du haut et 20px de la gauche.
        """
        header_row = ft.Row(
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
            spacing=20,
        )
        # Ici, le Container est placé dans un Stack, et on lui attribue top et left
        return ft.Container(
            content=header_row,
            top=20,
            left=400,
        )

    def _build_main_view(self, e=None) -> ft.Stack:
        """
        Vue principale (avec onglets Clients / Devis).

        On utilise un Stack pour positionner le header et le contenu :
        - Le header est positionné en haut à gauche.
        - Le conteneur principal est positionné sous le header.
        """
        self.content_container = ft.Container(
            content=self._build_client_view(),
            top=100,  # Ajustez cette valeur pour positionner le contenu sous le header
            left=20,
        )
        header = self._build_header()
        return ft.Stack(
            controls=[header, self.content_container],
            width=1280,
            height=720,
            visible=False,  # Sera affiché après switch_view("main")
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
            # Reconstruire la vue des clients (les boutons
            # admin et la liste déroulante s'afficheront si is_admin est True)
            self.content_container.content = self._build_client_view()

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
                [self.login_view, self.auth_view, self.main_view],
                alignment="center",
                horizontal_alignment="center",
                spacing=20,
            ),
            expand=True,
            bgcolor=ft.colors.with_opacity(0.5, "#89CFF0"),
        )

        page.add(content_container)

        # Vue login par défaut
        self.switch_view("login")


# Lance l'app Flet
if __name__ == "__main__":
    main_object = Main()
    ft.app(target=main_object.main)
