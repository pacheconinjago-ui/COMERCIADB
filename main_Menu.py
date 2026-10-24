import customtkinter as ctk
from PIL import Image
from clientes_gui import FrameClientes
from inventario_gui import FrameInventario
from proveedores_gui import FrameProveedores
from gastos_gui import FrameGastos

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class MenuPrincipal(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("COMERCIADB - Panel Principal")
        self.geometry("1670x830")
        self.resizable(False, False)

        self._cargar_imagenes()

        self.sidebar_frame = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.sidebar_frame.pack(side="left", fill="y")

        if self.logo_sidebar_img:
            self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="", image=self.logo_sidebar_img)
        else:
            self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="COMERCIADB", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.pack(pady=(30, 20), padx=20)

        self.botones = {}
        
        opciones_menu = [
            ("1. Inicio", self.mostrar_inicio),
            ("2. Clientes y Ventas", self.mostrar_clientes),
            ("3. Inventario", self.mostrar_inventario),
            ("4. Compras", self.mostrar_compras),
            ("5. Finanzas", self.mostrar_finanzas)
        ]

        for texto, comando in opciones_menu:
            btn = ctk.CTkButton(
                self.sidebar_frame, 
                text=texto, 
                command=lambda c=comando, t=texto: self._ejecutar_accion(c, t), 
                anchor="w", 
                height=40,
                fg_color="transparent", # Inician transparentes
                text_color=("gray10", "gray90")
            )
            btn.pack(pady=5, padx=20, fill="x")
            self.botones[texto] = btn

        # Botón de Salir (Fijo al fondo)
        self.btn_salir = ctk.CTkButton(
            self.sidebar_frame, text="Cerrar Sistema", command=self.quit,
            fg_color="#c0392b", hover_color="#e74c3c", text_color="white", # Color rojo para salir
            anchor="w", height=35
        )
        self.btn_salir.pack(side="bottom", pady=30, padx=20, fill="x")

        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(side="right", expand=True, fill="both", padx=20, pady=20)

        self._ejecutar_accion(self.mostrar_inicio, "1. Inicio")

    def _cargar_imagenes(self):
        """Carga las imágenes del sistema de forma segura."""
        self.logo_sidebar_img = None
        self.logo_centro_img = None
        try:
            imagen = Image.open("logo.png")
            self.logo_sidebar_img = ctk.CTkImage(light_image=imagen, dark_image=imagen, size=(200, 200))
            self.logo_centro_img = ctk.CTkImage(light_image=imagen, dark_image=imagen, size=(300, 300))
        except Exception as e:
            print(f"Advertencia: No se pudo cargar 'logo.png': {e}")

    def _ejecutar_accion(self, comando, nombre_boton):
        """Ejecuta el cambio de frame y resalta el botón activo en el menú."""
        for btn in self.botones.values():
            btn.configure(fg_color="transparent")
        
        if nombre_boton in self.botones:
            self.botones[nombre_boton].configure(fg_color=["#3a7ebf", "#1f538d"])

        comando()

    def limpiar_contenedor(self):
        """Elimina cualquier widget que esté actualmente en la pantalla derecha."""
        for widget in self.container.winfo_children():
            widget.destroy()

    def mostrar_inicio(self):
        self.limpiar_contenedor()
        
        lbl_bienvenida = ctk.CTkLabel(
            self.container, 
            text="Bienvenido al Sistema Contable COMERCIADB", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        lbl_bienvenida.pack(pady=(150, 10))

        lbl_sub = ctk.CTkLabel(
            self.container, 
            text="Selecciona un módulo en el menú lateral izquierdo para comenzar.", 
            font=ctk.CTkFont(size=14),
            text_color="gray"
        )
        lbl_sub.pack(pady=(0, 20))

        if self.logo_centro_img:
            lbl_logo = ctk.CTkLabel(self.container, text="", image=self.logo_centro_img)
            lbl_logo.pack(pady=10)
        else:
            lbl_fallback = ctk.CTkLabel(
                self.container, 
                text="[ Aquí iría tu Logotipo ]", 
                font=ctk.CTkFont(size=16, slant="italic"),
                text_color="gray"
            )
            lbl_fallback.pack(pady=40)

    def mostrar_clientes(self):
        self.limpiar_contenedor()
        self.modulo_clientes = FrameClientes(self.container)
        self.modulo_clientes.pack(expand=True, fill="both")

    def mostrar_inventario(self):
        self.limpiar_contenedor()
        self.modulo_inventario = FrameInventario(self.container)
        self.modulo_inventario.pack(expand=True, fill="both")

    def mostrar_compras(self):
        self.limpiar_contenedor()
        self.modulo_compras = FrameProveedores(self.container)
        self.modulo_compras.pack(expand=True, fill="both")

    def mostrar_finanzas(self):
        self.limpiar_contenedor()
        self.modulo_gastos = FrameGastos(self.container)
        self.modulo_gastos.pack(expand=True, fill="both")

if __name__ == "__main__":
    app = MenuPrincipal()
    app.mainloop()