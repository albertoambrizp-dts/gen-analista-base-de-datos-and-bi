# Agente Analista de Datos & BI

Un agente sencillo en Python para hacer consultas en lenguaje natural a una base de datos SQLite local, obtener tablas con Pandas y visualizar resultados con Matplotlib usando una interfaz en Gradio.

## Stack
- **Python 3.10+**
- **OpenAI API** (`gpt-4o-mini` mediante Function Calling)
- **SQLite3** y **Pandas**
- **Gradio** y **Matplotlib**
- **uv** (para entorno y dependencias)

## Qué hace
- Traduce preguntas de negocio a consultas `SELECT` en SQL.
- Valida la consulta para evitar comandos destructivos (`DROP`, `DELETE`, etc.).
- Muestra los resultados en tabla y genera una gráfica de barras dinámica.
- Devuelve un resumen corto con los puntos clave.

## Estructura
```text
.
├── data/          # Archivos CSV origen
├── database.py    # Carga de datos a SQLite
├── tools.py       # Esquema y validación de consultas SQL
├── agents.py      # Lógica del agente OpenAI
├── app.py         # Interfaz en Gradio
├── empresa_bi.db  # Base de datos SQLite
└── requirements.txt