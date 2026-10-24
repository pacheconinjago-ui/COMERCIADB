import customtkinter as ctk
from tkinter import messagebox, ttk
from base_crud import BaseCRUDFrame
from database import  obtener_registros_tabla,conectar_db

def operar_cliente(accion, id_cliente=None, nombre="", apellido="", nit="", telefono="", correo=""):
    conexion = conectar_db()
    if not conexion: return False, "Error de conexión."
    try:
        cursor = conexion.cursor()
        if accion == "INSERT":
            sql = "INSERT INTO PFclientes (nombre, apellido, no_telefono, nit, correo) VALUES (:1, :2, :3, :4, :5)"
            cursor.execute(sql, (nombre, apellido, telefono, nit, correo))
        elif accion == "UPDATE":
            # Se corrigió la sentencia UPDATE para que coincida con las columnas reales de la base de datos
            sql = "UPDATE PFclientes SET nombre=:1, apellido=:2, no_telefono=:3, nit=:4, correo=:5 WHERE id_cliente=:6"
            cursor.execute(sql, (nombre, apellido, telefono, nit, correo, id_cliente))
        elif accion == "DELETE":
            sql = "DELETE FROM PFclientes WHERE id_cliente=:1"
            cursor.execute(sql, (id_cliente,))
        conexion.commit()
        return True, "Operación exitosa."
    except Exception as e:
        return False, f"Error: {str(e)}"
    finally:
        if conexion: conexion.close()

def buscar_clientes_db(termino):
    conexion = conectar_db()
    if not conexion: return []
    try:
        cursor = conexion.cursor()
        # Se añadió 'apellido', se cambió a PFclientes y se ajustaron los parámetros para evitar DPY-4009
        sql = """SELECT id_cliente, nombre, apellido, no_telefono, nit, correo 
                 FROM PFclientes 
                 WHERE LOWER(nombre) LIKE :1 
                 OR LOWER(apellido) LIKE :2 
                 OR nit LIKE :3"""
        busqueda = f"%{termino.lower()}%"
        cursor.execute(sql, (busqueda, busqueda, busqueda))
        return cursor.fetchall()
    finally:
        conexion.close()

class FrameClientes(BaseCRUDFrame):
    def __init__(self, parent):
        super().__init__(parent, "Módulo de Gestión de Clientes y Ventas")

        lbl_form = ctk.CTkLabel(self.frame_form, text="Registrar Nuevo Cliente", font=ctk.CTkFont(size=16, weight="bold"))
        lbl_form.pack(pady=15)

        self.entry_nombre = self.crear_campo(self.frame_form, "* Nombre:")
        self.entry_apellido = self.crear_campo(self.frame_form, "Apellido:")
        self.entry_telefono = self.crear_campo(self.frame_form, "Teléfono:")
        self.entry_nit = self.crear_campo(self.frame_form, "NIT:")
        self.entry_correo = self.crear_campo(self.frame_form, "* Correo Electrónico:")

        self.btn_guardar = ctk.CTkButton(
            self.frame_form, 
            text="Guardar Cliente", 
            command=self.guardar_datos,
            fg_color="#27ae60",
            hover_color="#2ecc71",
            font=ctk.CTkFont(size=13, weight="bold"),
            height=38
        )
        self.btn_guardar.pack(pady=20, padx=20, fill="x")

        lbl_tabla = ctk.CTkLabel(self.frame_tabla, text="Clientes Registrados", font=ctk.CTkFont(size=16, weight="bold"))
        lbl_tabla.pack(pady=15)

        frame_tree = ctk.CTkFrame(self.frame_tabla, fg_color="transparent")
        frame_tree.pack(padx=15, pady=5, fill="both", expand=True)

        columns = ("ID", "Nombre", "Apellido", "Teléfono", "NIT", "Correo")
        self.tree = ttk.Treeview(frame_tree, columns=columns, show="headings", height=14)
        
        scrollbar = ttk.Scrollbar(frame_tree, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.column("ID", width=40, anchor="center")
        self.tree.column("Nombre", width=90, anchor="w")
        self.tree.column("Apellido", width=90, anchor="w")
        self.tree.column("Teléfono", width=80, anchor="center")
        self.tree.column("NIT", width=80, anchor="center")
        self.tree.column("Correo", width=140, anchor="w")

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
        
        clientes = obtener_registros_tabla("PFclientes", "id_cliente, nombre, apellido, no_telefono, nit, correo")
        for c in clientes:
            self.tree.insert("", "end", values=c)

    def refrescar_datos(self):
        self.entry_buscar.delete(0, 'end')
        for row in self.tree.get_children(): self.tree.delete(row)
        clientes = obtener_registros_tabla("PFclientes", "id_cliente, nombre, apellido, no_telefono, nit, correo")
        for c in clientes: self.tree.insert("", "end", values=c)

    def buscar_registros(self):
        termino = self.entry_buscar.get().strip()
        if not termino:
            self.refrescar_datos()
            return
        for row in self.tree.get_children(): self.tree.delete(row)
        for r in buscar_clientes_db(termino): self.tree.insert("", "end", values=r)

    def eliminar_registro(self):
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning("Selección vacía", "Selecciona un registro para eliminar.")
            return
        id_cli = self.tree.item(seleccion[0])['values'][0]
        if messagebox.askyesno("Confirmar", f"¿Eliminar cliente ID {id_cli}?"):
            exito, msj = operar_cliente("DELETE", id_cliente=id_cli)
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
        self.entry_apellido.insert(0,str(valores[2]))
        self.entry_nit.insert(0, str(valores[4]) if valores[4] != 'None' else "")
        self.entry_telefono.insert(0, str(valores[3]) if valores[3] != 'None' else "")
        self.entry_direccion.insert(0, str(valores[5]) if valores[5] != 'None' else "")
        
        self.btn_guardar.configure(text="Actualizar Cliente", fg_color="#f39c12", hover_color="#e67e22")

    def guardar_datos(self):
            nombre = self.entry_nombre.get().strip()
            apellido = self.entry_apellido.get().strip()
            nit = self.entry_nit.get().strip()
            telefono = self.entry_telefono.get().strip()
            # Cambio de entry_direccion a entry_correo
            correo = self.entry_correo.get().strip()
    
            if not nombre:
                messagebox.showwarning("Incompleto", "El campo Nombre es obligatorio.")
                return
    
            # Se ajustaron los parámetros para que coincidan con la función operar_cliente
            if getattr(self, 'id_seleccionado', None):
                exito, msj = operar_cliente("UPDATE", id_cliente=self.id_seleccionado, nombre=nombre, apellido=apellido, telefono=telefono, nit=nit, correo=correo)
            else:
                exito, msj = operar_cliente("INSERT", nombre=nombre, apellido=apellido, telefono=telefono, nit=nit, correo=correo)
    
            if exito:
                messagebox.showinfo("Éxito", msj)
                self.limpiar_campos()
                self.refrescar_datos()
            else:
                messagebox.showerror("Error", msj)

    def editar_registro(self):
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning("Selección vacía", "Selecciona un registro para editar.")
            return
        valores = self.tree.item(seleccion[0])['values']
        self.limpiar_campos()
        self.id_seleccionado = valores[0]
        
        self.entry_nombre.insert(0, str(valores[1]))
        self.entry_apellido.insert(0, str(valores[2]) if str(valores[2]) != 'None' else "")
        self.entry_telefono.insert(0, str(valores[3]) if str(valores[3]) != 'None' else "")
        self.entry_nit.insert(0, str(valores[4]) if str(valores[4]) != 'None' else "")
        # Cambio de entry_direccion a entry_correo
        self.entry_correo.insert(0, str(valores[5]) if str(valores[5]) != 'None' else "")
        
        self.btn_guardar.configure(text="Actualizar Cliente", fg_color="#f39c12", hover_color="#e67e22")

    def limpiar_campos(self):
        self.id_seleccionado = None
        self.btn_guardar.configure(text="Guardar Cliente", fg_color="#27ae60", hover_color="#2ecc71")
        self.entry_nombre.delete(0, 'end')
        self.entry_apellido.delete(0,'end')
        self.entry_nit.delete(0, 'end')
        self.entry_telefono.delete(0, 'end')
        # Cambio de entry_direccion a entry_correo
        self.entry_correo.delete(0, 'end')