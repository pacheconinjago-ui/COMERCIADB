import customtkinter as ctk
from tkinter import messagebox, ttk
from base_crud import BaseCRUDFrame
from database import conectar_db, obtener_registros_tabla

def operar_gasto(accion, id_gasto=None, categoria="", descripcion="", monto=0, comprobante=""):
    conexion = conectar_db()
    if not conexion: return False, "Error de conexión."
    try:
        cursor = conexion.cursor()
        if accion == "INSERT":
            sql = "INSERT INTO PFgastos (categoria, descripcion, monto, no_comprobante) VALUES (:1, :2, :3, :4)"
            cursor.execute(sql, (categoria, descripcion, monto, comprobante))
        elif accion == "UPDATE":
            sql = "UPDATE PFgastos SET categoria=:1, descripcion=:2, monto=:3, no_comprobante=:4 WHERE id_gastos=:5"
            cursor.execute(sql, (categoria, descripcion, monto, comprobante, id_gasto))
        elif accion == "DELETE":
            sql = "DELETE FROM PFgastos WHERE id_gastos=:1"
            cursor.execute(sql, (id_gasto,))
        conexion.commit()
        return True, "Operación exitosa."
    except Exception as e:
        return False, f"Error: {str(e)}"
    finally:
        if conexion: conexion.close()

def buscar_gastos_db(termino):
    conexion = conectar_db()
    if not conexion: return []
    try:
        cursor = conexion.cursor()
        sql = """SELECT id_gastos, categoria, descripcion, monto, fecha, no_comprobante 
                 FROM PFgastos 
                 WHERE LOWER(categoria) LIKE :1 
                 OR LOWER(descripcion) LIKE :2"""
                 
        busqueda = f"%{termino.lower()}%"
        cursor.execute(sql, (busqueda, busqueda))
        return cursor.fetchall()
    finally:
        conexion.close()

class FrameGastos(BaseCRUDFrame):
    def __init__(self, parent):
        super().__init__(parent, "Módulo de Finanzas y Gastos")
        
        self.id_seleccionado = None

        # --- FORMULARIO (Panel Izquierdo) ---
        self.form_scroll = ctk.CTkScrollableFrame(self.frame_form, fg_color="transparent")
        self.form_scroll.pack(side="left", fill="both", expand=True)

        self.lbl_form_titulo = ctk.CTkLabel(self.form_scroll, text="Registrar Gasto", font=ctk.CTkFont(size=16, weight="bold"))
        self.lbl_form_titulo.pack(pady=15, padx=10)

        self.entry_categoria = self.crear_campo(self.form_scroll, "* Categoría:")
        self.entry_desc = self.crear_campo(self.form_scroll, "* Descripción:")
        self.entry_monto = self.crear_campo(self.form_scroll, "* Monto (Q):")
        self.entry_comprobante = self.crear_campo(self.form_scroll, "No. Comprobante:")

        self.btn_guardar = ctk.CTkButton(
            self.form_scroll, text="Guardar Gasto", command=self.guardar_datos,
            fg_color="#27ae60", hover_color="#2ecc71", font=ctk.CTkFont(size=13, weight="bold"), height=38
        )
        self.btn_guardar.pack(pady=25, padx=20, fill="x")

        self.btn_cancelar_edicion = ctk.CTkButton(
            self.form_scroll, text="Cancelar Edición", command=self.limpiar_campos, fg_color="gray50"
        )
        # Se oculta por defecto hasta que se presione "Editar"

        # --- TABLA (Panel Derecho) ---
        columns = ("ID", "Categoría", "Descripción", "Monto", "Fecha", "Comprobante")
        
        # IMPORTANTE: La tabla ahora se empaqueta en self.frame_tree_container (heredado de base_crud)
        self.tree = ttk.Treeview(self.frame_tree_container, columns=columns, show="headings", height=14)
        scrollbar = ttk.Scrollbar(self.frame_tree_container, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        anchos = {"ID": 40, "Categoría": 110, "Descripción": 150, "Monto": 80, "Fecha": 100, "Comprobante": 100}
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=anchos[col], anchor="w" if col in ["Categoría", "Descripción"] else "center")

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.refrescar_datos()

    # --- IMPLEMENTACIÓN DE LOS MÉTODOS CRUD HEREDADOS ---
    def refrescar_datos(self):
        self.entry_buscar.delete(0, 'end')
        for row in self.tree.get_children():
            self.tree.delete(row)
        gastos = obtener_registros_tabla("PFgastos", "id_gastos, categoria, descripcion, monto, fecha, no_comprobante")
        for g in gastos:
            self.tree.insert("", "end", values=g)

    def buscar_registros(self):
        termino = self.entry_buscar.get().strip()
        if not termino:
            self.refrescar_datos()
            return
        
        for row in self.tree.get_children():
            self.tree.delete(row)
        resultados = buscar_gastos_db(termino)
        for r in resultados:
            self.tree.insert("", "end", values=r)

    def eliminar_registro(self):
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning("Selección vacía", "Por favor, selecciona un registro de la tabla para eliminar.")
            return
        
        item = self.tree.item(seleccion[0])
        id_gasto = item['values'][0]
        
        if messagebox.askyesno("Confirmar", f"¿Estás seguro de eliminar el gasto ID {id_gasto}?"):
            exito, msj = operar_gasto("DELETE", id_gasto=id_gasto)
            if exito:
                self.refrescar_datos()
            else:
                messagebox.showerror("Error", msj)

    def editar_registro(self):
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning("Selección vacía", "Por favor, selecciona un registro de la tabla para editar.")
            return
        
        item = self.tree.item(seleccion[0])
        valores = item['values']
        
        self.id_seleccionado = valores[0]
        self.limpiar_campos() # Limpia y luego llena
        self.id_seleccionado = valores[0] # Restaurar ID tras limpiar
        
        self.entry_categoria.insert(0, str(valores[1]))
        self.entry_desc.insert(0, str(valores[2]))
        self.entry_monto.insert(0, str(valores[3]))
        self.entry_comprobante.insert(0, str(valores[5]) if valores[5] != 'None' else "")
        
        self.lbl_form_titulo.configure(text=f"Editando Gasto ID: {self.id_seleccionado}")
        self.btn_guardar.configure(text="Actualizar Gasto", fg_color="#f39c12", hover_color="#e67e22")
        self.btn_cancelar_edicion.pack(pady=5)

    def guardar_datos(self):
        categoria = self.entry_categoria.get().strip()
        descripcion = self.entry_desc.get().strip()
        monto_str = self.entry_monto.get().strip()
        comprobante = self.entry_comprobante.get().strip()

        if not categoria or not descripcion or not monto_str:
            messagebox.showwarning("Campos incompletos", "Completa los campos obligatorios (*).")
            return

        try:
            monto = float(monto_str)
        except ValueError:
            messagebox.showwarning("Formato inválido", "El monto debe ser numérico.")
            return

        if self.id_seleccionado:
            exito, mensaje = operar_gasto("UPDATE", id_gasto=self.id_seleccionado, categoria=categoria, descripcion=descripcion, monto=monto, comprobante=comprobante)
        else:
            exito, mensaje = operar_gasto("INSERT", categoria=categoria, descripcion=descripcion, monto=monto, comprobante=comprobante)

        if exito:
            messagebox.showinfo("Éxito", mensaje)
            self.limpiar_campos()
            self.refrescar_datos()
        else:
            messagebox.showerror("Error DB", mensaje)

    def limpiar_campos(self):
        self.id_seleccionado = None
        self.lbl_form_titulo.configure(text="Registrar Gasto")
        self.btn_guardar.configure(text="Guardar Gasto", fg_color="#27ae60", hover_color="#2ecc71")
        self.btn_cancelar_edicion.pack_forget()
        
        self.entry_categoria.delete(0, 'end')
        self.entry_desc.delete(0, 'end')
        self.entry_monto.delete(0, 'end')
        self.entry_comprobante.delete(0, 'end')