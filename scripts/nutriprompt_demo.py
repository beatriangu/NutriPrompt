import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="NutriPrompt Demo",
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
[data-testid="stStatusWidget"] {display: none;}

.block-container {
    padding-top: 0.2rem;
    padding-bottom: 0.2rem;
    padding-left: 2rem;
    padding-right: 2rem;
    max-width: 100%;
}

/* Compact title */
h1 {
    font-size: 2.2rem !important;
    margin-bottom: 0.2rem !important;
}

h2, h3 {
    margin-top: 0.4rem !important;
    margin-bottom: 0.4rem !important;
}

/* Compact text */
p, label, div {
    font-size: 0.95rem;
}

/* Reduce vertical gaps */
[data-testid="stVerticalBlock"] {
    gap: 0.35rem;
}

[data-testid="stHorizontalBlock"] {
    gap: 1.2rem;
}

/* Compact tabs */
.stTabs [data-baseweb="tab-list"] {
    gap: 1rem;
    margin-bottom: 0.2rem;
}

.stTabs [data-baseweb="tab"] {
    height: 2rem;
    padding: 0.2rem 0.5rem;
    font-size: 0.95rem;
}

/* Compact inputs */
[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input,
[data-testid="stTextArea"] textarea {
    min-height: 2rem !important;
    padding: 0.25rem 0.6rem !important;
}

/* Compact select/multiselect */
[data-baseweb="select"] > div {
    min-height: 2rem !important;
}

/* Compact info box */
[data-testid="stAlert"] {
    padding: 0.45rem 0.8rem;
    margin-bottom: 0.3rem;
}

/* Reduce label spacing */
label {
    margin-bottom: 0.1rem !important;
}

/* Button */
.stButton button {
    padding: 0.35rem 1rem;
    border-radius: 0.6rem;
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)

st.title("🥦 NutriPrompt")

st.markdown(
    "**AI-powered nutrition intelligence platform** · Prompt Engineering · RAG · OCR · Multi-provider AI orchestration"
)

st.info(
    "Demo Streamlit basada en el flujo real de NutriPrompt. No sustituye consejo médico o nutricional profesional."
)

tab1, tab2, tab3, tab4 = st.tabs(
    ["🏠 Intake", "🧠 AI Workflow", "📄 Vision / OCR", "📊 Dashboard"]
)

with tab1:
    st.subheader("Smart Nutrition Intake")

    col1, col2, col3 = st.columns(3)

    with col1:
        name = st.text_input("Nombre", "Cliente demo")
        age = st.number_input("Edad", 16, 99, 35)

    with col2:
        goal = st.selectbox(
            "Objetivo principal",
            ["Pérdida de peso", "Mantenimiento", "Ganancia muscular", "Mejora digestiva"],
        )
        budget = st.selectbox(
            "Presupuesto semanal",
            ["Bajo", "Medio", "Alto"],
        )

    with col3:
        activity = st.slider("Nivel de actividad física", 1, 5, 3)
        symptoms = st.text_area("Síntomas o contexto", "Digestiones pesadas por la tarde", height=70)

    col4, col5 = st.columns(2)

    with col4:
        restrictions = st.multiselect(
            "Restricciones alimentarias",
            ["Low FODMAP", "Sin gluten", "Sin lactosa", "Vegetariano", "Vegano"],
        )

    with col5:
        preferences = st.multiselect(
            "Preferencias",
            ["Recetas rápidas", "Batch cooking", "Comida mediterránea", "Alta proteína"],
        )

    if st.button("🚀 Generate intelligent nutrition plan"):
        restrictions_text = ", ".join(restrictions) if restrictions else "None"
        preferences_text = ", ".join(preferences) if preferences else "No specific preferences"

        retrieved_context = []

        if "Low FODMAP" in restrictions:
            retrieved_context.append(
                "Avoid high-FODMAP ingredients such as onion, garlic, wheat, apples and some legumes."
            )

        if "Sin gluten" in restrictions:
            retrieved_context.append(
                "Use naturally gluten-free grains such as rice, quinoa, corn or certified gluten-free oats."
            )

        if "Sin lactosa" in restrictions:
            retrieved_context.append(
                "Avoid lactose-containing dairy or use lactose-free alternatives."
            )

        if not retrieved_context:
            retrieved_context.append(
                "Apply general balanced meal planning guidance."
            )

        incompatible_items = []

        if "Low FODMAP" in restrictions and "Comida mediterránea" in preferences:
            incompatible_items.append(
                "Review onion and garlic usage in Mediterranean recipes."
            )

        if "Vegano" in restrictions and "Alta proteína" in preferences:
            incompatible_items.append(
                "Prioritize tofu, tempeh, legumes if tolerated, seeds and protein-rich grains."
            )

        plan = pd.DataFrame(
            {
                "Day": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
                "Breakfast": [
                    "Lactose-free yogurt with berries",
                    "Oats with banana and chia",
                    "Rice cakes with egg or tofu",
                    "Smoothie with lactose-free milk",
                    "Gluten-free toast with avocado",
                ],
                "Lunch": [
                    "Quinoa bowl with chicken or tofu",
                    "Rice with vegetables and protein",
                    "Mediterranean salad adapted to restrictions",
                    "Potato and salmon or tofu plate",
                    "Low-FODMAP pasta alternative",
                ],
                "Dinner": [
                    "Vegetable soup + protein",
                    "Omelette or tofu scramble",
                    "Grilled fish/chicken or vegan alternative",
                    "Rice noodles with vegetables",
                    "Simple batch-cooking dinner",
                ],
                "Snack": [
                    "Nuts or kiwi",
                    "Rice cakes",
                    "Lactose-free yogurt",
                    "Fruit adapted to tolerance",
                    "Carrot sticks with dip",
                ],
            }
        )

        st.session_state["plan"] = plan
        st.session_state["context"] = retrieved_context
        st.session_state["warnings"] = incompatible_items

        st.session_state["prompt"] = f"""
You are NutriPrompt, an AI nutrition workflow assistant.

USER PROFILE
- Name: {name}
- Age: {age}
- Goal: {goal}
- Budget: {budget}
- Activity level: {activity}/5
- Restrictions: {restrictions_text}
- Preferences: {preferences_text}
- Symptoms/context: {symptoms}

RETRIEVED NUTRITION KNOWLEDGE
{chr(10).join("- " + item for item in retrieved_context)}

TASK
Generate a structured weekly meal plan with breakfast, lunch, dinner and snack.
Include a smart shopping list, explain compatibility issues and keep a professional, motivating tone.
"""

        st.success("✅ Nutrition plan generated")

    if "plan" in st.session_state:
        st.subheader("Generated Nutrition Plan")
        st.dataframe(st.session_state["plan"], use_container_width=True)

        st.subheader("Retrieved RAG Context")
        for item in st.session_state["context"]:
            st.write(f"✅ {item}")

        if st.session_state["warnings"]:
            st.subheader("Compatibility Warnings")
            for warning in st.session_state["warnings"]:
                st.warning(warning)

        st.subheader("Generated Prompt")
        st.code(st.session_state["prompt"], language="markdown")

with tab2:
    st.subheader("AI Workflow Pipeline")

    pipeline = [
        "User Input",
        "Structured Forms",
        "Profile Analysis",
        "RAG Knowledge Retrieval",
        "Prompt Builder",
        "Gemini API",
        "OpenAI Fallback",
        "Structured JSON Output",
        "Nutrition Rules Engine",
        "Compatibility Analysis",
        "HTML Rendering",
        "PDF Generation",
    ]

    cols = st.columns(4)

    for index, step in enumerate(pipeline):
        with cols[index % 4]:
            st.write(f"⬇️ **{step}**")

    st.success("Resilient orchestration: Gemini → OpenAI fallback → structured mock generation")

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
        st.warning("Potential incompatibilities detected: gluten, lactose and onion powder.")
        st.info("NutriPrompt would combine OCR extraction with nutrition rules and user restrictions.")

with tab4:
    st.subheader("Intelligence Dashboard")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("AI Providers", "2", "Gemini + OpenAI")
    col2.metric("Tests Passing", "17", "stable")
    col3.metric("Workflow Layers", "8+", "AI architecture")
    col4.metric("Output", "PDF", "downloadable")

    architecture = pd.DataFrame(
        {
            "Layer": [
                "Backend",
                "Language",
                "AI Providers",
                "Retrieval",
                "OCR",
                "Data",
                "PDF",
                "Frontend",
            ],
            "Technology": [
                "Django",
                "Python 3.13",
                "Gemini API + OpenAI API",
                "Custom Nutrition RAG",
                "Tesseract OCR",
                "JSON",
                "WeasyPrint",
                "HTML + CSS",
            ],
        }
    )

    st.table(architecture)