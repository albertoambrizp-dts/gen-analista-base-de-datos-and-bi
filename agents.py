import json
import pandas as pd
from openai import OpenAI
from tools import execute_sql_query_safe, sql_tool_schema

# Prompt principal
SYSTEM_PROMPT = (
    "Eres un Analista Senior de BI corporativo. Analiza la pregunta de negocio, "
    "consulta la base de datos mediante la herramienta SQL y proporciona un resumen "
    "ejecutivo con hallazgos clave y métricas relevantes."
)


def run_agent_openai(prompt: str, client: OpenAI) -> tuple[str, pd.DataFrame]:
  """Agente principal que procesa la consulta con OpenAI y ejecuta SQL si es necesario."""
  tools = [{"type": "function", "function": sql_tool_schema}]
  messages = [
      {"role": "system", "content": SYSTEM_PROMPT},
      {"role": "user", "content": prompt},
  ]

  response = client.chat.completions.create(
      model="gpt-4o-mini", messages=messages, tools=tools
  )

  last_df = pd.DataFrame()

  #  llamada a la herramienta 
  while response.choices[0].finish_reason == "tool_calls":
    message = response.choices[0].message
    tool_call = message.tool_calls[0]

    if tool_call.function.name == "execute_sql_query":
      args = json.loads(tool_call.function.arguments)
      query_str = args.get("query", "")

      
      result_text, df_data = execute_sql_query_safe(query_str)
      if not df_data.empty:
        last_df = df_data

     
      messages.append(message)
      messages.append({
          "role": "tool",
          "content": result_text,
          "tool_call_id": tool_call.id,
      })

      # Enviamos la respuesta de la base de datos de vuelta al modelo
      response = client.chat.completions.create(
          model="gpt-4o-mini", messages=messages, tools=tools
      )

  return response.choices[0].message.content or "", last_df