import streamlit as st
import pandas as pd
import random

st.set_page_config(page_title="NutriPrompt Demo", page_icon="🍽️", layout="wide")

# Simulación de datos extraídos del formulario
cliente = {
    "nombre": "Carla Rodríguez",
    "edad": 29,
    "peso": 68,
    "altura": 165,
    "presupuesto": 45,
    "horarios_ejercicio": ["Lunes 18:00–19:00", "Miércoles 18:00–19:00", "Viernes 18:00–19:00"],
    "restricciones": ["sin gluten", "digestiones pesadas"],
    "objetivo_peso": "Perder 3 kg en 6 semanas",
    "tiempo_cocina": 60,
    "actividad": "moderado",
    "comentarios": ["snacks saludables", "evitar impacto en rodillas"]
}

# Función para generar el plan
@st.cache_data
def generar_plan(cliente):
    dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    desayunos = ["Tostadas de arroz con aguacate", "Smoothie de plátano y avena sin gluten"]
    comidas = ["Quinoa con pollo y verduras", "Ensalada de lentejas y huevo cocido"]
    cenas = ["Crema de calabaza con huevo", "Tortilla de espinacas"]
    snacks = ["Yogur sin lactosa con nueces", "Fruta + puñado de semillas"]
    ejercicios = ["Bicicleta estática 30 min", "Yoga suave 30 min", "Ejercicios de core sin impacto"]
    descansos = ["Estiramientos 10 min antes de dormir", "Respiración profunda 5 min"]

    data = []
    for i, dia in enumerate(dias):
        data.append({
            "Día": dia,
            "🍳 Desayuno": random.choice(desayunos),
            "🥗 Comida": random.choice(comidas),
            "🌙 Cena": random.choice(cenas),
            "🍏 Snack": random.choice(snacks),
            "🏋️ Ejercicio": ejercicios[i % len(ejercicios)],
            "🛌 Descanso": random.choice(descansos),
            "Coste Diario (€)": round(cliente["presupuesto"] / 7, 2)
        })

    return pd.DataFrame(data)

# Interfaz Streamlit
st.title("🧠 NutriPrompt - Generador de Plan Semanal Personalizado")
st.markdown("Este es un ejemplo funcional que simula la generación de un plan basado en datos extraídos de un formulario nutricional PDF.")

with st.expander("📄 Ver resumen del formulario cargado"):
    st.markdown(f"- **Nombre:** {cliente['nombre']}")
    st.markdown(f"- **Edad:** {cliente['edad']} años")
    st.markdown(f"- **Peso:** {cliente['peso']} kg | **Altura:** {cliente['altura']} cm")
    st.markdown(f"- **Objetivo:** {cliente['objetivo_peso']}")
    st.markdown(f"- **Restricciones:** {', '.join(cliente['restricciones'])}")
    st.markdown(f"- **Tiempo de cocina disponible:** {cliente['tiempo_cocina']} min/día")
    st.markdown(f"- **Presupuesto semanal:** {cliente['presupuesto']} €")
    st.markdown(f"- **Comentarios adicionales:** {', '.join(cliente['comentarios'])}")

st.markdown("### 🚀 ¿Lista para generar tu plan?")
if st.button("Generar plan semanal"):
    df = generar_plan(cliente)
    st.success("¡Plan generado con éxito! 💚")
    st.dataframe(df, use_container_width=True)
    total = df["Coste Diario (€)"].sum()
    st.markdown(f"**💰 Total semanal estimado:** `{total:.2f} €`")

st.markdown("---")
st.markdown("👩‍💻 Este proyecto forma parte del servicio de **Soluciones Tecnológicas** (IA + Nutrición).")
