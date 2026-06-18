from __future__ import annotations

import pandas as pd
import streamlit as st


st.set_page_config(
    page_title="NutriPrompt Demo",
    page_icon="🥦",
    layout="wide",
)


def init_state() -> None:
    defaults = {
        "plan_generated": False,
        "name": "Laura",
        "goal": "Mejora digestiva",
        "budget": "Medio",
        "activity": 3,
        "context": "Digestiones pesadas por la tarde",
        "restrictions": ["Low FODMAP", "Sin lactosa"],
        "preferences": ["Recetas rápidas", "Batch cooking"],
    }

    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def reset_demo() -> None:
    st.session_state.clear()
    st.rerun()


def build_demo_plan() -> pd.DataFrame:
    name = st.session_state.get("name", "Laura")
    restrictions = ", ".join(st.session_state.get("restrictions", [])) or "sin restricciones específicas"

    return pd.DataFrame(
        [
            ["Lunes", "Yogur sin lactosa con fruta", "Arroz con pollo y verduras suaves", "Tortilla con espinacas"],
            ["Martes", "Avena sin gluten con plátano", "Pasta sin gluten con pavo", "Crema de verduras y huevo"],
            ["Miércoles", "Tostadas sin gluten", "Quinoa con pollo", "Pescado con patata cocida"],
            ["Jueves", "Batido suave de fruta", "Bowl de arroz y verduras", "Revuelto con calabacín"],
            ["Viernes", "Yogur sin lactosa con nueces", "Tupper de pollo y arroz", "Cena ligera con tortilla"],
        ],
        columns=["Día", "Desayuno", "Comida", "Cena"],
    )


def show_header() -> None:
    st.title("🥦 NutriPrompt")

    st.markdown(
        """
        <div style="
            padding: 1.6rem;
            border-radius: 1.2rem;
            background: linear-gradient(120deg, #eef7ff, #f2fff4);
            border: 1px solid #d8eadf;
            margin-bottom: 1rem;
        ">
            <h3 style="margin-bottom:.5rem;">AI-powered nutrition intelligence platform</h3>
            <p style="font-size:1rem; margin-bottom:1rem;">
                Prompt Engineering · RAG · OCR · Multi-provider AI orchestration · Compatibility analysis
            </p>
            <span style="background:#f4f6f8;padding:.4rem .8rem;border-radius:999px;margin-right:.4rem;">Django product</span>
            <span style="background:#f4f6f8;padding:.4rem .8rem;border-radius:999px;margin-right:.4rem;">Streamlit public demo</span>
            <span style="background:#f4f6f8;padding:.4rem .8rem;border-radius:999px;margin-right:.4rem;">RAG workflow</span>
            <span style="background:#f4f6f8;padding:.4rem .8rem;border-radius:999px;">OCR-ready</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.warning(
        "Demo técnica basada en el flujo real de NutriPrompt. "
        "No sustituye consejo médico o nutricional profesional."
    )


def intake_tab() -> None:
    st.header("Smart Nutrition Intake")
    st.caption("Completa un perfil ficticio y genera una propuesta demo basada en reglas, RAG y análisis de compatibilidad.")

    col1, col2, col3 = st.columns(3)

    with col1:
        name = st.text_input("Nombre", value=st.session_state["name"])
        age = st.number_input("Edad", min_value=18, max_value=90, value=34)

    with col2:
        goal = st.selectbox(
            "Objetivo principal",
            ["Mejora digestiva", "Organizar comidas", "Comer más equilibrado", "Ganar energía"],
            index=["Mejora digestiva", "Organizar comidas", "Comer más equilibrado", "Ganar energía"].index(
                st.session_state["goal"]
            ),
        )
        budget = st.selectbox(
            "Presupuesto semanal",
            ["Ajustado", "Medio", "Flexible"],
            index=["Ajustado", "Medio", "Flexible"].index(st.session_state["budget"]),
        )

    with col3:
        activity = st.slider("Nivel de actividad física", 1, 5, st.session_state["activity"])
        context = st.text_area("Síntomas o contexto", value=st.session_state["context"])

    restrictions = st.multiselect(
        "Restricciones alimentarias",
        ["Low FODMAP", "Sin lactosa", "Sin gluten", "Vegetariano", "Vegano"],
        default=st.session_state["restrictions"],
    )

    preferences = st.multiselect(
        "Preferencias",
        ["Recetas rápidas", "Batch cooking", "Tupper", "Cenas ligeras", "Presupuesto ajustado"],
        default=st.session_state["preferences"],
    )

    col_button, col_reset = st.columns([1, 1])

    with col_button:
        if st.button("🚀 Generar plan inteligente", use_container_width=True):
            st.session_state["plan_generated"] = True
            st.session_state["name"] = name
            st.session_state["goal"] = goal
            st.session_state["budget"] = budget
            st.session_state["activity"] = activity
            st.session_state["context"] = context
            st.session_state["restrictions"] = restrictions
            st.session_state["preferences"] = preferences

            st.success("✅ Plan generado correctamente. Abre la pestaña **✅ Plan** para ver el resultado.")

    with col_reset:
        if st.button("🔄 Reiniciar demo", use_container_width=True):
            reset_demo()

    if st.session_state.get("plan_generated"):
        st.info("Tu plan demo ya está preparado. Ve a la pestaña **✅ Plan** para revisarlo.")


def workflow_tab() -> None:
    st.header("AI Workflow Pipeline")
    st.caption("Así se transforma un perfil de usuario en una salida estructurada y explicable.")

    steps = [
        ("1. User Input", "Structured profile, restrictions and symptoms"),
        ("2. Profile Analysis", "Normalize goals, activity and dietary constraints"),
        ("3. RAG Retrieval", "Retrieve nutrition rules from the knowledge base"),
        ("4. Prompt Builder", "Compose grounded and structured generation prompt"),
        ("5. Gemini API", "Primary model provider"),
        ("6. OpenAI Fallback", "Secondary provider for resilience"),
        ("7. Rules Engine", "Validate restrictions and compatibility"),
        ("8. Structured Output", "Generate table, shopping logic and PDF-ready content"),
    ]

    cols = st.columns(4)

    for index, (title, description) in enumerate(steps):
        with cols[index % 4]:
            st.container(border=True).markdown(f"### {title}\n{description}")

    st.success("Resilient orchestration: Gemini → OpenAI fallback → structured mock generation")


def vision_tab() -> None:
    st.header("Vision Module · OCR + Nutrition Intelligence")
    st.caption("Simulación de análisis de etiqueta, despensa o PDF nutricional.")

    uploaded_file = st.file_uploader(
        "Sube una etiqueta, imagen o PDF",
        type=["png", "jpg", "jpeg", "pdf"],
    )

    if uploaded_file:
        st.success("Archivo recibido correctamente.")
    else:
        st.info("Puedes probar sin subir archivo: la demo muestra un análisis simulado de una etiqueta de producto.")

    st.code(
        """
Detected ingredients:
- Wheat flour
- Milk powder
- Onion powder
- Sugar
- Salt
        """,
        language="text",
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.warning("Gluten detected: wheat flour")

    with col2:
        st.warning("Lactose detected: milk powder")

    with col3:
        st.warning("Low FODMAP warning: onion powder")

    st.info("NutriPrompt combina OCR, reglas nutricionales y restricciones del perfil antes de generar el resultado.")


def plan_tab() -> None:
    if not st.session_state.get("plan_generated"):
        st.info("Primero genera un plan desde la pestaña **🏠 Intake**.")
        return

    name = st.session_state.get("name", "Laura")
    goal = st.session_state.get("goal", "Mejora digestiva")
    budget = st.session_state.get("budget", "Medio")
    restrictions = st.session_state.get("restrictions", [])
    preferences = st.session_state.get("preferences", [])
    context = st.session_state.get("context", "")

    st.success("✅ Plan generado correctamente")
    st.header(f"Generated Nutrition Plan for {name}")

    col1, col2, col3 = st.columns(3)

    col1.metric("Objetivo", goal)
    col2.metric("Presupuesto", budget)
    col3.metric("Restricciones", str(len(restrictions)))

    st.markdown("### Resumen del perfil")

    st.write(
        {
            "Nombre": name,
            "Objetivo": goal,
            "Presupuesto": budget,
            "Restricciones": restrictions,
            "Preferencias": preferences,
            "Contexto": context,
        }
    )

    st.markdown("### Plan semanal demo")

    plan = build_demo_plan()
    st.dataframe(plan, use_container_width=True)

    col_rag, col_compatibility = st.columns(2)

    with col_rag:
        st.subheader("Retrieved RAG Context")
        st.markdown(
            """
            ✅ Low FODMAP rule: avoid onion, garlic, wheat, apples and some legumes when digestive sensitivity is present.

            ✅ Lactose-free rule: avoid conventional dairy and use lactose-free or plant-based alternatives.

            ✅ Planning rule: prioritize simple, repeatable and realistic meals for weekly organization.
            """
        )

    with col_compatibility:
        st.subheader("Compatibility Analysis")
        st.warning("Review yogurts, cheeses, sauces and processed foods for hidden lactose.")
        st.warning("Avoid onion powder and wheat flour when Low FODMAP or gluten-free rules apply.")

    with st.expander("View generated prompt"):
        st.code(
            f"""
Act as a weekly meal organization assistant.

User profile:
- Name: {name}
- Goal: {goal}
- Budget: {budget}
- Restrictions: {", ".join(restrictions)}
- Preferences: {", ".join(preferences)}
- Context: {context}

Use retrieved nutrition rules as priority context.
Return structured JSON.
Avoid medical claims.
Generate a practical weekly plan adapted to restrictions and preferences.
            """,
            language="text",
        )


def dashboard_tab() -> None:
    st.header("Intelligence Dashboard")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("AI Providers", "2", "Gemini + OpenAI")
    col2.metric("Tests Passing", "17", "stable")
    col3.metric("Workflow Layers", "8+", "production-ready")
    col4.metric("Output Engine", "PDF", "downloadable")

    st.subheader("Architecture Overview")

    architecture = pd.DataFrame(
        [
            ["Backend Core", "Django"],
            ["Language Runtime", "Python 3.13"],
            ["AI Orchestration", "Gemini API + OpenAI Fallback"],
            ["Knowledge Retrieval", "Custom Nutrition RAG Engine"],
            ["OCR Intelligence", "Tesseract OCR + Parsing"],
            ["Data Layer", "JSON Knowledge Base"],
            ["Output Generation", "WeasyPrint PDF Engine"],
            ["Presentation Layer", "HTML + CSS"],
            ["Prototype Layer", "Streamlit Interactive Demo"],
        ],
        columns=["Layer", "Technology"],
    )

    st.dataframe(architecture, use_container_width=True)

    st.subheader("Core AI System Layers")

    layers = [
        "User Profiling Engine",
        "Restrictions Normalizer",
        "Nutritional Rule Retrieval",
        "Prompt Builder Engine",
        "AI Multi-provider Routing",
        "Compatibility Validator",
        "Structured Plan Generator",
        "PDF Export Pipeline",
    ]

    cols = st.columns(4)

    for index, layer in enumerate(layers):
        with cols[index % 4]:
            st.container(border=True).markdown(f"✓ {layer}")

    st.subheader("End-to-End AI Pipeline")
    st.info(
        "User Input → Profile Normalization → RAG Retrieval → Prompt Builder → Gemini Generation → "
        "OpenAI Fallback → Compatibility Analysis → Structured Plan → PDF Export"
    )


def copilot_tab() -> None:
    st.header("NutriPrompt AI Copilot")
    st.caption("Una capa conversacional para explicar el plan y hacerlo más comprensible.")

    st.chat_message("assistant").write(
        "Hola, soy NutriPrompt Copilot. Puedo explicar el plan, revisar restricciones "
        "o detectar posibles incompatibilidades."
    )

    question = st.chat_input("Pregunta sobre el plan nutricional...")

    if question:
        st.chat_message("user").write(question)
        st.chat_message("assistant").write(
            "Según el perfil actual, NutriPrompt prioriza un plan compatible con las restricciones indicadas. "
            "El flujo combina RAG, reglas nutricionales y análisis de compatibilidad antes de generar el resultado."
        )

    st.chat_message("user").write(
        "Explícame cómo este plan se adapta a mis restricciones y objetivos."
    )

    st.chat_message("assistant").write(
        "El sistema recupera reglas relevantes sobre Low FODMAP y lactosa, detecta posibles conflictos "
        "y adapta el plan con alternativas sencillas, transportables y compatibles con el contexto de la persona."
    )


def main() -> None:
    init_state()
    show_header()

    tabs = st.tabs(
        [
            "🏠 Intake",
            "🧠 AI Workflow",
            "📄 Vision / OCR",
            "📊 Dashboard",
            "💬 AI Copilot",
            "✅ Plan",
        ]
    )

    with tabs[0]:
        intake_tab()

    with tabs[1]:
        workflow_tab()

    with tabs[2]:
        vision_tab()

    with tabs[3]:
        dashboard_tab()

    with tabs[4]:
        copilot_tab()

    with tabs[5]:
        plan_tab()


if __name__ == "__main__":
    main()