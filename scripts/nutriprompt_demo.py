import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(
    page_title="NutriPrompt AI Demo",
    page_icon="🥦",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
#MainMenu {visibility: hidden;}
header {visibility: hidden;}
footer {visibility: hidden;}
[data-testid="stToolbar"] {display: none;}
[data-testid="stDecoration"] {display: none;}

.block-container {
    padding-top: 0.35rem;
    padding-left: 1.5rem;
    padding-right: 1.5rem;
    padding-bottom: 0.35rem;
    max-width: 100%;
}

h1 {
    font-size: 2.25rem !important;
    margin-bottom: 0.1rem !important;
}

h2, h3 {
    margin-top: 0.35rem !important;
    margin-bottom: 0.25rem !important;
}

p {
    margin-bottom: 0.35rem;
}

.np-hero {
    background: linear-gradient(135deg, #eef7ff 0%, #f5fff4 100%);
    padding: 0.75rem 1rem;
    border-radius: 16px;
    border: 1px solid #dbeafe;
    margin-bottom: 0.5rem;
}

.np-card {
    background: #ffffff;
    padding: 0.65rem 0.75rem;
    border-radius: 14px;
    border: 1px solid #e5e7eb;
    box-shadow: 0 3px 10px rgba(15, 23, 42, 0.04);
    height: 100%;
    font-size: 0.9rem;
}

.np-card h4 {
    margin-top: 0;
    margin-bottom: 0.25rem;
    font-size: 0.95rem;
}

.np-card p {
    font-size: 0.82rem;
    line-height: 1.25;
    margin-bottom: 0;
}

.np-badge {
    display: inline-block;
    background: #f1f5f9;
    color: #334155;
    padding: 0.25rem 0.55rem;
    border-radius: 999px;
    font-size: 0.76rem;
    margin-right: 0.25rem;
    margin-bottom: 0.25rem;
}

.np-alert {
    background: #fff7ed;
    border: 1px solid #fed7aa;
    color: #9a3412;
    padding: 0.5rem 0.75rem;
    border-radius: 12px;
    margin-bottom: 0.45rem;
    font-size: 0.85rem;
}

.np-flow {
    font-size: 0.95rem;
    line-height: 1.35;
}

.np-mini-label {
    color: #64748b;
    font-size: 0.78rem;
    font-weight: 700;
    letter-spacing: 0.02em;
    text-transform: uppercase;
}

[data-testid="stVerticalBlock"] {
    gap: 0.28rem;
}

[data-testid="column"] {
    padding: 0 0.25rem;
}

.stTabs [data-baseweb="tab-list"] {
    gap: 0.8rem;
}

.stTabs [data-baseweb="tab"] {
    font-size: 0.9rem;
    font-weight: 600;
    padding-top: 0.35rem;
    padding-bottom: 0.35rem;
}

[data-testid="stMetric"] {
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 14px;
    padding: 0.45rem 0.6rem;
}

[data-testid="stMetricLabel"] {
    font-size: 0.75rem;
}

[data-testid="stMetricValue"] {
    font-size: 1.45rem;
}

[data-testid="stDataFrame"] {
    font-size: 0.8rem;
}

div[data-testid="stTable"] table {
    font-size: 0.8rem;
}

div[data-testid="stTable"] td,
div[data-testid="stTable"] th {
    padding: 0.25rem 0.45rem !important;
}
</style>
""", unsafe_allow_html=True)


def build_retrieved_context(restrictions):
    context = []

    if "Low FODMAP" in restrictions:
        context.append(
            "Low FODMAP rule: avoid onion, garlic, wheat, apples and some legumes when digestive sensitivity is present."
        )

    if "Sin gluten" in restrictions:
        context.append(
            "Gluten-free rule: prioritize rice, quinoa, corn, potato and certified gluten-free oats."
        )

    if "Sin lactosa" in restrictions:
        context.append(
            "Lactose-free rule: avoid conventional dairy and use lactose-free or plant-based alternatives."
        )

    if "Vegano" in restrictions:
        context.append(
            "Vegan rule: ensure protein through tofu, tempeh, seeds, nuts and tolerated legumes."
        )

    if not context:
        context.append(
            "General balanced planning rule: combine protein, vegetables, complex carbohydrates and healthy fats."
        )

    return context


def build_warnings(restrictions, preferences):
    warnings = []

    if "Low FODMAP" in restrictions and "Comida mediterránea" in preferences:
        warnings.append("Mediterranean recipes must be adapted to avoid onion and garlic.")

    if "Vegano" in restrictions and "Alta proteína" in preferences:
        warnings.append("High-protein vegan planning requires careful protein source selection.")

    if "Sin lactosa" in restrictions:
        warnings.append("Check yogurts, cheeses, sauces and processed foods for hidden lactose.")

    return warnings


def build_plan(restrictions, preferences):
    lactose_free = "Sin lactosa" in restrictions
    gluten_free = "Sin gluten" in restrictions
    low_fodmap = "Low FODMAP" in restrictions
    quick = "Recetas rápidas" in preferences

    breakfast = [
        "Lactose-free yogurt with berries" if lactose_free else "Greek yogurt with fruit",
        "Rice cakes with egg or tofu" if gluten_free else "Oats with banana and chia",
        "Smoothie with lactose-free milk" if lactose_free else "Whole-grain toast with avocado",
        "Chia pudding with kiwi",
        "Gluten-free toast with avocado" if gluten_free else "Toast with hummus and tomato",
    ]

    lunch = [
        "Quinoa bowl with chicken or tofu",
        "Rice with vegetables and protein",
        "Mediterranean salad adapted to restrictions" if low_fodmap else "Mediterranean salad",
        "Potato and salmon or tofu plate",
        "Low-FODMAP pasta alternative" if low_fodmap else "Whole-grain pasta with vegetables",
    ]

    dinner = [
        "Vegetable soup + protein",
        "Omelette or tofu scramble",
        "Grilled fish/chicken or vegan alternative",
        "Rice noodles with vegetables",
        "Simple batch-cooking dinner" if quick else "Balanced seasonal dinner",
    ]

    snack = [
        "Nuts or kiwi",
        "Rice cakes",
        "Lactose-free yogurt" if lactose_free else "Fruit and yogurt",
        "Fruit adapted to tolerance",
        "Carrot sticks with dip",
    ]

    return pd.DataFrame(
        {
            "Day": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
            "Breakfast": breakfast,
            "Lunch": lunch,
            "Dinner": dinner,
            "Snack": snack,
        }
    )


def build_prompt(profile, context, warnings):
    return f"""
You are NutriPrompt, an AI nutrition workflow assistant.

USER PROFILE
- Name: {profile["name"]}
- Age: {profile["age"]}
- Goal: {profile["goal"]}
- Budget: {profile["budget"]}
- Activity level: {profile["activity"]}/5
- Restrictions: {", ".join(profile["restrictions"]) if profile["restrictions"] else "None"}
- Preferences: {", ".join(profile["preferences"]) if profile["preferences"] else "No specific preferences"}
- Symptoms/context: {profile["symptoms"]}

RETRIEVED NUTRITION KNOWLEDGE
{chr(10).join("- " + item for item in context)}

COMPATIBILITY WARNINGS
{chr(10).join("- " + item for item in warnings) if warnings else "- No critical incompatibilities detected."}

TASK
Generate a structured weekly nutrition plan with breakfast, lunch, dinner and snack.
Include smart shopping logic, compatibility notes and a professional motivating tone.
"""


st.title("🥦 NutriPrompt · AI Workflow Intelligence")

st.markdown("""
<div class="np-hero">
    <h3>Production-ready AI Architecture for Personalized Nutrition</h3>
    <p>
    RAG Retrieval · OCR Intelligence · Compatibility Engine · Multi-provider LLM Orchestration
    </p>
    <span class="np-badge">Django product</span>
    <span class="np-badge">Streamlit technical demo</span>
    <span class="np-badge">RAG workflow</span>
    <span class="np-badge">OCR-ready</span>
    <span class="np-badge">Fallback system</span>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="np-alert">
Demo técnica basada en el flujo real de NutriPrompt. No sustituye consejo médico o nutricional profesional.
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5 = st.tabs(
    [
        "🏠 Intake",
        "🧠 AI Workflow",
        "📄 Vision / OCR",
        "📊 Dashboard",
        "💬 AI Copilot",
    ]
)

with tab1:
    st.subheader("Smart Nutrition Intake")

    col1, col2, col3 = st.columns(3)

    with col1:
        name = st.text_input("Nombre", "Laura")
        age = st.number_input("Edad", 16, 99, 34)

    with col2:
        goal = st.selectbox(
            "Objetivo principal",
            ["Mejora digestiva", "Pérdida de peso", "Mantenimiento", "Ganancia muscular"],
        )
        budget = st.selectbox("Presupuesto semanal", ["Bajo", "Medio", "Alto"], index=1)

    with col3:
        activity = st.slider("Nivel de actividad física", 1, 5, 3)
        symptoms = st.text_area(
            "Síntomas o contexto",
            "Digestiones pesadas por la tarde",
            height=70,
        )

    col4, col5 = st.columns(2)

    with col4:
        restrictions = st.multiselect(
            "Restricciones alimentarias",
            ["Low FODMAP", "Sin gluten", "Sin lactosa", "Vegetariano", "Vegano"],
            default=["Low FODMAP", "Sin lactosa"],
        )

    with col5:
        preferences = st.multiselect(
            "Preferencias",
            ["Recetas rápidas", "Batch cooking", "Comida mediterránea", "Alta proteína"],
            default=["Recetas rápidas", "Batch cooking"],
        )

    if st.button("🚀 Generate intelligent nutrition plan"):
        profile = {
            "name": name,
            "age": age,
            "goal": goal,
            "budget": budget,
            "activity": activity,
            "restrictions": restrictions,
            "preferences": preferences,
            "symptoms": symptoms,
        }

        context = build_retrieved_context(restrictions)
        warnings = build_warnings(restrictions, preferences)
        plan = build_plan(restrictions, preferences)
        prompt = build_prompt(profile, context, warnings)

        st.session_state["profile"] = profile
        st.session_state["context"] = context
        st.session_state["warnings"] = warnings
        st.session_state["plan"] = plan
        st.session_state["prompt"] = prompt
        st.session_state["generated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")

        st.success("✅ Nutrition plan generated")

    if "plan" in st.session_state:
        st.subheader("Generated Nutrition Plan")
        st.dataframe(st.session_state["plan"], use_container_width=True)

        c1, c2 = st.columns(2)

        with c1:
            st.subheader("Retrieved RAG Context")
            for idx, item in enumerate(st.session_state["context"], start=1):
                st.markdown(f"**Source {idx}** · {item}")

        with c2:
            st.subheader("Compatibility Analysis")
            if st.session_state["warnings"]:
                for warning in st.session_state["warnings"]:
                    st.warning(warning)
            else:
                st.success("No critical incompatibilities detected.")

        with st.expander("View generated prompt"):
            st.code(st.session_state["prompt"], language="markdown")

with tab2:
    st.subheader("AI Workflow Pipeline")

    workflow = [
        ("1", "Structured Input", "Profile, goals, restrictions and symptoms"),
        ("2", "Profile Analysis", "Normalize objectives, activity level and dietary constraints"),
        ("3", "RAG Retrieval", "Retrieve domain rules before generation"),
        ("4", "Prompt Builder", "Inject context into a controlled prompt"),
        ("5", "Primary Inference", "Gemini API as main provider"),
        ("6", "Fallback Strategy", "OpenAI as secondary provider"),
        ("7", "Compatibility Engine", "Validate restrictions before rendering"),
        ("8", "Structured Output", "Generate plan, shopping logic and PDF-ready content"),
    ]

    cols = st.columns(4)
    for index, (number, title, description) in enumerate(workflow):
        with cols[index % 4]:
            st.markdown(
                f"""
                <div class="np-card">
                    <h4>{number}. {title}</h4>
                    <p>{description}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

    c1, c2, c3 = st.columns(3)
    c1.info("Primary inference → Gemini")
    c2.warning("Fallback strategy → OpenAI")
    c3.success("Final output → JSON + PDF")

with tab3:
    st.subheader("Vision Module · OCR + Nutrition Intelligence")

    uploaded_file = st.file_uploader(
        "Upload a product label, pantry image or nutrition PDF",
        type=["png", "jpg", "jpeg", "pdf"],
    )

    if uploaded_file:
        st.success("File received")

        extracted_text = """
Detected ingredients:
- Wheat flour
- Milk powder
- Onion powder
- Sugar
- Salt
"""

        st.code(extracted_text)

        detected_risks = [
            "Gluten detected: wheat flour",
            "Lactose detected: milk powder",
            "Low FODMAP warning: onion powder",
        ]

        for risk in detected_risks:
            st.warning(risk)

        st.info("NutriPrompt combines OCR extraction with nutrition rules and user restrictions.")

    else:
        st.info("Upload a label or PDF to simulate OCR-based compatibility detection.")

with tab4:
    st.subheader("Intelligence Dashboard")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("AI Providers", "2", "Gemini + OpenAI")
    col2.metric("Tests Passing", "17", "stable")
    col3.metric("Workflow Layers", "8+", "production-ready")
    col4.metric("Output Engine", "PDF", "downloadable")

    st.subheader("Architecture Overview")

    architecture = pd.DataFrame(
        {
            "Layer": [
                "Backend Core",
                "Language Runtime",
                "AI Orchestration",
                "Knowledge Retrieval",
                "OCR Intelligence",
                "Data Layer",
                "Output Generation",
                "Presentation Layer",
                "Prototype Layer",
            ],
            "Technology": [
                "Django",
                "Python 3.13",
                "Gemini API + OpenAI Fallback",
                "Custom Nutrition RAG Engine",
                "Tesseract OCR + Parsing",
                "JSON Knowledge Base",
                "WeasyPrint PDF Engine",
                "HTML + CSS",
                "Streamlit Interactive Prototype",
            ],
        }
    )

    st.table(architecture)

    st.subheader("Core AI System Layers")

    intelligence_layers = [
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

    for i, layer in enumerate(intelligence_layers):
        with cols[i % 4]:
            st.markdown(
                f"""
                <div class="np-card">
                    <b>✓ {layer}</b>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.subheader("End-to-End AI Pipeline")

    st.markdown(
        """
        <div class="np-card np-flow">
        <b>NutriPrompt Pipeline</b><br><br>
        User Input → Profile Normalization → RAG Retrieval → Prompt Builder → Gemini Generation → OpenAI Fallback → Compatibility Analysis → Structured Plan → PDF Export
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.info(
        "NutriPrompt is designed as a resilient AI product architecture combining retrieval, reasoning, OCR intelligence and multi-provider orchestration."
    )

with tab5:
    st.subheader("NutriPrompt AI Copilot")

    if "messages" not in st.session_state:
        st.session_state["messages"] = [
            {
                "role": "assistant",
                "content": "Hola, soy NutriPrompt Copilot. Puedo explicar el plan, revisar restricciones o detectar posibles incompatibilidades.",
            }
        ]

    for message in st.session_state["messages"]:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    user_message = st.chat_input("Pregunta sobre el plan nutricional...")

    if user_message:
        st.session_state["messages"].append(
            {"role": "user", "content": user_message}
        )

        with st.chat_message("user"):
            st.write(user_message)

        if "plan" in st.session_state:
            response = (
                "Según el perfil actual, NutriPrompt prioriza un plan compatible con las restricciones indicadas. "
                "El flujo combina RAG, reglas nutricionales y análisis de compatibilidad antes de generar el resultado."
            )
        else:
            response = (
                "Primero genera un plan desde la pestaña Intake para que pueda contextualizar la respuesta."
            )

        st.session_state["messages"].append(
            {"role": "assistant", "content": response}
        )

        with st.chat_message("assistant"):
            st.write(response)