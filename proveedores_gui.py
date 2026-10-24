import customtkinter as ctk
from tkinter import messagebox, ttk
from base_crud import BaseCRUDFrame
from database import obtener_registros_tabla, conectar_db

def operar_proveedor(accion, id_prov=None, nombre="", nit="", contacto="", direccion=""):
    conexion = conectar_db()
    if not conexion: return False, "Error de conexión."
    try:
        cursor = conexion.cursor()
        if accion == "INSERT":
            sql = "INSERT INTO PFproveedores (nombre, nit, contacto, direccion) VALUES (:1, :2, :3, :4)"
            cursor.execute(sql, (nombre, nit, contacto, direccion))
        elif accion == "UPDATE":
            sql = "UPDATE PFproveedores SET nombre=:1, nit=:2, contacto=:3, direccion=:4 WHERE id_proveedor=:5"
            cursor.execute(sql, (nombre, nit, contacto, direccion, id_prov))
        elif accion == "DELETE":
            sql = "DELETE FROM PFproveedores WHERE id_proveedor=:1"
            cursor.execute(sql, (id_prov,))
        conexion.commit()
        return True, "Operación exitosa."
    except Exception as e:
        return False, f"Error: {str(e)}"
    finally:
        if conexion: conexion.close()

def buscar_proveedores_db(termino):
    conexion = conectar_db()
    if not conexion: return []
    try:
        cursor = conexion.cursor()
        sql = """SELECT id_proveedor, nombre, nit, contacto, direccion 
                 FROM PFproveedores 
                 WHERE TO_CHAR(id_proveedor) LIKE :1 
                 OR LOWER(nombre) LIKE :2 
                 OR nit LIKE :3"""
                 
        busqueda = f"%{termino.lower()}%"
        cursor.execute(sql, (busqueda, busqueda, busqueda))
        return cursor.fetchall()
    finally:
        conexion.close()

def insertar_proveedor(nombre, nit, contacto, direccion):
    conexion = conectar_db()
    if not conexion:
        return False, "Error de conexión a la base de datos."
    try:
        cursor = conexion.cursor()
        sql = """
            INSERT INTO PFproveedores (nombre, nit, contacto, direccion)
            VALUES (:1, :2, :3, :4)
        """
        cursor.execute(sql, (nombre, nit, contacto, direccion))
        conexion.commit()
        cursor.close()
        conexion.close()
        return True, "¡Proveedor registrado con éxito!"
    except Exception as e:
        return False, f"Error al insertar proveedor: {str(e)}"

class FrameProveedores(BaseCRUDFrame):
    def __init__(self, parent):
        super().__init__(parent, "Módulo de Proveedores y Compras")

        self.form_frame = ctk.CTkScrollableFrame(self.frame_form, fg_color="transparent")
        self.form_frame.pack(side="left", fill="both", expand=True)

        lbl_form = ctk.CTkLabel(self.form_frame, text="Registrar Proveedor", font=ctk.CTkFont(size=16, weight="bold"))
        lbl_form.pack(pady=15, padx=10)

        self.entry_nombre = self.crear_campo(self.form_frame, "* Nombre / Empresa:")
        self.entry_nit = self.crear_campo(self.form_frame, "NIT:")
        self.entry_contacto = self.crear_campo(self.form_frame, "Persona de Contacto:")
        self.entry_direccion = self.crear_campo(self.form_frame, "Dirección:")

        self.btn_guardar = ctk.CTkButton(
            self.form_frame, 
            text="Guardar Proveedor", 
            command=self.guardar_datos,
            fg_color="#27ae60", 
            hover_color="#2ecc71",
            font=ctk.CTkFont(size=13, weight="bold"),
            height=38
        )
        self.btn_guardar.pack(pady=25, padx=20, fill="x")

        lbl_tabla = ctk.CTkLabel(self.frame_tabla, text="Proveedores Registrados en Oracle", font=ctk.CTkFont(size=16, weight="bold"))
        lbl_tabla.pack(pady=15)

        frame_tree = ctk.CTkFrame(self.frame_tabla, fg_color="transparent")
        frame_tree.pack(padx=15, pady=5, fill="both", expand=True)

        columns = ("ID", "Nombre", "NIT", "Contacto", "Dirección")
        self.tree = ttk.Treeview(frame_tree, columns=columns, show="headings", height=14)
        
        scrollbar = ttk.Scrollbar(frame_tree, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.column("ID", width=40, anchor="center")
        self.tree.column("Nombre", width=140, anchor="w")
        self.tree.column("NIT", width=80, anchor="center")
        self.tree.column("Contacto", width=120, anchor="w")
        self.tree.column("Dirección", width=160, anchor="w")

        for col in columns:
            self.tree.heading(col, text=col)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.btn_refrescar = ctk.CTkButton(
            self.frame_tabla, 
            text="Actualizar Lista", 
            command=self.cargar_datos_tabla,
            height=32,
            width=150
        )
        self.btn_refrescar.pack(pady=15)

        self.cargar_datos_tabla()

    def cargar_datos_tabla(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        
        proveedores = obtener_registros_tabla("PFproveedores", "id_proveedor, nombre, nit, contacto, direccion")
        for p in proveedores:
            self.tree.insert("", "end", values=p)

    def refrescar_datos(self):
        self.entry_buscar.delete(0, 'end')
        for row in self.tree.get_children(): self.tree.delete(row)
        proveedores = obtener_registros_tabla("PFproveedores", "id_proveedor, nombre, nit, contacto, direccion")
        for p in proveedores: self.tree.insert("", "end", values=p)

    def buscar_registros(self):
        termino = self.entry_buscar.get().strip()
        if not termino:
            self.refrescar_datos()
            return
        for row in self.tree.get_children(): self.tree.delete(row)
        for r in buscar_proveedores_db(termino): self.tree.insert("", "end", values=r)

    def eliminar_registro(self):
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning("Selección vacía", "Selecciona un registro para eliminar.")
            return
        id_prov = self.tree.item(seleccion[0])['values'][0]
        if messagebox.askyesno("Confirmar", f"¿Eliminar proveedor ID {id_prov}?"):
            exito, msj = operar_proveedor("DELETE", id_prov=id_prov)
            if exito: self.refrescar_datos()
            else: messagebox.showerror("Error", msj)

    def editar_registro(self):
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning("Selección vacía", "Selecciona un registro para editar.")
            return
        valores = self.tree.item(seleccion[0])['values']
        self.limpiar_campos()
        self.id_seleccionado = valores[0]
        
        self.entry_nombre.insert(0, str(valores[1]))
        self.entry_nit.insert(0, str(valores[2]) if valores[2] != 'None' else "")
        self.entry_contacto.insert(0, str(valores[3]) if valores[3] != 'None' else "")
        self.entry_direccion.insert(0, str(valores[4]) if valores[4] != 'None' else "")
        
        self.btn_guardar.configure(text="Actualizar Proveedor", fg_color="#f39c12", hover_color="#e67e22")

    def guardar_datos(self):
        nombre = self.entry_nombre.get().strip()
        nit = self.entry_nit.get().strip()
        contacto = self.entry_contacto.get().strip()
        direccion = self.entry_direccion.get().strip()

        if not nombre:
            messagebox.showwarning("Incompleto", "El campo Nombre es obligatorio.")
            return

        if getattr(self, 'id_seleccionado', None):
            exito, msj = operar_proveedor("UPDATE", id_prov=self.id_seleccionado, nombre=nombre, nit=nit, contacto=contacto, direccion=direccion)
        else:
            exito, msj = operar_proveedor("INSERT", nombre=nombre, nit=nit, contacto=contacto, direccion=direccion)

        if exito:
            messagebox.showinfo("Éxito", msj)
            self.limpiar_campos()
            self.refrescar_datos()
        else:
            messagebox.showerror("Error", msj)

    def limpiar_campos(self):
        self.id_seleccionado = None
        self.btn_guardar.configure(text="Guardar Proveedor", fg_color="#27ae60", hover_color="#2ecc71")
        self.entry_nombre.delete(0, 'end')
        self.entry_nit.delete(0, 'end')
        self.entry_contacto.delete(0, 'end')
        self.entry_direccion.delete(0, 'end')