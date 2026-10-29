import os
import re
import sqlite3
import unicodedata
import pandas as pd

DATA_DIR = "data"
DB_PATH = "empresa_bi.db"


def clean_column_name(name: str) -> str:
  """Convierte nombres de columnas a snake_case sin acentos ni caracteres especiales."""
  nfkd = unicodedata.normalize("NFKD", str(name))
  no_accents = "".join([c for c in nfkd if not unicodedata.combining(c)])
  cleaned = no_accents.lower().strip()
  cleaned = re.sub(r"[\s\-]+", "_", cleaned)
  return re.sub(r"[^a-z0-9_]", "", cleaned)


def build_database():
  """Lee todos los archivos CSV en DATA_DIR, estandariza fechas a YYYY-MM-DD y los guarda en SQLite."""
  if not os.path.exists(DATA_DIR):
    print(f"La carpeta '{DATA_DIR}' no existe.")
    return

  csv_files = [f for f in os.listdir(DATA_DIR) if f.endswith(".csv")]

  if not csv_files:
    print(f"No se encontraron archivos .csv en la carpeta '{DATA_DIR}'.")
    return

  print(
      f"Procesando {len(csv_files)} archivo(s) CSV desde '{DATA_DIR}'...\n"
  )

  with sqlite3.connect(DB_PATH) as conn:
    for file_name in csv_files:
      file_path = os.path.join(DATA_DIR, file_name)

      
      raw_table_name = os.path.splitext(file_name)[0]
      table_name = clean_column_name(raw_table_name)

   
      df = pd.read_csv(file_path)

     
      original_cols = list(df.columns)
      df.columns = [clean_column_name(col) for col in df.columns]

   
      for date_col in [col for col in df.columns if "fecha" in col]:
        df[date_col] = pd.to_datetime(
            df[date_col], dayfirst=True, errors="coerce"
        ).dt.strftime("%Y-%m-%d")


      df.to_sql(table_name, conn, if_exists="replace", index=False)

      print(f"Tabla '{table_name}' creada exitosamente ({len(df)} filas)")
      print(f"Columnas originales: {original_cols}")
      print(f"Columnas en BD:      {list(df.columns)}\n")

  print(
      f"Base de datos '{DB_PATH}' construida y lista con fechas"
      " estandarizadas."
  )


def verify_database():
  """Verifica las tablas guardadas en la base de datos."""
  if not os.path.exists(DB_PATH):
    print(f"No existe la base de datos '{DB_PATH}'.")
    return

  print(f"RESUMEN DE LA BASE DE DATOS '{DB_PATH}':")
  print("-" * 50)

  with sqlite3.connect(DB_PATH) as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    for table_tuple in tables:
      table_name = table_tuple[0]
      count = pd.read_sql_query(
          f"SELECT COUNT(*) FROM {table_name}", conn
      ).iloc[0, 0]
      cols = pd.read_sql_query(
          f"PRAGMA table_info({table_name})", conn
      )["name"].tolist()
      print(f"Tabla '{table_name}' -> {count} registros")
      print(f"Columnas: {cols}\n")


if __name__ == "__main__":
  build_database()
  verify_database()