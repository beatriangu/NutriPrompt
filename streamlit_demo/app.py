from __future__ import annotations

from datetime import datetime
from io import BytesIO
import re

import pandas as pd
import streamlit as st
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)


# =========================================================
# Config
# =========================================================

st.set_page_config(
    page_title="NutriPrompt · Demo IA",
    page_icon="🥦",
    layout="wide",
)


# =========================================================
# Visual system
# =========================================================

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:wght@500;600;700&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

.stApp {
    background-color: #FAF7F2;
}

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    color: #1C2420;
}

h1, h2, h3 {
    font-family: 'Fraunces', serif;
    color: #2F4538;
}

code, pre {
    font-family: 'JetBrains Mono', monospace !important;
}

.dossier-header {
    background: #FFFFFF;
    border: 1px solid #E4DDD0;
    border-radius: 10px;
    padding: 2rem 2.2rem;
    margin-bottom: 1.2rem;
    position: relative;
    box-shadow: 0 8px 24px rgba(47,69,56,.05);
}

.dossier-header::before {
    content: "";
    position: absolute;
    left: 0;
    top: 0;
    width: 6px;
    height: 100%;
    background: #C76F4D;
    border-radius: 10px 0 0 10px;
}

.eyebrow {
    font-family: 'JetBrains Mono', monospace;
    font-size: .72rem;
    letter-spacing: .14em;
    text-transform: uppercase;
    color: #C76F4D;
}

.title {
    font-family: 'Fraunces', serif;
    font-size: 2.8rem;
    font-weight: 700;
    color: #2F4538;
    margin: .4rem 0 .2rem 0;
}

.subtitle {
    color: #4A6354;
    max-width: 74ch;
    font-size: 1.02rem;
}

.tag {
    display:inline-block;
    font-family:'JetBrains Mono', monospace;
    font-size:.72rem;
    background:#F1ECE1;
    border:1px solid #E4DDD0;
    color:#2F4538;
    padding:.35rem .75rem;
    border-radius:999px;
    margin:.25rem .25rem .25rem 0;
}

.notice {
    border-left: 4px solid #C76F4D;
    background: #FBEFE6;
    padding: .9rem 1rem;
    border-radius: 4px;
    margin-bottom: 1.3rem;
    color: #1C2420;
}

.card {
    background:#FFFFFF;
    border:1px solid #E4DDD0;
    border-radius:10px;
    padding:1.1rem;
    min-height:135px;
    box-shadow: 0 8px 22px rgba(47,69,56,.035);
}

.card-title {
    font-family:'Fraunces', serif;
    color:#2F4538;
    font-size:1.15rem;
    font-weight:600;
    margin-top:.3rem;
}

.card-body {
    color:#4A6354;
    font-size:.92rem;
}

.section-label {
    font-family:'JetBrains Mono', monospace;
    font-size:.72rem;
    letter-spacing:.12em;
    text-transform:uppercase;
    color:#C76F4D;
}

.kpi-box {
    background:#FFFFFF;
    border:1px solid #E4DDD0;
    border-radius:10px;
    padding:1rem 1.1rem;
    min-height:112px;
    box-shadow: 0 8px 22px rgba(47,69,56,.035);
}

.kpi-label {
    font-size:.9rem;
    color:#4A6354;
    font-weight:600;
    margin-bottom:.35rem;
}

.kpi-value {
    font-family:'Fraunces', serif;
    font-size:2rem;
    line-height:1.1;
    color:#2F4538;
    word-wrap:break-word;
    overflow-wrap:anywhere;
}

.score-box {
    background: linear-gradient(135deg, #FFFFFF, #F1ECE1);
    border:1px solid #E4DDD0;
    border-radius:10px;
    padding:1rem;
}

.footer {
    text-align:center;
    font-family:'JetBrains Mono', monospace;
    color:#4A6354;
    font-size:.75rem;
    border-top:1px solid #E4DDD0;
    margin-top:2rem;
    padding-top:1rem;
}

.small-note {
    color:#4A6354;
    font-size:.9rem;
}
</style>
"""


# =========================================================
# Constants + state
# =========================================================

OBJETIVOS = [
    "Mejora digestiva",
    "Organizar comidas",
    "Comer más equilibrado",
    "Ganar energía",
]

PRESUPUESTOS = ["Ajustado", "Medio", "Flexible"]

RESTRICCIONES = [
    "Low FODMAP",
    "Sin lactosa",
    "Sin gluten",
    "Vegetariano",
    "Vegano",
]

PREFERENCIAS = [
    "Recetas rápidas",
    "Batch cooking",
    "Tupper",
    "Cenas ligeras",
    "Presupuesto ajustado",
]

DEFAULT_STATE = {
    "plan_generado": False,
    "alias": "",
    "edad": None,
    "objetivo": None,
    "presupuesto": None,
    "actividad": 3,
    "contexto": "",
    "restricciones": [],
    "preferencias": [],
    "chat_messages": [],
    "profile_id": None,
}


def init_state() -> None:
    for key, value in DEFAULT_STATE.items():
        st.session_state.setdefault(key, value)


def reset_demo() -> None:
    st.session_state.clear()
    st.rerun()


def reset_chat() -> None:
    st.session_state["chat_messages"] = []
    st.rerun()


# =========================================================
# UI helpers
# =========================================================

def render_header() -> None:
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
    st.markdown(
        """
        <div class="dossier-header">
            <div class="eyebrow">Expediente · NutriPrompt AI · Demo pública</div>
            <div class="title">🥦 NutriPrompt</div>
            <p class="subtitle">
                Plataforma de inteligencia nutricional que combina intake inteligente, reglas,
                RAG, OCR y orquestación multi-modelo para generar planes alimentarios explicables,
                compatibles y descargables.
            </p>
            <span class="tag">Producto Django</span>
            <span class="tag">Demo Streamlit</span>
            <span class="tag">RAG explicado</span>
            <span class="tag">OCR simulado</span>
            <span class="tag">Compatibility Engine</span>
            <span class="tag">PDF report</span>
            <span class="tag">Copilot</span>
        </div>
        <div class="notice">
            ⚠️ Demo técnica con datos simulados. No sustituye asesoramiento médico, sanitario o nutricional profesional.
            La IA no conoce tu nevera ni tus dramas digestivos reales.
        </div>
        """,
        unsafe_allow_html=True,
    )


def card(title: str, body: str, icon: str) -> None:
    st.markdown(
        f"""
        <div class="card">
            <div style="font-size:1.7rem;">{icon}</div>
            <div class="card-title">{title}</div>
            <div class="card-body">{body}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def kpi(label: str, value: str | int) -> None:
    st.markdown(
        f"""
        <div class="kpi-box">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def clean_filename(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"[^a-zA-Z0-9áéíóúÁÉÍÓÚñÑ_-]+", "_", text)
    return text.strip("_") or "persona_demo"


# =========================================================
# Demo logic
# =========================================================

def build_plan() -> pd.DataFrame:
    restricciones = st.session_state.get("restricciones", [])
    vegan = "Vegano" in restricciones
    sin_gluten = "Sin gluten" in restricciones
    sin_lactosa = "Sin lactosa" in restricciones

    if vegan:
        meals = [
            ["Lunes", "Avena con plátano y chía", "Bowl de arroz con tofu y verduras suaves", "Crema de calabacín con garbanzos"],
            ["Martes", "Yogur vegetal con fruta", "Quinoa con verduras y proteína vegetal", "Tortilla vegana de harina de garbanzo"],
            ["Miércoles", "Tostadas sin gluten con aguacate", "Arroz con tofu marinado", "Sopa de verduras y semillas"],
            ["Jueves", "Batido vegetal con fruta", "Patata cocida con verduras y hummus suave", "Salteado de tofu con calabacín"],
            ["Viernes", "Pudding de chía", "Tupper de arroz con verduras", "Cena ligera de crema vegetal"],
        ]
    else:
        desayuno = "Yogur sin lactosa con fruta" if sin_lactosa else "Yogur natural con fruta"
        pan = "Tostadas sin gluten con aceite" if sin_gluten else "Tostadas con aceite"
        pasta = "Pasta sin gluten con pavo" if sin_gluten else "Pasta con pavo"

        meals = [
            ["Lunes", desayuno, "Arroz con pollo y verduras suaves", "Tortilla con espinacas"],
            ["Martes", "Avena con plátano", pasta, "Crema de verduras y huevo"],
            ["Miércoles", pan, "Quinoa con pollo", "Pescado con patata cocida"],
            ["Jueves", "Batido suave de fruta", "Bowl de arroz y verduras", "Revuelto con calabacín"],
            ["Viernes", "Yogur sin lactosa con nueces" if sin_lactosa else "Yogur con nueces", "Tupper de pollo y arroz", "Cena ligera con tortilla"],
        ]

    return pd.DataFrame(meals, columns=["Día", "Desayuno", "Comida", "Cena"])


def shopping_list() -> pd.DataFrame:
    restricciones = st.session_state.get("restricciones", [])
    vegan = "Vegano" in restricciones
    sin_lactosa = "Sin lactosa" in restricciones

    if vegan:
        protein = "Tofu, garbanzos, hummus, semillas"
        breakfast = "Yogur vegetal, avena, fruta, chía"
    else:
        protein = "Pollo, pavo, huevo, pescado, tofu"
        breakfast = "Yogur sin lactosa o natural, fruta, avena, chía" if sin_lactosa else "Yogur, fruta, avena, chía"

    items = [
        ["Proteínas", protein],
        ["Base", "Arroz, quinoa, patata, avena"],
        ["Verduras", "Calabacín, espinacas, zanahoria, verduras suaves"],
        ["Desayunos", breakfast],
        ["Extras", "Nueces, aceite de oliva, semillas"],
    ]
    return pd.DataFrame(items, columns=["Categoría", "Compra sugerida"])


def compatibility_score() -> int:
    score = 94
    if not st.session_state.get("restricciones"):
        score -= 5
    if not st.session_state.get("contexto"):
        score -= 4
    if "Low FODMAP" in st.session_state.get("restricciones", []):
        score -= 2
    if st.session_state.get("presupuesto") == "Ajustado":
        score -= 1
    return max(score, 75)


def compatibility_checks() -> pd.DataFrame:
    restricciones = st.session_state.get("restricciones", [])
    contexto = st.session_state.get("contexto", "")

    rows = [
        [
            "Perfil completo",
            "PASS" if contexto else "WARNING",
            "Contexto incluido" if contexto else "Falta contexto: el plan será menos preciso",
        ],
        [
            "Sin lactosa",
            "PASS" if "Sin lactosa" in restricciones else "INFO",
            "Se priorizan alternativas sin lactosa" if "Sin lactosa" in restricciones else "No indicada",
        ],
        [
            "Sin gluten",
            "PASS" if "Sin gluten" in restricciones else "INFO",
            "Se sustituyen bases con gluten" if "Sin gluten" in restricciones else "No indicada",
        ],
        [
            "Low FODMAP",
            "WARNING" if "Low FODMAP" in restricciones else "INFO",
            "Revisar cebolla, ajo, trigo y manzana" if "Low FODMAP" in restricciones else "No indicada",
        ],
        ["Meal prep", "PASS", "Plan compatible con tupper y batch cooking"],
        ["Presupuesto", "PASS", "Plan ajustado al rango seleccionado"],
    ]

    return pd.DataFrame(rows, columns=["Regla", "Estado", "Detalle"])


def detected_ingredients() -> pd.DataFrame:
    return pd.DataFrame(
        [
            ["Harina de trigo", "Gluten", "WARNING"],
            ["Leche en polvo", "Lactosa", "WARNING"],
            ["Cebolla en polvo", "Low FODMAP", "WARNING"],
            ["Azúcar", "General", "INFO"],
            ["Sal", "General", "INFO"],
        ],
        columns=["Ingrediente", "Regla asociada", "Estado"],
    )


# =========================================================
# Report generation
# =========================================================

def dataframe_to_table_data(df: pd.DataFrame) -> list[list[str]]:
    return [list(df.columns)] + df.astype(str).values.tolist()


def build_pdf_report(
    alias: str,
    edad: int,
    objetivo: str,
    presupuesto: str,
    actividad: int,
    restricciones: list[str],
    preferencias: list[str],
    contexto: str,
    score: int,
    profile: pd.DataFrame,
    plan: pd.DataFrame,
    compra: pd.DataFrame,
    checks: pd.DataFrame,
) -> bytes:
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=1.5 * cm,
        leftMargin=1.5 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm,
    )

    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="NutriTitle",
            parent=styles["Title"],
            fontSize=22,
            leading=26,
            textColor=colors.HexColor("#2F4538"),
            spaceAfter=12,
        )
    )
    styles.add(
        ParagraphStyle(
            name="NutriHeading",
            parent=styles["Heading2"],
            fontSize=14,
            leading=18,
            textColor=colors.HexColor("#2F4538"),
            spaceBefore=12,
            spaceAfter=8,
        )
    )
    styles.add(
        ParagraphStyle(
            name="NutriBody",
            parent=styles["BodyText"],
            fontSize=9,
            leading=12,
            textColor=colors.HexColor("#1C2420"),
        )
    )

    story = []
    story.append(Paragraph("🥦 NutriPrompt Report", styles["NutriTitle"]))
    story.append(Paragraph(f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles["NutriBody"]))
    story.append(Spacer(1, 10))

    summary = f"""
    <b>Perfil:</b> {alias} · {edad} años · Objetivo: {objetivo}<br/>
    <b>Presupuesto:</b> {presupuesto} · <b>Actividad:</b> {actividad}/5 ·
    <b>Compatibilidad:</b> {score}%<br/>
    <b>Restricciones:</b> {", ".join(restricciones) if restricciones else "No indicadas"}<br/>
    <b>Preferencias:</b> {", ".join(preferencias) if preferencias else "No indicadas"}<br/>
    <b>Contexto:</b> {contexto if contexto else "No indicado"}
    """
    story.append(Paragraph(summary, styles["NutriBody"]))

    def add_table(title: str, df: pd.DataFrame) -> None:
        story.append(Paragraph(title, styles["NutriHeading"]))
        data = dataframe_to_table_data(df)
        table = Table(data, repeatRows=1)
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2F4538")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 7.5),
                    ("LEADING", (0, 0), (-1, -1), 9),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#FAF7F2")),
                    ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#E4DDD0")),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 5),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                    ("TOPPADDING", (0, 0), (-1, -1), 5),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ]
            )
        )
        story.append(table)
        story.append(Spacer(1, 8))

    add_table("Resumen del perfil", profile)
    add_table("Plan semanal demo", plan)
    add_table("Compatibility Layer Validation", checks)
    add_table("Lista de compra sugerida", compra)

    story.append(Paragraph("Disclaimer", styles["NutriHeading"]))
    story.append(
        Paragraph(
            "Esta es una demo técnica con datos simulados. No sustituye asesoramiento médico, sanitario o nutricional profesional.",
            styles["NutriBody"],
        )
    )

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()


def build_markdown_report(
    alias: str,
    edad: int,
    objetivo: str,
    presupuesto: str,
    actividad: int,
    restricciones: list[str],
    preferencias: list[str],
    contexto: str,
    score: int,
    plan: pd.DataFrame,
    compra: pd.DataFrame,
    checks: pd.DataFrame,
    prompt: str,
) -> str:
    return f"""# NutriPrompt Report

Generated: {datetime.now().strftime("%d/%m/%Y %H:%M")}

## Profile

| Field | Value |
|---|---|
| Alias | {alias} |
| Age | {edad} |
| Goal | {objetivo} |
| Budget | {presupuesto} |
| Activity | {actividad}/5 |
| Restrictions | {", ".join(restricciones) if restricciones else "Not indicated"} |
| Preferences | {", ".join(preferencias) if preferencias else "Not indicated"} |
| Context | {contexto if contexto else "Not indicated"} |
| Compatibility Score | {score}% |

---

## Weekly Plan

{plan.to_markdown(index=False)}

---

## Shopping List

{compra.to_markdown(index=False)}

---

## Compatibility Layer Validation

{checks.to_markdown(index=False)}

---

## Prompt Trace

```text
{prompt.strip()}
```

---

Generated with NutriPrompt.
This is a technical demo and does not replace professional medical or nutritional advice.
"""


# =========================================================
# Tabs
# =========================================================

def intro_tab() -> None:
    st.markdown('<span class="section-label">Sección 01 · Visión del producto</span>', unsafe_allow_html=True)
    st.header("Qué demuestra esta demo")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        card("Intake", "Recoge contexto, restricciones y preferencias sin fricción.", "🏠")
    with col2:
        card("RAG", "Añade reglas nutricionales antes de generar contenido.", "🧠")
    with col3:
        card("OCR", "Simula lectura de etiquetas e ingredientes sensibles.", "📄")
    with col4:
        card("Copilot", "Explica el plan y responde con contexto limpio por perfil.", "💬")

    st.markdown("---")
    st.markdown(
        """
        **NutriPrompt no es un simple prompt.** La demo enseña producto: captura de datos,
        reglas, trazabilidad, compatibilidad, Copilot contextual y salida estructurada.
        """
    )

    st.info(
        "Recorre las pestañas de izquierda a derecha: empieza en Intake, revisa el pipeline, prueba OCR, "
        "consulta el Copilot y descarga el informe final."
    )


def intake_tab() -> None:
    st.markdown('<span class="section-label">Sección 02 · Intake inteligente</span>', unsafe_allow_html=True)
    st.header("Crea un perfil nutricional ficticio")
    st.caption("No se guardan datos personales ni se llama a APIs externas en esta demo.")

    with st.form("intake_form"):
        col1, col2, col3 = st.columns(3)

        with col1:
            alias = st.text_input(
                "¿Cómo te llaman en casa?",
                value=st.session_state["alias"],
                placeholder="Ej. La jefa del tupper, Txiki, el de 'hoy empiezo'",
            )
            edad = st.number_input(
                "Edad",
                min_value=18,
                max_value=90,
                value=st.session_state["edad"],
                placeholder="Ej. 34, aunque tu espalda diga otra cosa",
            )

        with col2:
            objetivo = st.selectbox(
                "Objetivo principal",
                OBJETIVOS,
                index=OBJETIVOS.index(st.session_state["objetivo"]) if st.session_state["objetivo"] in OBJETIVOS else None,
                placeholder="Elige tu misión nutricional",
            )
            presupuesto = st.selectbox(
                "Presupuesto semanal",
                PRESUPUESTOS,
                index=PRESUPUESTOS.index(st.session_state["presupuesto"]) if st.session_state["presupuesto"] in PRESUPUESTOS else None,
                placeholder="Desde supervivencia hasta me-lo-merezco",
            )

        with col3:
            actividad = st.slider(
                "Nivel de actividad física",
                1,
                5,
                st.session_state["actividad"],
                help="1 = sofá premium · 5 = persona que sube escaleras por gusto",
            )
            contexto = st.text_area(
                "Rutina, síntomas o contexto",
                value=st.session_state["contexto"],
                placeholder="Ej. como fuera, tengo poco tiempo, digestiones pesadas, vivo a base de café y esperanza...",
            )

        restricciones = st.multiselect(
            "Restricciones alimentarias",
            RESTRICCIONES,
            default=st.session_state["restricciones"],
            placeholder="Marca lo que haya que respetar",
        )

        preferencias = st.multiselect(
            "Preferencias",
            PREFERENCIAS,
            default=st.session_state["preferencias"],
            placeholder="Lo que haría que no abandones al tercer día",
        )

        col_a, col_b = st.columns([2, 1])
        generar = col_a.form_submit_button("🚀 Generar plan inteligente", type="primary", use_container_width=True)
        limpiar = col_b.form_submit_button("🧹 Cliente nuevo", use_container_width=True)

    if limpiar:
        reset_demo()

    if generar:
        faltan = []
        if not alias.strip():
            faltan.append("cómo te llaman en casa")
        if edad is None:
            faltan.append("edad")
        if objetivo is None:
            faltan.append("objetivo")
        if presupuesto is None:
            faltan.append("presupuesto")

        if faltan:
            st.error("Falta completar: " + ", ".join(faltan) + ". La IA aún no lee la mente.")
            return

        current_profile = f"{alias.strip().lower()}_{edad}_{objetivo}_{presupuesto}"
        if st.session_state.get("profile_id") != current_profile:
            st.session_state["chat_messages"] = []

        st.session_state["plan_generado"] = True
        st.session_state["alias"] = alias.strip()
        st.session_state["edad"] = edad
        st.session_state["objetivo"] = objetivo
        st.session_state["presupuesto"] = presupuesto
        st.session_state["actividad"] = actividad
        st.session_state["contexto"] = contexto.strip()
        st.session_state["restricciones"] = restricciones
        st.session_state["preferencias"] = preferencias
        st.session_state["profile_id"] = current_profile

        st.success("✅ Plan generado. Ve a **✅ Plan generado** para verlo.")

    if st.session_state["plan_generado"]:
        st.info("Plan demo listo. El Copilot se ha reiniciado si el perfil ha cambiado.")


def pipeline_tab() -> None:
    st.markdown('<span class="section-label">Sección 03 · Pipeline IA</span>', unsafe_allow_html=True)
    st.header("Trazabilidad del proceso")

    steps = [
        ("01", "Entrada", "Perfil, contexto, preferencias y restricciones."),
        ("02", "Normalización", "Convierte datos libres en señales útiles."),
        ("03", "RAG", "Recupera reglas nutricionales aplicables."),
        ("04", "Prompt Builder", "Construye un prompt controlado."),
        ("05", "Modelo IA", "Generación con proveedor principal."),
        ("06", "Fallback", "Proveedor alternativo si falla el primero."),
        ("07", "Compatibility Engine", "Valida reglas, restricciones e ingredientes."),
        ("08", "Salida", "Plan, explicación, compra e informe descargable."),
    ]

    cols = st.columns(4)
    for i, (num, title, desc) in enumerate(steps):
        with cols[i % 4]:
            card(f"{num} · {title}", desc, "✓")

    st.success("Pipeline: Entrada → RAG → Prompt Builder → Modelo → Compatibility Engine → Plan explicable.")


def vision_tab() -> None:
    st.markdown('<span class="section-label">Sección 04 · Vision / OCR</span>', unsafe_allow_html=True)
    st.header("Lectura de etiquetas")

    archivo = st.file_uploader(
        "Sube una etiqueta, imagen o PDF",
        type=["png", "jpg", "jpeg", "pdf"],
    )

    if archivo:
        st.success("Archivo recibido. En esta demo el análisis es simulado.")
    else:
        st.info("Puedes probar sin subir archivo. Usamos una etiqueta ficticia con ingredientes problemáticos, como la vida misma.")

    ingredients = detected_ingredients()
    st.dataframe(ingredients, use_container_width=True, hide_index=True)

    col1, col2, col3 = st.columns(3)
    col1.warning("Gluten detectado: harina de trigo")
    col2.warning("Lactosa detectada: leche en polvo")
    col3.warning("Low FODMAP: cebolla en polvo")


def dashboard_tab() -> None:
    st.markdown('<span class="section-label">Sección 05 · Panel técnico</span>', unsafe_allow_html=True)
    st.header("Arquitectura del producto")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Proveedores IA", "2", "Gemini + OpenAI")
    col2.metric("Capas pipeline", "8+", "modular")
    col3.metric("Compatibility Engine", "Activo", "RAG + reglas")
    col4.metric("Salida", "PDF + MD", "descargable")

    architecture = pd.DataFrame(
        [
            ["Backend principal", "Django"],
            ["Demo pública", "Streamlit"],
            ["RAG", "Base de conocimiento nutricional"],
            ["OCR", "Tesseract + parsing"],
            ["IA", "Gemini + OpenAI fallback"],
            ["Compatibility Engine", "Validación de reglas y restricciones"],
            ["Datos", "JSON estructurado"],
            ["Informe", "PDF + Markdown descargable"],
        ],
        columns=["Capa", "Tecnología"],
    )
    st.dataframe(architecture, use_container_width=True, hide_index=True)


def copilot_tab() -> None:
    st.markdown('<span class="section-label">Sección 06 · Copilot</span>', unsafe_allow_html=True)
    st.header("NutriPrompt Copilot")

    if not st.session_state["plan_generado"]:
        st.info("Primero genera un plan en **🏠 Intake**.")
        return

    st.caption("El chat se reinicia automáticamente si generas un nuevo perfil.")

    if "chat_messages" not in st.session_state:
        st.session_state["chat_messages"] = []

    if st.button("🧹 Limpiar chat", use_container_width=False):
        reset_chat()

    alias = st.session_state["alias"]
    objetivo = st.session_state["objetivo"]
    restricciones = st.session_state["restricciones"]
    contexto = st.session_state["contexto"]

    if not st.session_state["chat_messages"]:
        st.chat_message("assistant").write(
            f"Hola, soy NutriPrompt Copilot. Estoy trabajando con el perfil actual de **{alias}**. "
            "Puedo explicar el plan, revisar restricciones o proponer alternativas. "
            "Prometo no juzgar el cajón de snacks."
        )

    for msg in st.session_state["chat_messages"]:
        st.chat_message(msg["role"]).write(msg["content"])

    pregunta = st.chat_input("Pregunta sobre el plan nutricional...")

    if pregunta:
        st.session_state["chat_messages"].append({"role": "user", "content": pregunta})

        respuesta = (
            f"Para **{alias}**, el plan se orienta a **{objetivo}**. "
            f"Restricciones consideradas: **{', '.join(restricciones) if restricciones else 'ninguna indicada'}**. "
            f"Contexto disponible: **{contexto if contexto else 'no indicado'}**. "
            "La demo cruza reglas nutricionales, preferencias y contexto antes de proponer el plan. "
            "No sustituye una valoración profesional, pero muestra un flujo de IA explicable."
        )

        st.session_state["chat_messages"].append({"role": "assistant", "content": respuesta})
        st.rerun()


def plan_tab() -> None:
    st.markdown('<span class="section-label">Sección 07 · Resultado final</span>', unsafe_allow_html=True)

    if not st.session_state["plan_generado"]:
        st.info("Primero genera un plan desde **🏠 Intake**.")
        return

    alias = st.session_state["alias"]
    edad = st.session_state["edad"]
    objetivo = st.session_state["objetivo"]
    presupuesto = st.session_state["presupuesto"]
    actividad = st.session_state["actividad"]
    restricciones = st.session_state["restricciones"]
    preferencias = st.session_state["preferencias"]
    contexto = st.session_state["contexto"]

    st.success("✅ Plan generado correctamente")
    st.header(f"Plan nutricional demo para {alias}")

    score = compatibility_score()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        kpi("Edad", edad)
    with col2:
        kpi("Objetivo", objetivo)
    with col3:
        kpi("Presupuesto", presupuesto)
    with col4:
        kpi("Compatibilidad", f"{score}%")

    profile = pd.DataFrame(
        [
            ["Alias", alias],
            ["Edad", edad],
            ["Objetivo", objetivo],
            ["Presupuesto", presupuesto],
            ["Actividad física", f"{actividad}/5"],
            ["Restricciones", ", ".join(restricciones) if restricciones else "No indicadas"],
            ["Preferencias", ", ".join(preferencias) if preferencias else "No indicadas"],
            ["Contexto", contexto if contexto else "No indicado"],
        ],
        columns=["Campo", "Valor"],
    )

    plan = build_plan()
    compra = shopping_list()
    checks = compatibility_checks()

    st.subheader("Resumen del perfil")
    st.dataframe(profile, use_container_width=True, hide_index=True)

    st.subheader("Plan semanal demo")
    st.dataframe(plan, use_container_width=True, hide_index=True)

    st.subheader("Compatibility Layer Validation")
    st.dataframe(checks, use_container_width=True, hide_index=True)

    st.subheader("Lista de compra sugerida")
    st.dataframe(compra, use_container_width=True, hide_index=True)

    col_rag, col_comp = st.columns(2)

    with col_rag:
        st.markdown("#### Contexto recuperado con RAG")
        st.markdown(
            """
            ✅ Low FODMAP: revisar cebolla, ajo, trigo, manzana y algunas legumbres.

            ✅ Sin lactosa: evitar lácteos convencionales y revisar procesados.

            ✅ Planificación: priorizar platos repetibles, sencillos y realistas.
            """
        )

    with col_comp:
        st.markdown("#### Análisis de compatibilidad")
        st.warning("Revisar yogures, quesos, salsas y procesados por posible lactosa oculta.")
        st.warning("Evitar cebolla en polvo y harina de trigo si aplican reglas Low FODMAP o sin gluten.")

    prompt = f"""
Actúa como asistente de organización semanal de comidas.

Perfil:
- Alias: {alias}
- Edad: {edad}
- Objetivo: {objetivo}
- Presupuesto: {presupuesto}
- Actividad física: {actividad}/5
- Restricciones: {", ".join(restricciones) if restricciones else "No indicadas"}
- Preferencias: {", ".join(preferencias) if preferencias else "No indicadas"}
- Contexto: {contexto if contexto else "No indicado"}

Prioriza reglas nutricionales recuperadas por RAG.
Valida las recomendaciones con el Compatibility Engine.
Evita afirmaciones médicas.
Devuelve una salida estructurada, revisable y útil.
"""

    with st.expander("Ver prompt generado"):
        st.code(prompt, language="text")

    safe_alias = clean_filename(alias)

    md_report = build_markdown_report(
        alias=alias,
        edad=edad,
        objetivo=objetivo,
        presupuesto=presupuesto,
        actividad=actividad,
        restricciones=restricciones,
        preferencias=preferencias,
        contexto=contexto,
        score=score,
        plan=plan,
        compra=compra,
        checks=checks,
        prompt=prompt,
    )

    pdf_report = build_pdf_report(
        alias=alias,
        edad=edad,
        objetivo=objetivo,
        presupuesto=presupuesto,
        actividad=actividad,
        restricciones=restricciones,
        preferencias=preferencias,
        contexto=contexto,
        score=score,
        profile=profile,
        plan=plan,
        compra=compra,
        checks=checks,
    )

    st.subheader("Descargas")
    col_pdf, col_md = st.columns(2)

    with col_pdf:
        st.download_button(
            "📄 Descargar PDF profesional",
            data=pdf_report,
            file_name=f"nutriprompt_report_{safe_alias}.pdf",
            mime="application/pdf",
            use_container_width=True,
        )

    with col_md:
        st.download_button(
            "📥 Descargar Markdown técnico",
            data=md_report,
            file_name=f"nutriprompt_report_{safe_alias}.md",
            mime="text/markdown",
            use_container_width=True,
        )


# =========================================================
# Main
# =========================================================

def main() -> None:
    init_state()
    render_header()

    tabs = st.tabs(
        [
            "👋 Inicio",
            "🏠 Intake",
            "🧠 Pipeline IA",
            "📄 Vision / OCR",
            "📊 Panel técnico",
            "💬 Copilot",
            "✅ Plan generado",
        ]
    )

    with tabs[0]:
        intro_tab()
    with tabs[1]:
        intake_tab()
    with tabs[2]:
        pipeline_tab()
    with tabs[3]:
        vision_tab()
    with tabs[4]:
        dashboard_tab()
    with tabs[5]:
        copilot_tab()
    with tabs[6]:
        plan_tab()

    if st.button("🧹 Reset demo completo"):
        reset_demo()

    st.markdown(
        '<div class="footer">NutriPrompt · Demo técnica con datos simulados · Construido con Streamlit</div>',
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
