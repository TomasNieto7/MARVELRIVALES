from tkinter import messagebox
import customtkinter as ctk
from PIL import Image, ImageChops, ImageFont

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class Interfaz(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Marvel Rivales")
        self.after(1, self.wm_state, 'zoomed')  # Maximiza la ventana

        # Cargar imagen de fondo
        try:
            self.bg_image_raw = Image.open("fondo.jpeg").convert("RGBA")
            self.opacity_layer = Image.new("RGBA", self.bg_image_raw.size, (0, 0, 0, 20))
            self.bg_image_opacified = Image.blend(self.bg_image_raw, self.opacity_layer, alpha=0.5)
            self.bg_image = ctk.CTkImage(
                light_image=self.bg_image_opacified,
                dark_image=self.bg_image_opacified,
                size=(self.winfo_width(), self.winfo_height())
            )
            self.bg_label = ctk.CTkLabel(self, image=self.bg_image, text="")
            self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        except FileNotFoundError:
            print("Error: El archivo de imagen 'fondo.jpeg' no se encuentra.")

        # === Frame contenedor centrado verticalmente ===
        self.container = ctk.CTkFrame(self, fg_color="transparent")
        # ocupa todo el ancho, centrado verticalmente
        self.container.place(relx=0, rely=0.5, anchor="w", relwidth=1)

        # Campo de contraseña que toca los bordes
        self.inputPassword = ctk.CTkEntry(
            self.container,
            placeholder_text="PASSWORD",
            height=150,
            show="*",
            justify="center",
            fg_color="white",
            text_color="black",
            font=ctk.CTkFont(family="Bruno Ace", size=24)
        )
        self.inputPassword.pack(fill="x", expand=True, padx=0, pady=0)

        # Vincular evento de redimensionado
        self.bind("<Configure>", self.resize_bg)

    def resize_bg(self, event):
        """Redimensiona y opaca la imagen de fondo cuando la ventana cambia de tamaño."""
        if hasattr(self, 'bg_label') and hasattr(self, 'bg_image_raw'):
            new_size = (event.width, event.height)
            resized_img = self.bg_image_raw.resize(new_size, Image.Resampling.LANCZOS)
            opacity_layer = Image.new("RGBA", new_size, (0, 0, 0, 20))
            opacified_resized_img = Image.blend(resized_img, opacity_layer, alpha=0.5)
            self.bg_image.configure(size=new_size)
            self.bg_image._image = opacified_resized_img
            self.bg_label.configure(image=self.bg_image)


if __name__ == "__main__":
    app = Interfaz()
    app.mainloop()
