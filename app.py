import os
import matplotlib.pyplot as plt
import pandas as pd
import gradio as gr
from dotenv import load_dotenv
from openai import OpenAI

from agents import run_agent_openai

load_dotenv(override=True)

openai_key = os.getenv("OPENAI_API_KEY")
client_openai = OpenAI(api_key=openai_key) if openai_key else None

def generate_chart(df: pd.DataFrame):
    if df.empty or len(df.columns) < 2:
        return None

    x_col = df.columns[0]
    num_cols = df.select_dtypes(include=['number']).columns.tolist()
    y_col = num_cols[1] if (len(num_cols) > 1 and num_cols[0] == x_col) else (num_cols[0] if num_cols else None)

    if y_col:
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.bar(df[x_col].astype(str), df[y_col], color="#1f77b4")
        ax.set_xlabel(x_col.replace('_', ' ').capitalize())
        ax.set_ylabel(y_col.replace('_', ' ').capitalize())
        ax.set_title(f"{y_col.replace('_', ' ').capitalize()} por {x_col.replace('_', ' ').capitalize()}")
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        return fig

    return None

def main_pipeline(prompt: str):
    if not prompt.strip():
        return "⚠️ Ingresa una consulta válida.", pd.DataFrame(), None

    if not client_openai:
        return "❌ API Key de OpenAI no configurada en el .env", pd.DataFrame(), None

    try:
        text_res, df_res = run_agent_openai(prompt, client_openai)
        chart_fig = generate_chart(df_res)
        return text_res, df_res, chart_fig
    except Exception as e:
        return f"❌ Error al procesar:\n\n`{str(e)}`", pd.DataFrame(), None

with gr.Blocks(title="Agente BI Corporativo") as demo:
    gr.Markdown("# 📊 Agente Analista de Datos & BI Corporativo")
    
    with gr.Row():
        with gr.Column(scale=1):
            input_prompt = gr.Textbox(label="Consulta de Negocio:", placeholder="Ej. ¿Ventas por mes?", lines=3)
            btn_submit = gr.Button("Analizar Datos 🚀", variant="primary")

        with gr.Column(scale=2):
            output_markdown = gr.Markdown(label="Resumen Ejecutivo:")
            output_table = gr.Dataframe(label="Datos SQL Extraídos:")
            output_plot = gr.Plot(label="Visualización Dinámica:")

    btn_submit.click(
        fn=main_pipeline,
        inputs=[input_prompt],
        outputs=[output_markdown, output_table, output_plot]
    )

if __name__ == "__main__":
    demo.launch(inbrowser=True)