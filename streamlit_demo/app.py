from __future__ import annotations

import io
from datetime import datetime

import pandas as pd
import streamlit as st


st.set_page_config(
    page_title="NutriPrompt · Demo IA",
    page_icon="🥦",
    layout="wide",
)


CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:wght@500;600;700&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

.stApp { background-color: #FAF7F2; }
html, body, [class*="css"] { font-family: 'Inter', sans-serif; color: #1C2420; }
h1, h2, h3 { font-family: 'Fraunces', serif; color: #2F4538; }
code, pre { font-family: 'JetBrains Mono', monospace !important; }

.dossier-header {
    background: #FFFFFF;
    border: 1px solid #E4DDD0;
    border-radius: 8px;
    padding: 2rem 2.2rem;
    margin-bottom: 1.2rem;
    position: relative;
    box-shadow: 0 8px 24px rgba(47,69,56,.05);
}
.dossier-header::before {
    content: "";
    position: absolute;
    left: 0; top: 0;
    width: 6px; height: 100%;
    background: #C76F4D;
    border-radius: 8px 0 0 8px;
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
    font-size: 2.7rem;
    font-weight: 700;
    color: #2F4538;
    margin: .4rem 0 .2rem 0;
}
.subtitle {
    color: #4A6354;
    max-width: 70ch;
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
}
.card {
    background:#FFFFFF;
    border:1px solid #E4DDD0;
    border-radius:8px;
    padding:1.1rem;
    min-height:130px;
}
.card-title {
    font-family:'Fraunces', serif;
    color:#2F4538;
    font-size:1.1rem;
    font-weight:600;
}
.card-body { color:#4A6354; font-size:.9rem; }
.section-label {
    font-family:'JetBrains Mono', monospace;
    font-size:.72rem;
    letter-spacing:.12em;
    text-transform:uppercase;
    color:#C76F4D;
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
</style>
"""


OBJETIVOS = ["Mejora digestiva", "Organizar comidas", "Comer más equilibrado", "Ganar energía"]
PRESUPUESTOS = ["Ajustado", "Medio", "Flexible"]
RESTRICCIONES = ["Low FODMAP", "Sin lactosa", "Sin gluten", "Vegetariano", "Vegano"]
PREFERENCIAS = ["Recetas rápidas", "Batch cooking", "Tupper", "Cenas ligeras", "Presupuesto ajustado"]


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
}


def init_state() -> None:
    for key, value in DEFAULT_STATE.items():
        st.session_state.setdefault(key, value)


def reset_demo() -> None:
    st.session_state.clear()
    st.rerun()


def render_header() -> None:
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
    st.markdown(
        """
        <div class="dossier-header">
            <div class="eyebrow">Expediente · NutriPrompt AI · Demo pública</div>
            <div class="title">🥦 NutriPrompt</div>
            <p class="subtitle">
                Plataforma de inteligencia nutricional que combina intake inteligente, reglas,
                RAG, OCR y orquestación multi-modelo para generar planes alimentarios explicables.
            </p>
            <span class="tag">Producto Django</span>
            <span class="tag">Demo Streamlit</span>
            <span class="tag">RAG explicado</span>
            <span class="tag">OCR simulado</span>
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


def build_plan() -> pd.DataFrame:
    vegan = "Vegano" in st.session_state.get("restricciones", [])

    if vegan:
        meals = [
            ["Lunes", "Avena con plátano y chía", "Bowl de arroz con tofu", "Crema de calabacín con garbanzos"],
            ["Martes", "Yogur vegetal con fruta", "Quinoa con verduras", "Tortilla vegana de garbanzo"],
            ["Miércoles", "Tostadas con aguacate", "Arroz con tofu marinado", "Sopa de verduras"],
            ["Jueves", "Batido vegetal", "Patata cocida con hummus", "Salteado de tofu"],
            ["Viernes", "Pudding de chía", "Tupper de arroz y verduras", "Crema vegetal"],
        ]
    else:
        meals = [
            ["Lunes", "Yogur sin lactosa con fruta", "Arroz con pollo y verduras suaves", "Tortilla con espinacas"],
            ["Martes", "Avena con plátano", "Pasta con pavo", "Crema de verduras y huevo"],
            ["Miércoles", "Tostadas con aceite", "Quinoa con pollo", "Pescado con patata cocida"],
            ["Jueves", "Batido suave de fruta", "Bowl de arroz y verduras", "Revuelto con calabacín"],
            ["Viernes", "Yogur sin lactosa con nueces", "Tupper de pollo y arroz", "Cena ligera con tortilla"],
        ]

    return pd.DataFrame(meals, columns=["Día", "Desayuno", "Comida", "Cena"])


def shopping_list() -> pd.DataFrame:
    items = [
        ["Proteínas", "Pollo / tofu / huevo / pescado"],
        ["Base", "Arroz, quinoa, patata, avena"],
        ["Verduras", "Calabacín, espinacas, zanahoria"],
        ["Desayunos", "Yogur sin lactosa o vegetal, fruta, chía"],
        ["Extras", "Nueces, aceite de oliva, semillas"],
    ]
    return pd.DataFrame(items, columns=["Categoría", "Compra sugerida"])


def compatibility_score() -> int:
    score = 92
    if not st.session_state.get("restricciones"):
        score -= 5
    if not st.session_state.get("contexto"):
        score -= 4
    if "Low FODMAP" in st.session_state.get("restricciones", []):
        score -= 2
    return max(score, 75)


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
        card("Copilot", "Explica el plan y responde con contexto.", "💬")

    st.markdown("---")
    st.markdown(
        """
        **NutriPrompt no es un simple prompt.** La demo enseña producto: captura de datos,
        reglas, trazabilidad, compatibilidad y salida estructurada.
        """
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
                placeholder="Ej. La jefa del tupper, Txiki, el de 'hoy empiezo'"
            )
            edad = st.number_input(
                "Edad",
                min_value=18,
                max_value=90,
                value=st.session_state["edad"],
                placeholder="Ej. 34, aunque tu espalda diga otra cosa"
            )

        with col2:
            objetivo = st.selectbox(
                "Objetivo principal",
                OBJETIVOS,
                index=OBJETIVOS.index(st.session_state["objetivo"]) if st.session_state["objetivo"] in OBJETIVOS else None,
                placeholder="Elige tu misión nutricional"
            )
            presupuesto = st.selectbox(
                "Presupuesto semanal",
                PRESUPUESTOS,
                index=PRESUPUESTOS.index(st.session_state["presupuesto"]) if st.session_state["presupuesto"] in PRESUPUESTOS else None,
                placeholder="Desde supervivencia hasta me-lo-merezco"
            )

        with col3:
            actividad = st.slider(
                "Nivel de actividad física",
                1,
                5,
                st.session_state["actividad"],
                help="1 = sofá premium · 5 = persona que sube escaleras por gusto"
            )
            contexto = st.text_area(
                "Rutina, síntomas o contexto",
                value=st.session_state["contexto"],
                placeholder="Ej. como fuera, tengo poco tiempo, digestiones pesadas, vivo a base de café y esperanza..."
            )

        restricciones = st.multiselect(
            "Restricciones alimentarias",
            RESTRICCIONES,
            default=st.session_state["restricciones"],
            placeholder="Marca lo que haya que respetar"
        )

        preferencias = st.multiselect(
            "Preferencias",
            PREFERENCIAS,
            default=st.session_state["preferencias"],
            placeholder="Lo que haría que no abandones al tercer día"
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

        st.session_state["plan_generado"] = True
        st.session_state["alias"] = alias.strip()
        st.session_state["edad"] = edad
        st.session_state["objetivo"] = objetivo
        st.session_state["presupuesto"] = presupuesto
        st.session_state["actividad"] = actividad
        st.session_state["contexto"] = contexto.strip()
        st.session_state["restricciones"] = restricciones
        st.session_state["preferencias"] = preferencias
        st.session_state["chat_messages"] = []

        st.success("✅ Plan generado. Ve a **✅ Plan generado** para verlo.")

    if st.session_state["plan_generado"]:
        st.info("Plan demo listo. El Copilot también se ha reiniciado para este perfil.")


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
        ("07", "Reglas", "Validación de compatibilidad."),
        ("08", "Salida", "Plan, explicación, compra y PDF."),
    ]

    cols = st.columns(4)
    for i, (num, title, desc) in enumerate(steps):
        with cols[i % 4]:
            card(f"{num} · {title}", desc, "✓")

    st.success("Pipeline: Entrada → RAG → Prompt Builder → Modelo → Validación → Plan explicable.")


def vision_tab() -> None:
    st.markdown('<span class="section-label">Sección 04 · Vision / OCR</span>', unsafe_allow_html=True)
    st.header("Lectura de etiquetas")
    archivo = st.file_uploader("Sube una etiqueta, imagen o PDF", type=["png", "jpg", "jpeg", "pdf"])

    if archivo:
        st.success("Archivo recibido. En esta demo el análisis es simulado.")
    else:
        st.info("Puedes probar sin subir archivo. Usamos una etiqueta ficticia con ingredientes problemáticos, como la vida misma.")

    st.code(
        "- Harina de trigo\n- Leche en polvo\n- Cebolla en polvo\n- Azúcar\n- Sal",
        language="text"
    )

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
    col3.metric("Compatibilidad", "Reglas", "RAG + validación")
    col4.metric("Salida", "PDF", "descargable")

    architecture = pd.DataFrame(
        [
            ["Backend principal", "Django"],
            ["Demo pública", "Streamlit"],
            ["RAG", "Base de conocimiento nutricional"],
            ["OCR", "Tesseract + parsing"],
            ["IA", "Gemini + OpenAI fallback"],
            ["Datos", "JSON estructurado"],
            ["PDF", "WeasyPrint"],
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

    if st.button("🧹 Limpiar chat", use_container_width=False):
        st.session_state["chat_messages"] = []
        st.rerun()

    alias = st.session_state["alias"]
    objetivo = st.session_state["objetivo"]
    restricciones = st.session_state["restricciones"]

    if not st.session_state["chat_messages"]:
        st.chat_message("assistant").write(
            f"Hola, soy NutriPrompt Copilot. Puedo explicar el plan de {alias}, revisar restricciones "
            "o proponer alternativas. Prometo no juzgar el cajón de snacks."
        )

    for msg in st.session_state["chat_messages"]:
        st.chat_message(msg["role"]).write(msg["content"])

    pregunta = st.chat_input("Pregunta sobre el plan nutricional...")

    if pregunta:
        st.session_state["chat_messages"].append({"role": "user", "content": pregunta})

        respuesta = (
            f"Para **{alias}**, el plan se orienta a **{objetivo}**. "
            f"Restricciones consideradas: **{', '.join(restricciones) if restricciones else 'ninguna indicada'}**. "
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
    col1.metric("Edad", edad)
    col2.metric("Objetivo", objetivo)
    col3.metric("Presupuesto", presupuesto)
    col4.metric("Compatibilidad", f"{score}%")

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

    st.subheader("Resumen del perfil")
    st.dataframe(profile, use_container_width=True, hide_index=True)

    st.subheader("Plan semanal demo")
    plan = build_plan()
    st.dataframe(plan, use_container_width=True, hide_index=True)

    st.subheader("Lista de compra sugerida")
    compra = shopping_list()
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
Evita afirmaciones médicas.
Devuelve una salida estructurada, revisable y útil.
"""

    with st.expander("Ver prompt generado"):
        st.code(prompt, language="text")

    informe = io.StringIO()
    informe.write(f"NutriPrompt · Informe demo\n")
    informe.write(f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n")
    informe.write(profile.to_string(index=False))
    informe.write("\n\nPLAN SEMANAL\n")
    informe.write(plan.to_string(index=False))
    informe.write("\n\nLISTA DE COMPRA\n")
    informe.write(compra.to_string(index=False))

    st.download_button(
        "📥 Descargar informe demo",
        data=informe.getvalue(),
        file_name=f"nutriprompt_demo_{alias.replace(' ', '_').lower()}.txt",
        mime="text/plain",
        use_container_width=True,
    )


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

    st.markdown(
        '<div class="footer">NutriPrompt · Demo técnica con datos simulados · Construido con Streamlit</div>',
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()