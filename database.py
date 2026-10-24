import oracledb
from config import DB_USER, DB_PASSWORD, DB_DSN

def conectar_db():
    try:
        return oracledb.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            dsn=DB_DSN
        )
    except oracledb.Error as e:
        error, = e.args
        print(f"Error de conexión a Oracle: {error.message}")
        return None

def obtener_registros_tabla(nombre_tabla, columnas="*"):
    conexion = conectar_db()
    if not conexion:
        return []
    
    try:
        with conexion:
            with conexion.cursor() as cursor:
                cursor.execute(f"SELECT {columnas} FROM {nombre_tabla}")
                return cursor.fetchall()
    except Exception as e:
        print(f"Error al consultar la tabla {nombre_tabla}: {str(e)}")
        return []

def eliminar_registro_por_id(nombre_tabla, nombre_columna_id, id_valor):
    conexion = conectar_db()
    if not conexion:
        return False, "No se pudo conectar a la base de datos."
    
    try:
        with conexion:
            with conexion.cursor() as cursor:
                sql = f"DELETE FROM {nombre_tabla} WHERE {nombre_columna_id} = :1"
                cursor.execute(sql, (id_valor,))
                conexion.commit()
                return True, "¡Registro eliminado con éxito!"
    except Exception as e:
        return False, f"Error al eliminar: {str(e)}"

def obtener_categorias():
    return obtener_registros_tabla("PFcategoria_producto", "id_categoria_producto, nombre")

def insertar_categoria(nombre):
    conexion = conectar_db()
    if not conexion:
        return False, "No se pudo conectar a la base de datos."
    
    try:
        with conexion:
            with conexion.cursor() as cursor:
                sql = "INSERT INTO PFcategoria_producto (nombre) VALUES (:1)"
                cursor.execute(sql, (nombre,))
                conexion.commit()
                return True, "¡Categoría registrada con éxito!"
    except Exception as e:
        return False, f"Error al insertar categoría: {str(e)}"

def obtener_proveedores_combo():
    return obtener_registros_tabla("PFproveedores", "id_proveedor, nombre")

def insertar_producto(codigo, descripcion, id_categoria, id_proveedor, p_compra, p_venta, stock_min, stock_max):
    conexion = conectar_db()
    if not conexion:
        return False, "No se pudo conectar a la base de datos."
    
    try:
        with conexion:
            with conexion.cursor() as cursor:
                sql = """
                    INSERT INTO PFproducto (codigo, descripcion, id_categoria, id_proveedor, precio_compra, precio_venta, stock_min, stock_max)
                    VALUES (:1, :2, :3, :4, :5, :6, :7, :8)
                """
                cursor.execute(sql, (codigo, descripcion, id_categoria, id_proveedor, p_compra, p_venta, stock_min, stock_max))
                conexion.commit()
                return True, "¡Producto registrado con éxito!"
    except Exception as e:
        return False, f"Error al insertar producto: {str(e)}"

def obtener_productos():
    conexion = conectar_db()
    if not conexion:
        return []
    
    try:
        with conexion:
            with conexion.cursor() as cursor:
                sql = """
                    SELECT p.id_producto, p.codigo, p.descripcion, c.nombre, pr.nombre, p.precio_compra, p.precio_venta, p.stock_min
                    FROM PFproducto p
                    JOIN PFcategoria_producto c ON p.id_categoria = c.id_categoria_producto
                    JOIN PFproveedores pr ON p.id_proveedor = pr.id_proveedor
                """
                cursor.execute(sql)
                return cursor.fetchall()
    except Exception as e:
        print(f"Error al consultar productos: {str(e)}")
        return []