import customtkinter as ctk
from tkinter import ttk

class BaseCRUDFrame(ctk.CTkFrame):
    def __init__(self, parent, titulo_modulo):
        super().__init__(parent, fg_color="transparent")

        self.titulo = ctk.CTkLabel(
            self, 
            text=titulo_modulo, 
            font=ctk.CTkFont(size=22, weight="bold")
        )
        self.titulo.pack(pady=(0, 15))

        self.sub_container = ctk.CTkFrame(self, fg_color="transparent")
        self.sub_container.pack(fill="both", expand=True)

        # Panel Izquierdo: Formulario
        self.frame_form = ctk.CTkFrame(self.sub_container, width=340)
        self.frame_form.pack(side="left", fill="y", padx=(0, 10))

        # Panel Derecho: Tabla y Herramientas
        self.frame_tabla = ctk.CTkFrame(self.sub_container)
        self.frame_tabla.pack(side="right", fill="both", expand=True, padx=(10, 0))

        # --- NUEVO: BARRA DE BÚSQUEDA SUPERIOR ---
        self.frame_busqueda = ctk.CTkFrame(self.frame_tabla, fg_color="transparent")
        self.frame_busqueda.pack(fill="x", padx=15, pady=(15, 5))
        
        self.entry_buscar = ctk.CTkEntry(self.frame_busqueda, placeholder_text="Buscar registro...", width=250)
        self.entry_buscar.pack(side="left", padx=(0, 10))
        
        self.btn_buscar = ctk.CTkButton(
            self.frame_busqueda, text="Buscar", width=100, command=self.buscar_registros
        )
        self.btn_buscar.pack(side="left")
        
        self.btn_refrescar = ctk.CTkButton(
            self.frame_busqueda, text="Refrescar Lista", width=140, 
            command=self.refrescar_datos, fg_color="gray50", hover_color="gray40"
        )
        self.btn_refrescar.pack(side="right")

        # --- NUEVO: CONTENEDOR ESPECÍFICO PARA EL TREEVIEW ---
        self.frame_tree_container = ctk.CTkFrame(self.frame_tabla, fg_color="transparent")
        self.frame_tree_container.pack(fill="both", expand=True, padx=15, pady=5)

        # --- NUEVO: BOTONES CRUD INFERIORES ---
        self.frame_acciones = ctk.CTkFrame(self.frame_tabla, fg_color="transparent")
        self.frame_acciones.pack(fill="x", padx=15, pady=(5, 15))

        self.btn_editar = ctk.CTkButton(
            self.frame_acciones, text="Editar Seleccionado", 
            command=self.editar_registro, fg_color="#f39c12", hover_color="#e67e22"
        )
        self.btn_editar.pack(side="left", padx=(0, 10))

        self.btn_eliminar = ctk.CTkButton(
            self.frame_acciones, text="Eliminar Seleccionado", 
            command=self.eliminar_registro, fg_color="#e74c3c", hover_color="#c0392b"
        )
        self.btn_eliminar.pack(side="left")

    def crear_campo(self, parent, label_text):
        lbl = ctk.CTkLabel(parent, text=label_text, font=ctk.CTkFont(size=12, weight="bold"))
        lbl.pack(anchor="w", padx=20, pady=(5, 2))
        entry = ctk.CTkEntry(parent, width=260)
        entry.pack(padx=20, pady=(0, 8))
        return entry

    # --- MÉTODOS BASE (Se sobreescribirán en cada módulo hijo) ---
    def buscar_registros(self):
        """Método a personalizar en el hijo para ejecutar SELECT ... WHERE"""
        pass
        
    def refrescar_datos(self):
        """Método a personalizar en el hijo para recargar la tabla"""
        pass

    def editar_registro(self):
        """Método a personalizar en el hijo para ejecutar UPDATE"""
        pass

    def eliminar_registro(self):
        """Método a personalizar en el hijo para ejecutar DELETE"""
        pass