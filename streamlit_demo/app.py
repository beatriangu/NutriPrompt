from __future__ import annotations

import pandas as pd
import streamlit as st


st.set_page_config(
    page_title="NutriPrompt · Demo IA",
    page_icon="🥦",
    layout="wide",
)


# =========================================================
# Estado limpio
# =========================================================

DEFAULT_STATE = {
    "plan_generated": False,
    "alias": "",
    "age": None,
    "goal": None,
    "budget": None,
    "activity": 3,
    "context": "",
    "restrictions": [],
    "preferences": [],
    "chat_messages": [],
}


def init_state() -> None:
    for key, value in DEFAULT_STATE.items():
        if key not in st.session_state:
            st.session_state[key] = value


def reset_demo() -> None:
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()


# =========================================================
# Datos demo
# =========================================================

def build_demo_plan() -> pd.DataFrame:
    restrictions = st.session_state.get("restrictions", [])

    if "Vegano" in restrictions:
        meals = [
            ["Lunes", "Avena con plátano y chía", "Bowl de arroz con tofu y verduras suaves", "Crema de calabacín con garbanzos"],
            ["Martes", "Yogur vegetal con fruta", "Quinoa con verduras y proteína vegetal", "Tortilla vegana de harina de garbanzo"],
            ["Miércoles", "Tostadas sin gluten con aguacate", "Arroz con tofu marinado", "Sopa de verduras y semillas"],
            ["Jueves", "Batido vegetal con fruta", "Patata cocida con verduras y hummus suave", "Salteado de tofu con calabacín"],
            ["Viernes", "Pudding de chía", "Tupper de arroz con verduras", "Cena ligera de crema vegetal"],
        ]
    else:
        meals = [
            ["Lunes", "Yogur sin lactosa con fruta", "Arroz con pollo y verduras suaves", "Tortilla con espinacas"],
            ["Martes", "Avena sin gluten con plátano", "Pasta sin gluten con pavo", "Crema de verduras y huevo"],
            ["Miércoles", "Tostadas sin gluten", "Quinoa con pollo", "Pescado con patata cocida"],
            ["Jueves", "Batido suave de fruta", "Bowl de arroz y verduras", "Revuelto con calabacín"],
            ["Viernes", "Yogur sin lactosa con nueces", "Tupper de pollo y arroz", "Cena ligera con tortilla"],
        ]

    return pd.DataFrame(meals, columns=["Día", "Desayuno", "Comida", "Cena"])


def get_detected_ingredients() -> list[str]:
    return [
        "Harina de trigo",
        "Leche en polvo",
        "Cebolla en polvo",
        "Azúcar",
        "Sal",
    ]


# =========================================================
# UI helpers
# =========================================================

def card(title: str, body: str, icon: str = "✅") -> None:
    st.markdown(
        f"""
        <div style="
            padding: 1.1rem;
            border: 1px solid #e5e7eb;
            border-radius: 1rem;
            background: #ffffff;
            min-height: 135px;
            box-shadow: 0 8px 24px rgba(15, 23, 42, 0.04);
        ">
            <div style="font-size:1.8rem;">{icon}</div>
            <h4 style="margin:.4rem 0 .3rem 0;">{title}</h4>
            <p style="color:#64748b; margin:0;">{body}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def show_header() -> None:
    st.markdown(
        """
        <h1 style="font-size:3rem; margin-bottom:.2rem;">🥦 NutriPrompt</h1>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div style="
            padding: 1.6rem;
            border-radius: 1.2rem;
            background: linear-gradient(120deg, #eef7ff, #f2fff4);
            border: 1px solid #d8eadf;
            margin-bottom: 1rem;
        ">
            <h3 style="margin-bottom:.5rem;">Demo pública de inteligencia nutricional con IA</h3>
            <p style="font-size:1rem; margin-bottom:1rem;">
                Formulario inteligente · RAG · OCR · análisis de compatibilidad · orquestación multi-modelo
            </p>
            <span style="background:#f4f6f8;padding:.4rem .8rem;border-radius:999px;margin-right:.4rem;">Producto principal en Django</span>
            <span style="background:#f4f6f8;padding:.4rem .8rem;border-radius:999px;margin-right:.4rem;">Demo pública en Streamlit</span>
            <span style="background:#f4f6f8;padding:.4rem .8rem;border-radius:999px;margin-right:.4rem;">RAG explicado</span>
            <span style="background:#f4f6f8;padding:.4rem .8rem;border-radius:999px;">OCR simulado</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.warning(
        "Demo técnica. No sustituye asesoramiento médico, sanitario o nutricional profesional. "
        "La IA no conoce tu nevera ni tus dramas digestivos reales."
    )


def show_demo_status() -> None:
    if st.session_state.get("plan_generated"):
        st.success("✅ Plan demo generado. Puedes revisarlo en **✅ Plan generado**.")
    else:
        st.info("Empieza en **🏠 Intake**, rellena el perfil ficticio y genera el plan.")


# =========================================================
# Tabs
# =========================================================

def intro_tab() -> None:
    st.header("Qué puedes probar en esta demo")

    st.markdown(
        """
        NutriPrompt muestra cómo una aplicación de IA puede transformar datos de entrada en una salida
        estructurada, explicable y revisable. No es magia: es producto, reglas y prompts bien pensados.
        """
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        card("1. Intake", "Recoge objetivos, restricciones, preferencias y contexto real.", "🏠")

    with col2:
        card("2. Flujo IA", "Explica cómo se combinan RAG, prompt builder y fallback.", "🧠")

    with col3:
        card("3. Vision / OCR", "Simula lectura de etiquetas e ingredientes conflictivos.", "📄")

    with col4:
        card("4. Plan", "Genera una planificación semanal demo y revisable.", "✅")

    st.markdown("---")

    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown(
            """
            ### Producto principal: Django

            - Arquitectura real
            - Servicios separados
            - Tests
            - PDF
            - RAG
            - OCR
            - Fallback Gemini/OpenAI
            """
        )

    with col_b:
        st.markdown(
            """
            ### Demo pública: Streamlit

            - Fácil de probar
            - Sin instalación
            - Pensada para LinkedIn
            - Explica el flujo
            - Reduce fricción
            - Permite recibir feedback
            """
        )


def intake_tab() -> None:
    st.header("Smart Nutrition Intake")
    st.caption("Completa un perfil ficticio. La demo no guarda datos personales ni llama a APIs externas.")

    with st.form("intake_form", clear_on_submit=False):
        col1, col2, col3 = st.columns(3)

        with col1:
            alias = st.text_input(
                "¿Cómo te llaman en casa?",
                value=st.session_state.get("alias", ""),
                placeholder="Ej. La jefa del tupper, Txiki, Mamá tengo hambre..."
            )

            age = st.number_input(
                "Edad",
                min_value=18,
                max_value=90,
                value=st.session_state.get("age"),
                placeholder="Ej. 34, aunque tu espalda diga 57"
            )

        with col2:
            goals = [
                "Mejora digestiva",
                "Organizar comidas",
                "Comer más equilibrado",
                "Ganar energía",
            ]

            current_goal = st.session_state.get("goal")
            goal_index = goals.index(current_goal) if current_goal in goals else None

            goal = st.selectbox(
                "Objetivo principal",
                goals,
                index=goal_index,
                placeholder="Elige tu misión nutricional"
            )

            budgets = ["Ajustado", "Medio", "Flexible"]
            current_budget = st.session_state.get("budget")
            budget_index = budgets.index(current_budget) if current_budget in budgets else None

            budget = st.selectbox(
                "Presupuesto semanal",
                budgets,
                index=budget_index,
                placeholder="Desde supervivencia hasta me-lo-merezco"
            )

        with col3:
            activity = st.slider(
                "Nivel de actividad física",
                min_value=1,
                max_value=5,
                value=st.session_state.get("activity", 3),
                help="1 = sofá premium · 5 = persona que sube escaleras por gusto"
            )

            context = st.text_area(
                "Síntomas, rutina o contexto",
                value=st.session_state.get("context", ""),
                placeholder="Ej. como fuera, tengo poco tiempo, digestiones pesadas, vivo a base de café y esperanza..."
            )

        restrictions = st.multiselect(
            "Restricciones alimentarias",
            ["Low FODMAP", "Sin lactosa", "Sin gluten", "Vegetariano", "Vegano"],
            default=st.session_state.get("restrictions", []),
            placeholder="Marca lo que haya que respetar"
        )

        preferences = st.multiselect(
            "Preferencias",
            ["Recetas rápidas", "Batch cooking", "Tupper", "Cenas ligeras", "Presupuesto ajustado"],
            default=st.session_state.get("preferences", []),
            placeholder="Lo que haría que no abandones al tercer día"
        )

        st.markdown("### Antes de generar")
        st.caption(
            "La salida se genera en modo demo. Flujo: datos → reglas → compatibilidad → plan estructurado."
        )

        col_button, col_reset = st.columns([2, 1])

        with col_button:
            submitted = st.form_submit_button("🚀 Generar plan inteligente", use_container_width=True)

        with col_reset:
            reset_clicked = st.form_submit_button("🧹 Cliente nuevo", use_container_width=True)

    if reset_clicked:
        reset_demo()

    if submitted:
        missing = []

        if not alias.strip():
            missing.append("cómo te llaman en casa")
        if age is None:
            missing.append("edad")
        if goal is None:
            missing.append("objetivo")
        if budget is None:
            missing.append("presupuesto")

        if missing:
            st.error("Falta completar: " + ", ".join(missing) + ". La IA no adivina tanto, todavía.")
            return

        st.session_state["plan_generated"] = True
        st.session_state["alias"] = alias.strip()
        st.session_state["age"] = age
        st.session_state["goal"] = goal
        st.session_state["budget"] = budget
        st.session_state["activity"] = activity
        st.session_state["context"] = context.strip()
        st.session_state["restrictions"] = restrictions
        st.session_state["preferences"] = preferences
        st.session_state["chat_messages"] = []

        st.success("✅ Plan generado. Abre la pestaña **✅ Plan generado** para verlo.")

    show_demo_status()


def workflow_tab() -> None:
    st.header("Flujo de IA explicado")
    st.caption("NutriPrompt no lanza el formulario sin control al modelo. Primero ordena, contextualiza y valida.")

    steps = [
        ("1. Entrada", "Objetivos, restricciones, preferencias y contexto.", "🏠"),
        ("2. Perfil", "Normalización de datos y señales relevantes.", "👤"),
        ("3. RAG", "Búsqueda de reglas nutricionales aplicables.", "🧠"),
        ("4. Prompt Builder", "Construcción de un prompt controlado.", "🧩"),
        ("5. Modelo principal", "Generación con proveedor principal.", "🤖"),
        ("6. Fallback", "Proveedor alternativo si falla el primero.", "🔁"),
        ("7. Reglas", "Validación de compatibilidad.", "🛡️"),
        ("8. Salida", "Plan estructurado, lista y PDF.", "📄"),
    ]

    cols = st.columns(4)

    for index, (title, description, icon) in enumerate(steps):
        with cols[index % 4]:
            card(title, description, icon)

    st.success("Orquestación resiliente: Gemini → OpenAI fallback → salida estructurada en modo demo.")


def vision_tab() -> None:
    st.header("Vision / OCR")
    st.caption("Simulación de análisis de etiqueta, despensa o PDF nutricional.")

    uploaded_file = st.file_uploader(
        "Sube una etiqueta, imagen de despensa o PDF",
        type=["png", "jpg", "jpeg", "pdf"],
    )

    if uploaded_file:
        st.success("Archivo recibido correctamente. En esta demo el análisis es simulado.")
    else:
        st.info("Puedes probar sin subir archivo. Usamos una etiqueta ficticia, que también tiene sus secretos.")

    st.markdown("### Ingredientes detectados")

    ingredients = get_detected_ingredients()
    st.code("\n".join(f"- {ingredient}" for ingredient in ingredients), language="text")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.warning("Gluten detectado: harina de trigo")

    with col2:
        st.warning("Lactosa detectada: leche en polvo")

    with col3:
        st.warning("Alerta Low FODMAP: cebolla en polvo")

    st.info("NutriPrompt cruza OCR, reglas nutricionales y restricciones antes de generar el resultado.")


def dashboard_tab() -> None:
    st.header("Panel técnico")
    st.caption("Resumen visual de la arquitectura que hay detrás del producto.")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Proveedores IA", "2", "Gemini + OpenAI")
    col2.metric("Tests", "17", "OK")
    col3.metric("Capas del flujo", "8+", "modular")
    col4.metric("Salida", "PDF", "descargable")

    st.subheader("Arquitectura")

    architecture = pd.DataFrame(
        [
            ["Backend principal", "Django"],
            ["Lenguaje", "Python"],
            ["Orquestación IA", "Gemini + OpenAI fallback"],
            ["RAG", "Base de conocimiento nutricional"],
            ["OCR", "Tesseract + parsing"],
            ["Datos", "JSON"],
            ["PDF", "WeasyPrint"],
            ["Demo pública", "Streamlit"],
        ],
        columns=["Capa", "Tecnología"],
    )

    st.dataframe(architecture, use_container_width=True, hide_index=True)

    st.subheader("Pipeline extremo a extremo")
    st.info("Entrada → Perfil → RAG → Prompt Builder → Modelo IA → Fallback → Compatibilidad → Plan → PDF")


def copilot_tab() -> None:
    st.header("NutriPrompt Copilot")
    st.caption("Chat demo. Se limpia al generar un nuevo perfil o al pulsar limpiar chat.")

    if "chat_messages" not in st.session_state:
        st.session_state["chat_messages"] = []

    col_a, col_b = st.columns([3, 1])

    with col_b:
        if st.button("🧹 Limpiar chat", use_container_width=True):
            st.session_state["chat_messages"] = []
            st.rerun()

    if not st.session_state.get("plan_generated"):
        st.info("Genera primero un plan en **🏠 Intake** para que el Copilot tenga contexto.")
        return

    alias = st.session_state.get("alias", "esta persona")
    goal = st.session_state.get("goal", "objetivo no indicado")
    restrictions = st.session_state.get("restrictions", [])

    if not st.session_state["chat_messages"]:
        st.chat_message("assistant").write(
            f"Hola, soy NutriPrompt Copilot. Puedo explicar el plan de {alias}, revisar restricciones "
            "o detectar posibles incompatibilidades. Prometo no juzgar el batch cooking abandonado."
        )

    for message in st.session_state["chat_messages"]:
        st.chat_message(message["role"]).write(message["content"])

    question = st.chat_input("Pregunta sobre el plan nutricional...")

    if question:
        st.session_state["chat_messages"].append(
            {"role": "user", "content": question}
        )

        answer = (
            f"Para {alias}, el plan se orienta a **{goal}**. "
            f"Las restricciones consideradas son: **{', '.join(restrictions) if restrictions else 'ninguna indicada'}**. "
            "La demo cruza reglas nutricionales, preferencias y contexto antes de proponer el plan. "
            "Esto no sustituye una valoración profesional, pero sí muestra cómo sería el flujo de IA explicable."
        )

        st.session_state["chat_messages"].append(
            {"role": "assistant", "content": answer}
        )

        st.rerun()


def plan_tab() -> None:
    if not st.session_state.get("plan_generated"):
        st.info("Primero genera un plan desde **🏠 Intake**.")
        return

    alias = st.session_state.get("alias", "Persona demo")
    age = st.session_state.get("age")
    goal = st.session_state.get("goal", "No indicado")
    budget = st.session_state.get("budget", "No indicado")
    activity = st.session_state.get("activity", 3)
    restrictions = st.session_state.get("restrictions", [])
    preferences = st.session_state.get("preferences", [])
    context = st.session_state.get("context", "")

    st.success("✅ Plan generado correctamente")
    st.header(f"Plan nutricional demo para {alias}")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Edad", age)
    col2.metric("Objetivo", goal)
    col3.metric("Presupuesto", budget)
    col4.metric("Actividad", f"{activity}/5")

    st.markdown("### Resumen del perfil")

    profile = pd.DataFrame(
        [
            ["Alias", alias],
            ["Edad", age],
            ["Objetivo", goal],
            ["Presupuesto", budget],
            ["Actividad física", f"{activity}/5"],
            ["Restricciones", ", ".join(restrictions) if restrictions else "No indicadas"],
            ["Preferencias", ", ".join(preferences) if preferences else "No indicadas"],
            ["Contexto", context if context else "No indicado"],
        ],
        columns=["Campo", "Valor"],
    )

    st.dataframe(profile, use_container_width=True, hide_index=True)

    st.markdown("### Plan semanal demo")

    plan = build_demo_plan()
    st.dataframe(plan, use_container_width=True, hide_index=True)

    col_rag, col_compatibility = st.columns(2)

    with col_rag:
        st.subheader("Contexto recuperado con RAG")
        st.markdown(
            """
            ✅ Regla Low FODMAP: revisar cebolla, ajo, trigo, manzana y algunas legumbres.

            ✅ Regla sin lactosa: evitar lácteos convencionales y priorizar alternativas compatibles.

            ✅ Regla de planificación: priorizar comidas sencillas, repetibles y realistas.
            """
        )

    with col_compatibility:
        st.subheader("Análisis de compatibilidad")
        st.warning("Revisar yogures, quesos, salsas y procesados por posible lactosa oculta.")
        st.warning("Evitar cebolla en polvo y harina de trigo si aplican reglas Low FODMAP o sin gluten.")

    with st.expander("Ver prompt generado"):
        st.code(
            f"""
Actúa como asistente de organización semanal de comidas.

Perfil:
- Alias: {alias}
- Edad: {age}
- Objetivo: {goal}
- Presupuesto: {budget}
- Actividad física: {activity}/5
- Restricciones: {", ".join(restrictions) if restrictions else "No indicadas"}
- Preferencias: {", ".join(preferences) if preferences else "No indicadas"}
- Contexto: {context if context else "No indicado"}

Prioriza las reglas nutricionales recuperadas por RAG.
Evita afirmaciones médicas.
Devuelve una salida estructurada, revisable y útil.
            """,
            language="text",
        )


# =========================================================
# Main
# =========================================================

def main() -> None:
    init_state()
    show_header()

    tabs = st.tabs(
        [
            "👋 Inicio",
            "🏠 Intake",
            "🧠 Flujo IA",
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
        workflow_tab()

    with tabs[3]:
        vision_tab()

    with tabs[4]:
        dashboard_tab()

    with tabs[5]:
        copilot_tab()

    with tabs[6]:
        plan_tab()


if __name__ == "__main__":
    main()