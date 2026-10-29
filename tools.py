import json
import re
import sqlite3
import pandas as pd

DB_PATH = "empresa_bi.db"

# 1. Esquema de la herramienta SQL para las LLMs
sql_tool_schema = {
    "name": "execute_sql_query",
    "description": (
        "Ejecuta una consulta SQL SELECT en la base de datos de e-commerce de la empresa. "
        "Usa esta herramienta para responder preguntas sobre ventas, clientes, inventario, "
        "ingresos, métricas por región, estados de pedidos o rendimiento de categorías.\n\n"
        "Estructura del Esquema de la BD (SQLite):\n"
        "1. ventas(id_venta, fecha, id_cliente, id_producto, cantidad, metodo_pago, estado)\n"
        "   - 'estado' puede ser: 'Completa', 'Pendiente', 'Cancelada'.\n"
        "2. clientes(id_cliente, nombre, apellido, email, fecha_registro, region)\n"
        "3. productos(id_producto, nombre_producto, id_categoria, precio_unitario, stock)\n"
        "4. categorias_productos(id_categoria, categoria, descripcion)\n"
        "5. metodos_pago(id_metodo, metodo, descripcion)\n\n"
        "Notas para consultas:\n"
        "- Puedes realizar JOINs entre las tablas usando sus identificadores (ej. ventas.id_cliente = clientes.id_cliente).\n"
        "- Para calcular ingresos totales en ventas, multiplica ventas.cantidad * productos.precio_unitario haciendo JOIN."

        "Notas sobre Fechas en SQLite:\n"
        "- La columna 'fecha' está guardada en formato TEXT ('YYYY-MM-DD').\n"
        "- Para agrupar o filtrar por mes en SQLite, USA OBLIGATORIAMENTE strftime('%Y-%m', fecha) o substr(fecha, 1, 7).\n"
        "- NO uses funciones de otros motores como MONTH(), EXTRACT() o DATE_FORMAT()."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Consulta SQL SELECT válida, optimizada y sanitizada a ejecutar.",
            }
        },
        "required": ["query"],
        "additionalProperties": False,
    },
}


# 2. Guardián de Seguridad SQL
def validate_sql_query(query: str) -> tuple[bool, str]:
  """Valida que la consulta sea exclusivamente un SELECT de lectura sin comandos destructivos."""
  clean_query = query.strip().upper()

  if not clean_query.startswith("SELECT"):
    return (
        False,
        "Seguridad: Solo se permiten consultas de lectura que inicien con SELECT.",
    )

  forbidden_keywords = [
      "DROP",
      "DELETE",
      "INSERT",
      "UPDATE",
      "ALTER",
      "CREATE",
      "TRUNCATE",
      "EXEC",
      "EXECUTE",
      "--",
      ";",
  ]

  for kw in forbidden_keywords:
    if re.search(r"\b" + kw + r"\b", clean_query):
      return (
          False,
          f"Seguridad: Se detectó un comando no permitido en la consulta ({kw}).",
      )

  return True, ""


# 3. Ejecutor Seguro de Consultas SQL
def execute_sql_query_safe(query: str) -> tuple[str, pd.DataFrame]:
  """Ejecuta una consulta SQL sanitizada y retorna el resultado en texto y como DataFrame."""
  print(f"\n🛡️ [SQL ENGINE] Validando y ejecutando: {query}\n", flush=True)

  is_safe, error_message = validate_sql_query(query)
  if not is_safe:
    print(f"⚠️ [SQL ENGINE] Bloqueo: {error_message}")
    return error_message, pd.DataFrame()

  try:
    with sqlite3.connect(DB_PATH) as conn:
      df = pd.read_sql_query(query, conn)
      if df.empty:
        return "La consulta no devolvió registros.", pd.DataFrame()
      return df.to_string(index=False), df
  except Exception as e:
    return f"Error de ejecución SQL: {str(e)}", pd.DataFrame()