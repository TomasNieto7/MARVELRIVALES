# -*- coding: utf-8 -*-
"""
Interfaz gráfica para explorar personajes de Marvel Rivals.

Esta aplicación permite a los usuarios buscar información sobre los personajes
jugables en Marvel Rivals, ver una lista completa, obtener datos de un personaje
aleatorio y exportar la información a un archivo PDF.
"""

# -----------------
# IMPORTACIONES
# -----------------
import os
import random
from io import BytesIO
from tkinter import messagebox, filedialog

# Importaciones de terceros (requieren instalación)
import customtkinter as ctk
import pygame
import requests
from PIL import Image

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import landscape, letter
    from reportlab.lib.utils import ImageReader
    from reportlab.pdfgen import canvas
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    print("ADVERTENCIA: La biblioteca 'reportlab' no está instalada. La exportación a PDF no funcionará.")


# -----------------
# CONSTANTES
# -----------------
# --- Apariencia y Tema ---
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# --- Colores ---
COLOR_PRIMARY = "#9f0000"
COLOR_PRIMARY_HOVER = "#7a0000"
COLOR_BACKGROUND = "#d9d9d9"
COLOR_TEXT_DARK = "black"
COLOR_TEXT_LIGHT = "white"

# --- Fuentes ---
FONT_IMPACT = "Impact"
FONT_BRUNO_ACE = "Bruno Ace"

# --- Archivos y Rutas ---
BACKGROUND_IMAGE_PATH = "fondo3.png"
MUSIC_FILE_PATH = "musica_fondo.mp3"
# Ruta de guardado predeterminada para los PDF
DEFAULT_EXPORT_PATH = os.path.join(
    os.path.expanduser("~"), "Documents", "MarvelRivalsExports"
)

# --- API ---
API_TOKEN = "91e2e541450bf6936653103a81dacd0e"
API_BASE_URL = f"https://www.superheroapi.com/api/{API_TOKEN}/search/"
REQUESTS_HEADERS = {'User-Agent': 'Mozilla/5.0'}

# --- Contraseña ---
APP_PASSWORD = "kronos"

# --- Roster de Personajes ---
MARVEL_RIVALS_ROSTER = [
    "Black Panther", "Doctor Strange", "Groot", "Hulk", "Iron Man", "Loki",
    "Luna Snow", "Magik", "Magneto", "Mantis", "Namor", "Peni Parker",
    "Punisher", "Rocket Raccoon", "Scarlet Witch", "Spider-Man",
    "Star-Lord", "Storm", "Thor", "Wolverine", "The Thing",
    "Captain America", "Black Widow", "Mr. Fantastic", "Human Torch",
    "Invisible Woman", "Psylocke", "Daredevil", "Moon Knight", "Jeff the landshark"
]


# -----------------
# CLASE PRINCIPAL DE LA APLICACIÓN
# -----------------
class MarvelRivalsApp(ctk.CTk):
    """Clase principal que encapsula toda la interfaz y lógica de la aplicación."""

    def __init__(self):
        """Inicializa la ventana principal y sus componentes."""
        super().__init__()
        self.title("Marvel Rivales")
        self.after(1, self.wm_state, 'zoomed')  # Maximiza la ventana al iniciar

        # --- Atributos de la instancia ---
        self.bg_image_raw = None
        self.bg_label = None
        self._current_bg_image = None
        self.password_entry = None
        self.search_entry = None

        # --- Frames (contenedores de vistas) ---
        self.password_frame = None
        self.menu_frame = None
        self.search_frame = None
        self.hero_info_frame = None
        self.hero_list_frame = None

        # --- Datos del héroe actual ---
        self.current_hero_data = None
        self.current_hero_image = None

        # --- Inicialización de componentes ---
        self._setup_music()
        self._setup_background()
        self._show_password_screen()

    # ---------------------------------------------
    # MÉTODOS DE CONFIGURACIÓN INICIAL (SETUP)
    # ---------------------------------------------

    def _setup_music(self):
        """Inicializa y reproduce la música de fondo."""
        try:
            pygame.init()
            pygame.mixer.init()
            pygame.mixer.music.load(MUSIC_FILE_PATH)
            pygame.mixer.music.set_volume(0.4)
            pygame.mixer.music.play(loops=-1)
        except Exception as e:
            print(f"Error al iniciar la música de fondo: {e}")

    def _setup_background(self):
        """Carga y configura la imagen de fondo de la aplicación."""
        try:
            self.bg_image_raw = Image.open(BACKGROUND_IMAGE_PATH).convert("RGBA")
        except FileNotFoundError:
            print(f"Error: No se encontró la imagen de fondo '{BACKGROUND_IMAGE_PATH}'.")
            self.configure(fg_color="gray20")
            return

        self.after(100, lambda: self._update_background(self.winfo_width(), self.winfo_height()))
        self.bind("<Configure>", self._on_resize_background)

    # ---------------------------------------------
    # MÉTODOS PARA MOSTRAR VISTAS (PANTALLAS)
    # ---------------------------------------------

    def _show_password_screen(self):
        """Muestra la pantalla inicial de ingreso de contraseña."""
        self._clear_main_area()
        self.password_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.password_frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=1)

        self.password_entry = ctk.CTkEntry(
            self.password_frame,
            placeholder_text="PASSWORD",
            height=150,
            justify="center",
            fg_color=COLOR_TEXT_LIGHT,
            text_color=COLOR_TEXT_DARK,
            font=ctk.CTkFont(family=FONT_IMPACT, size=64)
        )
        self.password_entry.pack(fill="x", expand=True, padx=100)
        self.password_entry.focus_set()
        self.password_entry.bind("<Return>", self._verify_password)
        self.password_entry.bind("<KeyRelease>", self._format_spaced_text)

    def _show_main_menu(self):
        """Muestra el menú principal con las opciones de la aplicación."""
        if hasattr(self, 'password_frame') and self.password_frame.winfo_exists():
            self.password_frame.destroy()
        self._clear_main_area()
        self._update_background(self.winfo_width(), self.winfo_height())

        self.menu_frame = ctk.CTkFrame(self, fg_color=COLOR_BACKGROUND, corner_radius=0)
        self.menu_frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=1, relheight=0.5)

        options_container = ctk.CTkFrame(self.menu_frame, fg_color="transparent")
        options_container.pack(expand=True)

        menu_options = [
            ("BUSCAR HÉROE", "icon1.png", "icon1hover.png", self._show_search_screen),
            ("HÉROES", "icon2.png", "icon2hover.png", self._show_hero_list_screen),
            ("ALEATORIO", "icon3.png", "icon3hover.png", self._search_random_hero)
        ]

        for text, icon_path, hover_icon_path, command in menu_options:
            self._create_menu_option(options_container, text, icon_path, hover_icon_path, command)

    def _show_search_screen(self):
        """Muestra la pantalla de búsqueda de héroes."""
        self._clear_main_area()
        self._update_background(self.winfo_width(), self.winfo_height())
        self.search_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.search_frame.place(relx=0, rely=0, relwidth=1, relheight=1)

        gray_bar = ctk.CTkFrame(self.search_frame, fg_color=COLOR_BACKGROUND, corner_radius=0)
        gray_bar.place(relx=0.5, rely=0.5, anchor="center", relwidth=1, relheight=0.2)

        search_container = ctk.CTkFrame(gray_bar, fg_color="transparent")
        search_container.pack(expand=True)

        ctk.CTkLabel(
            search_container, text="BUSCAR:", font=ctk.CTkFont(family=FONT_IMPACT, size=32),
            fg_color=COLOR_PRIMARY, text_color=COLOR_TEXT_LIGHT, height=60, width=180
        ).pack(side="left")

        self.search_entry = ctk.CTkEntry(
            search_container, placeholder_text="", height=60, width=500,
            fg_color=COLOR_TEXT_LIGHT, text_color=COLOR_TEXT_DARK,
            font=ctk.CTkFont(family=FONT_IMPACT, size=28), border_width=0, corner_radius=0
        )
        self.search_entry.pack(side="left")
        self.search_entry.bind("<Return>", self._execute_search)
        self.search_entry.focus_set()

        self._create_back_button(self.search_frame, self._show_main_menu)

    def _show_hero_list_screen(self):
        """Muestra la lista completa de héroes jugables."""
        self._clear_main_area()
        self.hero_list_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.hero_list_frame.place(relx=0, rely=0, relwidth=1, relheight=1)

        main_container = ctk.CTkFrame(self.hero_list_frame, fg_color=COLOR_BACKGROUND)
        main_container.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.5, relheight=0.8)

        ctk.CTkLabel(main_container, text="PERSONAJES DE MARVEL RIVALS",
                     font=ctk.CTkFont(family=FONT_IMPACT, size=32),
                     text_color=COLOR_TEXT_DARK).pack(pady=20)

        scroll_frame = ctk.CTkScrollableFrame(main_container, fg_color="transparent", border_width=0)
        scroll_frame.pack(expand=True, fill="both", padx=20, pady=10)

        for hero_name in sorted(MARVEL_RIVALS_ROSTER):
            label_font = ctk.CTkFont(family=FONT_IMPACT, size=24)
            hero_label = ctk.CTkLabel(scroll_frame, text=hero_name.upper(),
                                      font=label_font, text_color=COLOR_TEXT_DARK, anchor="w")
            hero_label.pack(fill="x", padx=40, pady=8)
            hero_label.bind(
                "<Button-1>",
                lambda e,
                name=hero_name: self._fetch_hero_data(name))
            hero_label.bind(
                "<Enter>",
                lambda e,
                lbl=hero_label: lbl.configure(text_color=COLOR_PRIMARY,cursor="hand2"))
            hero_label.bind("<Leave>", lambda e, lbl=hero_label: lbl.configure(text_color=COLOR_TEXT_DARK, cursor=""))

        self._create_back_button(self.hero_list_frame, self._show_main_menu)

    def _display_hero_info(self, hero_data):
        """Muestra la información detallada de un héroe específico."""
        self._clear_main_area()
        self.current_hero_data = hero_data
        self.hero_info_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.hero_info_frame.place(relx=0, rely=0, relwidth=1, relheight=1)

        main_container = ctk.CTkFrame(
            self.hero_info_frame,
            fg_color=COLOR_BACKGROUND,
            corner_radius=0)
        main_container.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.8, relheight=0.7)

        self._create_hero_image_widget(main_container, hero_data)
        self._create_hero_info_widgets(main_container, hero_data)

        self._create_back_button(self.hero_info_frame, self._show_main_menu)

    # ---------------------------------------------
    # MÉTODOS DE LÓGICA Y MANEJO DE EVENTOS
    # ---------------------------------------------

    def _verify_password(self, event=None):
        """Verifica la contraseña ingresada y abre el menú si es correcta."""
        password = self.password_entry.get().replace(" ", "").lower()
        if password == APP_PASSWORD:
            self._show_main_menu()
        else:
            messagebox.showerror("Error", "Contraseña incorrecta")

    def _execute_search(self, event=None):
        """Realiza la búsqueda del héroe ingresado por el usuario."""
        hero_name = self.search_entry.get().strip()
        if not hero_name:
            messagebox.showwarning("Entrada Vacía", "Por favor, introduce el nombre de un héroe.")
            return

        roster_lower = [name.lower() for name in MARVEL_RIVALS_ROSTER]
        if hero_name.lower() not in roster_lower:
            messagebox.showerror("Héroe no Válido", f"'{hero_name}' no es un personaje jugable en Marvel Rivals.")
            return

        self._fetch_hero_data(hero_name)

    def _search_random_hero(self):
        """Selecciona un héroe aleatorio del roster y busca su información."""
        random_hero_name = random.choice(MARVEL_RIVALS_ROSTER)
        self._fetch_hero_data(random_hero_name)

    def _fetch_hero_data(self, hero_name):
        """Obtiene los datos de un héroe desde la Superhero API."""
        url = f"{API_BASE_URL}{hero_name}"
        try:
            response = requests.get(url, headers=REQUESTS_HEADERS, timeout=10)
            response.raise_for_status()
            data = response.json()

            if data.get("response") == "success":
                # Busca una coincidencia exacta del nombre para evitar resultados ambiguos
                exact_match = next(
                    (result for result in data["results"] if result['name'].lower() == hero_name.lower()),
                    None
                )
                self._display_hero_info(exact_match or data["results"][0])
            else:
                messagebox.showerror("Error de Búsqueda", f"No se encontró el héroe '{hero_name}'.")
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Error de Conexión", f"No se pudo conectar a la API: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error inesperado: {e}")

    def _export_to_pdf(self):
        """Exporta la información del héroe actual a un archivo PDF."""
        if not REPORTLAB_AVAILABLE:
            messagebox.showerror("Error", "La biblioteca 'reportlab' es necesaria para exportar a PDF.")
            return
        if not self.current_hero_data:
            messagebox.showerror("Error", "No hay información de héroe para exportar.")
            return

        filepath = self._get_save_filepath()
        if not filepath:
            return

        try:
            self._generate_pdf_content(filepath)
            messagebox.showinfo("Éxito", f"El archivo PDF se ha guardado en:\n{filepath}")
        except Exception as e:
            messagebox.showerror("Error de Exportación",
            f"No se pudo crear el archivo PDF.\nError: {e}")

    def _on_resize_background(self, event):
        """
        Manejador de evento para redimensionar 
        el fondo cuando la ventana cambia de tamaño."""
        if self.bg_image_raw and event.widget == self:
            self._update_background(event.width, event.height)

    # ---------------------------------------------
    # MÉTODOS AUXILIARES (HELPERS)
    # ---------------------------------------------

    def _clear_main_area(self):
        """Destruye todos los frames principales para limpiar la ventana."""
        for frame in [
            self.menu_frame,
            self.search_frame,
            self.hero_info_frame,
            self.hero_list_frame]:
            if frame and frame.winfo_exists():
                frame.destroy()
        self.menu_frame = self.search_frame = self.hero_info_frame = self.hero_list_frame = None

    def _update_background(self, width, height):
        """Redimensiona y aplica el efecto de opacidad a la imagen de fondo."""
        if not self.bg_image_raw:
            return
        try:
            new_size = (max(1, int(width)), max(1, int(height)))
            resized_img = self.bg_image_raw.resize(new_size, Image.Resampling.LANCZOS)
            opacity_layer = Image.new("RGBA", new_size, (0, 0, 0, 128))  # 50% de opacidad negra
            blended_img = Image.alpha_composite(resized_img, opacity_layer)
            new_ctk_image = ctk.CTkImage(light_image=blended_img, dark_image=blended_img, size=new_size)

            if hasattr(self, "bg_label") and self.bg_label.winfo_exists():
                self.bg_label.configure(image=new_ctk_image)
            else:
                self.bg_label = ctk.CTkLabel(self, image=new_ctk_image, text="")
                self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
            self.bg_label.lower()  # Mueve el label al fondo
            self._current_bg_image = new_ctk_image
        except Exception as e:
            print(f"Error al actualizar el fondo: {e}")

    @staticmethod
    def _clean_api_data(value, default="Desconocido"):
        """Limpia los datos de la API que son nulos o vacíos."""
        if not value or str(value).strip() in ("-", "null", "none"):
            return default
        return str(value)

    def _format_spaced_text(self, event):
        """Formatea el texto del entry de contraseña para que tenga espacios."""
        widget = event.widget
        current_text = widget.get()
        # Evita bucles si el último caracter ya es un espacio
        if len(current_text) > 1 and current_text.endswith(' '):
            return

        # Elimina los espacios existentes, añade espacios entre cada caracter y convierte a mayúsculas
        formatted_text = " ".join(list(current_text.replace(" ", ""))).upper()

        # Desvincula temporalmente para evitar recursión infinita
        widget.unbind("<KeyRelease>")
        widget.delete(0, "end")
        widget.insert(0, formatted_text)
        widget.bind("<KeyRelease>", self._format_spaced_text)

        # Mueve el cursor al final, excepto si se está borrando
        if event.keysym != 'BackSpace':
            widget.icursor("end")

    def _create_back_button(self, parent_frame, command):
        """Crea un botón 'VOLVER' estandarizado."""
        btn_volver = ctk.CTkButton(
            parent_frame, text="VOLVER", command=command,
            font=ctk.CTkFont(family=FONT_IMPACT, size=20),
            fg_color=COLOR_PRIMARY, hover_color=COLOR_PRIMARY_HOVER
        )
        btn_volver.place(relx=0.02, rely=0.03, anchor="nw")
        return btn_volver

    def _create_menu_option(self, parent, text, icon_path, hover_icon_path, command):
        """Crea un botón de opción para el menú principal."""
        option_frame = ctk.CTkFrame(parent, fg_color="transparent", width=320, height=80)
        option_frame.pack(pady=8)
        option_frame.pack_propagate(False)

        try:
            icon_img = ctk.CTkImage(Image.open(icon_path), size=(40, 40))
            icon_hover_img = ctk.CTkImage(Image.open(hover_icon_path), size=(40, 40))
        except FileNotFoundError:
            icon_img = icon_hover_img = None
            print(f"No se encontró {icon_path} o {hover_icon_path}")

        content_frame = ctk.CTkFrame(option_frame, fg_color="transparent")
        content_frame.pack(expand=True, fill="both")

        icon_label = ctk.CTkLabel(content_frame, image=icon_img, text="")
        icon_label.pack(side="left", padx=20)
        text_label = ctk.CTkLabel(content_frame, text=text,
                                  font=ctk.CTkFont(family=FONT_BRUNO_ACE, size=26),
                                  text_color=COLOR_TEXT_DARK, anchor="w")
        text_label.pack(side="left", padx=10, fill="x", expand=True)

        widgets_to_bind = [option_frame, content_frame, icon_label, text_label]

        def on_enter(e):
            option_frame.configure(fg_color="gray30")
            text_label.configure(text_color=COLOR_TEXT_LIGHT)
            if icon_hover_img:
                icon_label.configure(image=icon_hover_img)
        def on_leave(e):
            option_frame.configure(fg_color="transparent")
            text_label.configure(text_color=COLOR_TEXT_DARK)
            if icon_img:
                icon_label.configure(image=icon_img)

        for widget in widgets_to_bind:
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)
            widget.bind("<Button-1>", lambda e: command())

    def _create_hero_image_widget(self, parent, hero_data):
        """Crea y muestra el widget de la imagen del héroe."""
        try:
            image_url = hero_data.get("image", {}).get("url")
            if not image_url:
                raise ValueError("URL de imagen no encontrada en los datos de la API.")

            img_response = requests.get(image_url, headers=REQUESTS_HEADERS, timeout=10)
            img_response.raise_for_status()
            self.current_hero_image = Image.open(BytesIO(img_response.content))

            aspect_ratio = self.current_hero_image.width / self.current_hero_image.height
            new_height = 450
            new_width = int(new_height * aspect_ratio)

            hero_image_resized = self.current_hero_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            hero_ctk_image = ctk.CTkImage(
                light_image=hero_image_resized, dark_image=hero_image_resized, size=(new_width, new_height)
            )
            image_label = ctk.CTkLabel(parent, image=hero_ctk_image, text="")
            image_label.pack(side="left", padx=(80, 40), pady=40)

        except Exception as e:
            self.current_hero_image = None
            print(f"Error al cargar imagen del héroe: {e}")
            placeholder = ctk.CTkFrame(parent, fg_color="gray20", width=300, height=450)
            placeholder.pack(side="left", padx=(80, 40), pady=40)
            ctk.CTkLabel(placeholder, text="Imagen no disponible", text_color=COLOR_TEXT_LIGHT).pack(expand=True)

    def _create_hero_info_widgets(self, parent, hero_data):
        """Crea y muestra los widgets con la información textual del héroe."""
        info_container = ctk.CTkFrame(parent, fg_color="transparent")
        info_container.pack(side="left", expand=True, fill="both", padx=(20, 20), pady=40)

        text_wrapper = ctk.CTkFrame(info_container, fg_color="transparent")
        text_wrapper.place(relx=0.0, rely=0.5, anchor="w")

        # Nombre del Héroe
        hero_name = self._clean_api_data(hero_data.get("name"), "Desconocido").upper()
        ctk.CTkLabel(text_wrapper, text=hero_name,
                     font=ctk.CTkFont(family=FONT_IMPACT, size=72, weight="bold"),
                     text_color=COLOR_TEXT_DARK).pack(anchor="w", pady=(0, 40))

        # Lugar de Origen
        place_of_birth = self._clean_api_data(hero_data.get("biography", {}).get("place-of-birth"))
        ctk.CTkLabel(text_wrapper, text="LUGAR DE ORIGEN:",
                     font=ctk.CTkFont(family=FONT_IMPACT, size=24, weight="bold"),
                     text_color=COLOR_TEXT_DARK).pack(anchor="w")
        ctk.CTkLabel(text_wrapper, text=place_of_birth,
                     font=ctk.CTkFont(family=FONT_IMPACT, size=24, weight="bold"),
                     text_color=COLOR_PRIMARY).pack(anchor="w", pady=(0, 20))

        # Base de Operaciones
        base = self._clean_api_data(hero_data.get("work", {}).get("base"), default="Desconocida")
        ctk.CTkLabel(text_wrapper, text="BASE DE OPERACIONES",
                     font=ctk.CTkFont(family=FONT_IMPACT, size=24, weight="bold"),
                     text_color=COLOR_TEXT_DARK).pack(anchor="w")
        ctk.CTkLabel(text_wrapper, text=base,
                     font=ctk.CTkFont(family=FONT_IMPACT, size=24, weight="bold"),
                     text_color=COLOR_PRIMARY).pack(anchor="w")

        # Botón de exportación
        btn_export = ctk.CTkButton(
            info_container, text="Exportar a PDF", command=self._export_to_pdf, width=150, height=40,
            font=ctk.CTkFont(family=FONT_IMPACT, size=18), corner_radius=5,
            fg_color=COLOR_PRIMARY, hover_color=COLOR_PRIMARY_HOVER
        )
        btn_export.pack(side="bottom", anchor="se", pady=10, padx=10)

    def _get_save_filepath(self):
        """Abre un diálogo para que el usuario elija dónde guardar el PDF."""
        # Crea el directorio de exportación si no existe
        try:
            os.makedirs(DEFAULT_EXPORT_PATH, exist_ok=True)
        except OSError as e:
            messagebox.showerror("Error de Directorio", f"No se pudo crear la carpeta de destino.\nError: {e}")
            return None

        # Configura el nombre de archivo por defecto
        hero_name = self.current_hero_data.get('name', 'heroe').replace(' ', '_')
        default_filename = f"{hero_name}.pdf"

        # Abre el diálogo para guardar
        filepath = filedialog.asksaveasfilename(
            initialdir=DEFAULT_EXPORT_PATH,
            initialfile=default_filename,
            defaultextension=".pdf",
            filetypes=[("PDF Documents", "*.pdf")],
            title="Guardar Ficha de Héroe"
        )
        return filepath

    def _generate_pdf_content(self, filepath):
        """Crea el lienzo y dibuja el contenido del PDF."""
        pdf = canvas.Canvas(filepath, pagesize=landscape(letter))
        width, height = landscape(letter)

        # Fondo del PDF
        pdf.setFillColorRGB(217/255, 217/255, 217/255) # Mismo color que el fondo de la UI
        pdf.rect(0, 0, width, height, fill=1, stroke=0)

        # Dibuja la imagen del héroe
        img_width_on_pdf = self._draw_pdf_image(pdf, width, height)

        # Dibuja la información textual
        self._draw_pdf_text(pdf, width, height, img_width_on_pdf)

        pdf.save()

    def _draw_pdf_image(self, pdf, page_width, page_height):
        """Dibuja la imagen del héroe en el lienzo del PDF."""
        if not self.current_hero_image:
            return 0

        img_buffer = BytesIO()
        self.current_hero_image.convert("RGB").save(img_buffer, format='JPEG')
        img_buffer.seek(0)
        img_reader = ImageReader(img_buffer)

        img_aspect = self.current_hero_image.width / self.current_hero_image.height
        pdf_img_h = page_height * 0.7
        pdf_img_w = pdf_img_h * img_aspect
        pdf_img_x = page_width * 0.08
        pdf_img_y = (page_height - pdf_img_h) / 2

        pdf.drawImage(img_reader, pdf_img_x, pdf_img_y, width=pdf_img_w, height=pdf_img_h, mask='auto')
        return pdf_img_w

    def _draw_pdf_text(self, pdf, page_width, page_height, image_width):
        """Dibuja el texto informativo en el lienzo del PDF."""
        text_x_start = (page_width * 0.08) + image_width + 50
        text_center_x = text_x_start + (page_width - text_x_start) / 2.2
        text_y = page_height * 0.75

        # Nombre del Héroe
        hero_name = self._clean_api_data(self.current_hero_data.get("name"), "Desconocido").upper()
        pdf.setFont("Helvetica-Bold", 40)
        pdf.setFillColor(colors.black)
        pdf.drawCentredString(text_center_x, text_y, hero_name)
        text_y -= 80

        # Lugar de Origen
        pob = self._clean_api_data(self.current_hero_data.get("biography", {}).get("place-of-birth"))
        pdf.setFont("Helvetica", 18)
        pdf.setFillColor(colors.black)
        pdf.drawCentredString(text_center_x, text_y, "LUGAR DE ORIGEN:")
        text_y -= 30
        pdf.setFont("Helvetica-Bold", 18)
        pdf.setFillColor(colors.HexColor(COLOR_PRIMARY))
        pdf.drawCentredString(text_center_x, text_y, pob)
        text_y -= 60

        # Base de Operaciones
        base = self._clean_api_data(self.current_hero_data.get("work", {}).get("base"), "Desconocida")
        pdf.setFont("Helvetica", 18)
        pdf.setFillColor(colors.black)
        pdf.drawCentredString(text_center_x, text_y, "BASE DE OPERACIONES:")
        text_y -= 30
        pdf.setFont("Helvetica-Bold", 18)
        pdf.setFillColor(colors.HexColor(COLOR_PRIMARY))
        pdf.drawCentredString(text_center_x, text_y, base)

# -----------------
# PUNTO DE ENTRADA
# -----------------
if __name__ == "__main__":
    app = MarvelRivalsApp()
    app.mainloop()