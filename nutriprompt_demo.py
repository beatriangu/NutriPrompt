import streamlit as st
import os
from fpdf import FPDF
from PIL import Image
import io
from datetime import datetime

st.set_page_config(page_title="NutriPrompt – Plan generado", page_icon="💡", layout="centered")

st.title("💡 NutriPrompt: Tu Plan Semanal Personalizado")

st.markdown("""
Este espacio muestra el resultado final generado con IA a partir de los datos de tu formulario.  
¡Listo para poner en práctica y cuidarte esta semana! 🥑🏃‍♀️🧘‍♂️
""")

# Archivos de entrada
output_path = "output_ejemplo.md"
formulario_path = "datos_cliente_ejemplo.txt"
fondo_path = "media/fondos/bienvenida_fondo.jpg"

# Función para extraer el nombre del cliente desde el .txt
def obtener_nombre_desde_txt(ruta):
    if not os.path.exists(ruta):
        return "Cliente"
    with open(ruta, "r", encoding="utf-8") as f:
        for linea in f:
            if linea.lower().startswith("nombre"):
                return linea.split(":", 1)[1].strip()
    return "Cliente"

# Pie de página
def pie_de_pagina(pdf):
    pdf.set_y(-15)
    pdf.set_font("Arial", "I", 9)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 10, "Generado con IA – NutriPrompt", 0, 0, "C")

# Función para generar PDF completo
def generar_pdf_desde_markdown(contenido, cliente="Cliente", fecha="", fondo_path=""):
    pdf = FPDF()

    # Portada
    pdf.add_page()
    if os.path.exists(fondo_path):
        img = Image.open(fondo_path)
        img = img.resize((595, 842))
        temp_path = "temp_portada.jpg"
        img.save(temp_path)
        pdf.image(temp_path, x=0, y=0, w=210, h=297)
        os.remove(temp_path)

    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", "B", 20)
    pdf.set_xy(0, 100)
    pdf.cell(210, 10, "Plan Semanal NutriPrompt", ln=True, align="C")

    pdf.set_font("Arial", "", 14)
    pdf.cell(210, 10, f"Cliente: {cliente}", ln=True, align="C")
    pdf.cell(210, 10, f"Fecha: {fecha}", ln=True, align="C")

    pie_de_pagina(pdf)

    # Contenido
    pdf.add_page()
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", size=11)
    pdf.set_auto_page_break(auto=True, margin=15)

    for linea in contenido.split("\n"):
        pdf.multi_cell(0, 8, linea)

    pie_de_pagina(pdf)

    pdf_bytes = io.BytesIO()
    pdf.output(pdf_bytes)
    pdf_bytes.seek(0)
    return pdf_bytes

# Mostrar resultado en Streamlit
if os.path.exists(output_path):
    with open(output_path, "r", encoding="utf-8") as f:
        contenido_markdown = f.read()

    nombre_cliente = obtener_nombre_desde_txt(formulario_path)
    fecha_actual = datetime.now().strftime("%d/%m/%Y")

    st.markdown("### 🧾 Resultado generado por IA")
    st.markdown(contenido_markdown, unsafe_allow_html=True)

    pdf_bytes = generar_pdf_desde_markdown(
        contenido_markdown,
        cliente=nombre_cliente,
        fecha=fecha_actual,
        fondo_path=fondo_path
    )

    st.download_button(
        label="📄 Descargar plan como PDF",
        data=pdf_bytes,
        file_name=f"plan_nutriprompt_{nombre_cliente.replace(' ', '_')}.pdf",
        mime="application/pdf"
    )

else:
    st.warning("⚠️ El archivo `output_ejemplo.md` no se ha generado aún. Asegúrate de haber enviado el formulario y pulsado 'Generar plan'.")
