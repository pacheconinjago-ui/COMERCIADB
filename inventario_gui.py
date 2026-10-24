import customtkinter as ctk
from tkinter import messagebox, ttk
from base_crud import BaseCRUDFrame
from database import (
    insertar_producto,
    obtener_productos, 
    obtener_categorias, 
    obtener_proveedores_combo, 
    insertar_categoria,
    conectar_db
)

def operar_producto_extra(accion, id_producto=None, codigo="", desc="", id_cat=None, id_prov=None, pcompra=0, pventa=0, stock=0):
    conexion = conectar_db()
    if not conexion: return False, "Error de conexión."
    try:
        cursor = conexion.cursor()
        if accion == "UPDATE":
            sql = """UPDATE PFproducto SET codigo=:1, descripcion=:2, id_categoria=:3, id_proveedor=:4, 
                     precio_compra=:5, precio_venta=:6, stock_min=:7 WHERE id_producto=:8"""
            cursor.execute(sql, (codigo, desc, id_cat, id_prov, pcompra, pventa, stock, id_producto))
        elif accion == "DELETE":
            sql = "DELETE FROM PFproducto WHERE id_producto=:1"
            cursor.execute(sql, (id_producto,))
        conexion.commit()
        return True, "Operación exitosa."
    except Exception as e:
        return False, f"Error: {str(e)}"
    finally:
        if conexion: conexion.close()

def buscar_productos_db(termino):
    conexion = conectar_db()
    if not conexion: return []
    try:
        cursor = conexion.cursor()
        # Se usan :1, :2 y :3 para buscar por ID, código o descripción
        sql = """SELECT p.id_producto, p.codigo, p.descripcion, c.nombre, pr.nombre, p.precio_compra, p.precio_venta, p.stock_min
                 FROM PFproducto p
                 LEFT JOIN PFcategoria_Producto c ON p.id_categoria = c.id_categoria_Producto
                 LEFT JOIN PFproveedores pr ON p.id_proveedor = pr.id_proveedor
                 WHERE TO_CHAR(p.id_producto) LIKE :1 
                 OR LOWER(p.codigo) LIKE :2 
                 OR LOWER(p.descripcion) LIKE :3"""
                 
        busqueda = f"%{termino.lower()}%"
        # Se envía la variable 'busqueda' tres veces para llenar :1, :2 y :3
        cursor.execute(sql, (busqueda, busqueda, busqueda))
        return cursor.fetchall()
    finally:
        conexion.close()

class FrameInventario(BaseCRUDFrame):
    def __init__(self, parent):
        super().__init__(parent, "Módulo de Inventario y Productos")

        self.internal_form_frame = ctk.CTkScrollableFrame(self.frame_form, fg_color="transparent")
        self.internal_form_frame.pack(side="left", fill="both", expand=True)

        lbl_form = ctk.CTkLabel(self.internal_form_frame, text="Registrar Producto", font=ctk.CTkFont(size=16, weight="bold"))
        lbl_form.pack(pady=15, padx=10)

        # Campos de texto (UX: Se marcan con * los obligatorios)
        self.entry_codigo = self.crear_campo(self.internal_form_frame, "* Código:")
        self.entry_desc = self.crear_campo(self.internal_form_frame, "Descripción")
        
        # Selector de Categoría + Botón "+"
        lbl_cat = ctk.CTkLabel(self.internal_form_frame, text="* Categoría:", font=ctk.CTkFont(size=12, weight="bold"))
        lbl_cat.pack(anchor="w", padx=20, pady=(5, 2))

        frame_cat_container = ctk.CTkFrame(self.internal_form_frame, fg_color="transparent")
        frame_cat_container.pack(padx=20, pady=(0, 8), fill="x")
        
        # 1. Empaquetar PRIMERO el botón a la derecha para garantizar su espacio
        self.btn_nueva_cat = ctk.CTkButton(
            frame_cat_container, 
            text="+", 
            width=35, 
            command=self.abrir_ventana_nueva_categoria,
            fg_color="gray50", 
            hover_color="gray40",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.btn_nueva_cat.pack(side="right", padx=(5, 0))

        # 2. Empaquetar SEGUNDO el combo para que use el espacio restante
        self.combo_cat = ctk.CTkComboBox(frame_cat_container, values=["Cargando..."], width=190)
        self.combo_cat.pack(side="left", fill="x", expand=True)

        self.btn_nueva_cat = ctk.CTkButton(
            frame_cat_container, 
            text="+", 
            width=35, 
            command=self.abrir_ventana_nueva_categoria,
            fg_color="gray50", 
            hover_color="gray40",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.btn_nueva_cat.pack(side="right", padx=(5, 0))

        # Selector de Proveedor
        lbl_prov = ctk.CTkLabel(self.internal_form_frame, text="* Proveedor:", font=ctk.CTkFont(size=12, weight="bold"))
        lbl_prov.pack(anchor="w", padx=20, pady=(5, 2))
        
        self.combo_prov = ctk.CTkComboBox(self.internal_form_frame, values=["Cargando..."], width=250)
        self.combo_prov.pack(padx=20, pady=(0, 8), fill="x")

        self.entry_pcompra = self.crear_campo(self.internal_form_frame, "* Precio Compra:")
        self.entry_pventa = self.crear_campo(self.internal_form_frame, "* Precio Venta:")
        self.entry_stock_min = self.crear_campo(self.internal_form_frame, "Stock Mínimo:")

        self.btn_guardar = ctk.CTkButton(
            self.internal_form_frame, 
            text="Guardar Producto", 
            command=self.guardar_datos,
            fg_color="#27ae60", 
            hover_color="#2ecc71",
            font=ctk.CTkFont(size=13, weight="bold"),
            height=38
        )
        self.btn_guardar.pack(pady=25, padx=20, fill="x")

        lbl_tabla = ctk.CTkLabel(self.frame_tabla, text="Catálogo de Productos en Oracle", font=ctk.CTkFont(size=16, weight="bold"))
        lbl_tabla.pack(pady=15)

        # Contenedor para integrar la tabla y su barra de desplazamiento
        frame_tree = ctk.CTkFrame(self.frame_tabla, fg_color="transparent")
        frame_tree.pack(padx=15, pady=5, fill="both", expand=True)

        columns = ("ID", "Código", "Descripción", "Categoría", "Proveedor", "P. Compra", "P. Venta", "Stock Min")
        self.tree = ttk.Treeview(frame_tree, columns=columns, show="headings", height=14)
        
        # Scrollbar vertical
        scrollbar = ttk.Scrollbar(frame_tree, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Diccionario para anchos personalizados de columnas
        anchos_columnas = {
            "ID": 40, "Código": 80, "Descripción": 130, 
            "Categoría": 100, "Proveedor": 100, 
            "P. Compra": 80, "P. Venta": 80, "Stock Min": 75
        }

        for col in columns:
            self.tree.heading(col, text=col)
            # Alineación a la izquierda para texto largo, centrado para números/códigos
            alineacion = "w" if col in ["Descripción", "Categoría", "Proveedor"] else "center"
            self.tree.column(col, width=anchos_columnas.get(col, 75), anchor=alineacion)
        
        # Empaquetar la tabla a la izquierda y el scrollbar a la derecha
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.btn_refrescar = ctk.CTkButton(
            self.frame_tabla, 
            text="Actualizar Datos", 
            command=self.refrescar_todo,
            height=32,
            width=150
        )
        self.btn_refrescar.pack(pady=15)

        # Cargar datos iniciales
        self.refrescar_todo()

    def actualizar_combos(self):
        """Carga dinámicamente las categorías y proveedores más recientes de la BD."""
        self.categorias_data = obtener_categorias()
        cat_nombres = [c[1] for c in self.categorias_data] if self.categorias_data else ["Sin categorías"]
        self.combo_cat.configure(values=cat_nombres)
        if cat_nombres and self.combo_cat.get() not in cat_nombres:
            self.combo_cat.set(cat_nombres[0])

        self.proveedores_data = obtener_proveedores_combo()
        prov_nombres = [p[1] for p in self.proveedores_data] if self.proveedores_data else ["Sin proveedores"]
        self.combo_prov.configure(values=prov_nombres)
        if prov_nombres and self.combo_prov.get() not in prov_nombres:
            self.combo_prov.set(prov_nombres[0])

    def refrescar_todo(self):
        """Actualiza la tabla de productos y los comboboxes en un solo llamado."""
        self.cargar_datos_tabla()
        self.actualizar_combos()

    def abrir_ventana_nueva_categoria(self):
        ventana_cat = ctk.CTkToplevel(self)
        ventana_cat.title("Nueva Categoría")
        ventana_cat.geometry("300x180")
        ventana_cat.resizable(False, False)
        ventana_cat.grab_set() # Evita interactuar con la ventana principal hasta cerrar esta

        lbl = ctk.CTkLabel(ventana_cat, text="Nombre de la Categoría:", font=ctk.CTkFont(size=12, weight="bold"))
        lbl.pack(pady=(20, 5))

        entry_cat = ctk.CTkEntry(ventana_cat, width=240)
        entry_cat.pack(pady=5)

        def guardar_nueva_cat():
            nombre_cat = entry_cat.get().strip()
            if not nombre_cat:
                messagebox.showwarning("Error", "El nombre no puede estar vacío.", parent=ventana_cat)
                return

            exito, mensaje = insertar_categoria(nombre_cat)
            if exito:
                messagebox.showinfo("Éxito", mensaje, parent=ventana_cat)
                self.actualizar_combos() # Refresca el combo directamente
                self.combo_cat.set(nombre_cat) # Selecciona la recién creada
                ventana_cat.destroy()
            else:
                messagebox.showerror("Error", mensaje, parent=ventana_cat)

        btn_guardar_cat = ctk.CTkButton(ventana_cat, text="Guardar Categoría", command=guardar_nueva_cat, fg_color="#27ae60", hover_color="#2ecc71", height=32)
        btn_guardar_cat.pack(pady=15)

    def cargar_datos_tabla(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        
        productos = obtener_productos()
        for p in productos:
            self.tree.insert("", "end", values=p)

    def refrescar_datos(self):
        self.entry_buscar.delete(0, 'end')
        self.cargar_datos_tabla() # Usa tu función existente
        self.actualizar_combos()  # Usa tu función existente

    def buscar_registros(self):
        termino = self.entry_buscar.get().strip()
        if not termino:
            self.refrescar_datos()
            return
        for row in self.tree.get_children(): self.tree.delete(row)
        for r in buscar_productos_db(termino): self.tree.insert("", "end", values=r)

    def eliminar_registro(self):
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning("Selección vacía", "Selecciona un producto para eliminar.")
            return
        id_prod = self.tree.item(seleccion[0])['values'][0]
        if messagebox.askyesno("Confirmar", f"¿Eliminar producto ID {id_prod}?"):
            exito, msj = operar_producto_extra("DELETE", id_producto=id_prod)
            if exito: self.refrescar_datos()
            else: messagebox.showerror("Error", msj)

    def editar_registro(self):
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning("Selección vacía", "Selecciona un producto para editar.")
            return
        valores = self.tree.item(seleccion[0])['values']
        self.limpiar_campos()
        self.id_seleccionado = valores[0]
        
        self.entry_codigo.insert(0, str(valores[1]))
        self.entry_desc.insert(0, str(valores[2]) if valores[2] != 'None' else "")
        self.combo_cat.set(str(valores[3]))
        self.combo_prov.set(str(valores[4]))
        self.entry_pcompra.insert(0, str(valores[5]))
        self.entry_pventa.insert(0, str(valores[6]))
        self.entry_stock_min.insert(0, str(valores[7]) if len(valores)>7 and valores[7] != 'None' else "0")
        
        self.btn_guardar.configure(text="Actualizar Producto", fg_color="#f39c12", hover_color="#e67e22")

    def guardar_datos(self):
        codigo = self.entry_codigo.get().strip()
        descripcion = self.entry_desc.get().strip()
        cat_nombre = self.combo_cat.get()
        prov_nombre = self.combo_prov.get()
        p_compra = self.entry_pcompra.get().strip()
        p_venta = self.entry_pventa.get().strip()
        stock_min = self.entry_stock_min.get().strip() or "0"

        if not codigo or not p_compra or not p_venta:
            messagebox.showwarning("Incompleto", "Llena los campos obligatorios (*).")
            return

        try:
            p_compra_f, p_venta_f, stock_min_i = float(p_compra), float(p_venta), int(stock_min)
        except ValueError:
            messagebox.showwarning("Formato inválido", "Precios y stock deben ser numéricos.")
            return

        id_cat = next((c[0] for c in self.categorias_data if c[1] == cat_nombre), None)
        id_prov = next((p[0] for p in self.proveedores_data if p[1] == prov_nombre), None)

        if not id_cat or not id_prov:
            messagebox.showerror("Error", "Selecciona categoría y proveedor válidos.")
            return

        if getattr(self, 'id_seleccionado', None):
            exito, msj = operar_producto_extra("UPDATE", id_producto=self.id_seleccionado, codigo=codigo, desc=descripcion, 
                                               id_cat=id_cat, id_prov=id_prov, pcompra=p_compra_f, pventa=p_venta_f, stock=stock_min_i)
        else:
            from database import insertar_producto
            exito, msj = insertar_producto(codigo, descripcion, id_cat, id_prov, p_compra_f, p_venta_f, stock_min_i, None)

        if exito:
            messagebox.showinfo("Éxito", msj)
            self.limpiar_campos()
            self.refrescar_datos()
        else:
            messagebox.showerror("Error", msj)

    def limpiar_campos(self):
        self.id_seleccionado = None
        self.btn_guardar.configure(text="Guardar Producto", fg_color="#27ae60", hover_color="#2ecc71")
        self.entry_codigo.delete(0, 'end')
        self.entry_desc.delete(0, 'end')
        self.entry_pcompra.delete(0, 'end')
        self.entry_pventa.delete(0, 'end')
        self.entry_stock_min.delete(0, 'end')