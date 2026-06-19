# 🥦 NutriPrompt

> **NutriPrompt is a domain-specific AI workflow system designed to demonstrate production-grade Prompt Engineering, Retrieval-Augmented Generation (RAG), OCR pipelines, validation layers and resilient multi-provider LLM orchestration.**

Built with **Django**, **Prompt Engineering**, **Retrieval-Augmented Generation (RAG)**, **OCR pipelines**, **validation layers**, **shopping intelligence**, **PDF generation**, and **multi-provider AI orchestration**.

NutriPrompt is not a meal-plan generator.

It is an **AI decision-support system for contextual nutrition planning**.

Its purpose is to demonstrate how modern AI systems combine:

- structured user data
- domain knowledge
- retrieval systems
- validation layers
- explainability
- fallback orchestration
- execution-ready outputs

to deliver **more reliable, grounded and operational AI workflows**.

![Python](https://img.shields.io/badge/Python-3.13-blue)
![Django](https://img.shields.io/badge/Django-5.x-green)
![OpenAI](https://img.shields.io/badge/OpenAI-API-black)
![Gemini](https://img.shields.io/badge/Gemini-AI-orange)
![OCR](https://img.shields.io/badge/OCR-Vision-purple)
![RAG](https://img.shields.io/badge/RAG-Knowledge%20Retrieval-red)

---

# 🔗 Live Demo

### Public Streamlit Demo

👉 **https://nutriprompt-live.streamlit.app**

This public technical demo exposes NutriPrompt’s internal workflow in a recruiter-friendly format:

- structured intake
- RAG orchestration
- OCR reasoning
- validation layers
- AI Copilot explainability
- structured outputs

---

# 🧠 What This Project Demonstrates

NutriPrompt is designed as an **AI systems engineering project**.

It demonstrates:

- Context-first AI workflows
- Prompt Engineering for controlled generation
- Retrieval-Augmented Generation (RAG)
- OCR ingestion and structured parsing
- Validation layers before inference
- Multi-provider LLM orchestration
- Fallback resilience strategies
- Explainable outputs
- Human-readable + machine-readable reports
- Product-oriented AI UX design

This project reflects how production AI systems move beyond raw prompting into structured, resilient and explainable workflows.

---

# ✨ Product Vision

Nutrition planning is not a simple content generation problem.

Reliable AI nutrition systems must understand:

- personal goals
- digestive conditions
- ingredient compatibility
- dietary restrictions
- food preferences
- budget limitations
- real-life constraints
- execution friction

NutriPrompt treats nutrition as an **intelligent workflow problem**.

Not as a chatbot.

Its architecture enriches every request before generation.

This produces:

✅ grounded outputs  
✅ fewer hallucinations  
✅ explainable recommendations  
✅ compatibility-aware planning  
✅ resilient provider orchestration  
✅ production-oriented AI workflows

---

# 🎯 Why This Matters

Most AI nutrition tools rely on direct prompting.

That creates serious limitations:

- no domain grounding
- weak restriction handling
- no ingredient validation
- no compatibility logic
- no retrieval layer
- no fallback resilience
- no explainability

For healthcare-adjacent workflows, this is not enough.

NutriPrompt addresses this through **layered AI architecture**.

It is built to demonstrate how **production-grade AI systems** should be designed.

---

# 💡 Why I Built This

I built NutriPrompt to explore how AI systems can evolve beyond content generation into **decision-support architectures**.

The goal was never to generate meal plans.

The goal was to design a system that demonstrates:

- structured reasoning
- domain grounding
- retrieval orchestration
- explainability
- resilient fallbacks
- product-oriented thinking
- real-world execution

This project reflects how I think about **AI product design**.

---

# 🏗 System Architecture

```text
User Input
      ↓
Structured Intake Forms
      ↓
Profile Analysis
      ↓
RAG Knowledge Retrieval
      ↓
Prompt Builder
      ↓
Gemini API
      ↓ (Fallback)
OpenAI API
      ↓
Structured JSON Output
      ↓
Nutrition Rules Engine
      ↓
Validation Layer
      ↓
HTML Rendering
      ↓
Shopping Intelligence
      ↓
PDF Generation
      ↓
AI Copilot Layer
```

---

# 📸 Product Walkthrough · Django Application

## 1. Smart Nutrition Intake

NutriPrompt transforms structured user information into personalized nutrition workflows using:

- goal understanding
- digestive symptoms
- food preferences
- dietary restrictions
- budget logic
- lifestyle context

![Home](docs/screenshots/01_home.png)

---

## 2. Generated Nutrition Plan

The AI output includes:

- weekly meal planning
- compatibility-aware recommendations
- practical tupper adaptation
- explainable profile tags
- downloadable PDF

![Generated Plan](docs/screenshots/02_plan.png)

---

## 3. Intelligent Shopping Layer

NutriPrompt converts generated plans into:

- organized shopping lists
- category grouping
- optimized planning
- actionable execution

This transforms generation into utility.

![Shopping List](docs/screenshots/03_shopping_list.png)

---

# 🧠 Streamlit Technical Demo

NutriPrompt includes a dedicated **public Streamlit demo** to expose the internal AI workflow.

Designed for:

- technical interviews
- AI architecture walkthroughs
- product demos
- recruiter exploration
- portfolio storytelling

---

## Intake Layer

Structured nutrition intake.

![Intake](docs/streamlit_demo/01_Intake.png)

---

## Pipeline Orchestration

Full workflow visibility.

![Workflow](docs/streamlit_demo/02_AI_Workflow.png)

---

## OCR Layer

Ingredient extraction and incompatibility detection.

![OCR](docs/streamlit_demo/03_Vision_OCR.png)

---

## Structured Output Layer

Weekly nutrition planning.

![Plan](docs/streamlit_demo/04_Plan.png)

---

## Technical Dashboard

Architecture and workflow observability.

![Dashboard](docs/streamlit_demo/05_Dashboard.png)

---

## AI Copilot Layer

Interactive explainability assistant:

- explains generated plans
- validates restrictions
- reviews ingredients
- provides contextual reasoning

This transforms NutriPrompt into an interactive AI decision-support layer.

![AI Copilot](docs/streamlit_demo/06_AI_copilot.png)

---

# ⚡ Core AI Capabilities

## Personalized Nutrition Planning

Generate structured plans based on:

- goals
- restrictions
- symptoms
- preferences
- routines
- budget
- activity levels

---

## Retrieval-Augmented Generation (RAG)

NutriPrompt retrieves nutrition rules before generation.

Examples:

- Low FODMAP guidance
- gluten-free substitutions
- lactose-free alternatives
- digestive-safe patterns
- shopping optimization

This reduces hallucinations and improves consistency.

---

## OCR + Ingredient Intelligence

NutriPrompt analyzes:

- product labels
- pantry inventories
- ingredient lists
- nutrition PDFs
- fridge scans

OCR outputs are validated against user restrictions.

---

## Validation Layer

NutriPrompt evaluates:

- user restrictions
- retrieved rules
- OCR-detected ingredients

to detect conflicts before recommendation.

---

## Shopping Intelligence

Generated plans are transformed into:

- categorized shopping lists
- planning-friendly structures
- execution-ready outputs

This reduces friction between recommendation and action.

---

# ⚡ Resilient AI Orchestration

NutriPrompt implements provider resilience:

```text
Gemini API
      ↓
OpenAI Fallback
      ↓
Structured Mock Generation
```

Benefits:

- stable demos
- graceful degradation
- provider independence
- predictable outputs

---

# ⚙ Design Decisions

NutriPrompt was intentionally designed around:

- Controlled generation over open-ended prompting
- Retrieval before inference
- Validation before recommendation
- Explainability over black-box generation
- Provider abstraction for portability
- Separation between core product and public demo layer
- Structured outputs for downstream usability

These decisions reflect product-oriented AI architecture principles.

---

# 🧠 AI Engineering Concepts Demonstrated

This project showcases:

- Prompt Engineering
- Retrieval-Augmented Generation (RAG)
- OCR Pipelines
- Multi-provider orchestration
- Explainable AI workflows
- Rule-based reasoning
- Validation layers
- Shopping intelligence
- Product-oriented AI architecture
- Service-oriented design
- Fallback resilience
- Structured AI outputs

---

# ⚙️ Technology Stack

| Layer | Technology |
|---|---|
| Backend | Django |
| Language | Python 3.13 |
| AI Providers | Gemini API + OpenAI API |
| Retrieval | Custom Nutrition RAG |
| OCR | Tesseract OCR |
| Data | JSON |
| PDF Rendering | WeasyPrint |
| Frontend | HTML + CSS |
| Demo Layer | Streamlit |
| Testing | Django Test Framework |
| Architecture | Service-Oriented Design |

---

# 📁 Project Structure

```text
NutriPrompt/
├── nutriprompt_app/
│   ├── services/
│   │   ├── ai/
│   │   ├── nutrition/
│   │   ├── profiles/
│   │   ├── rag/
│   │   ├── vision/
│   │   └── presentation/
│   ├── templates/
│   ├── tests/
│   └── views.py
│
├── streamlit_demo/
│   └── app.py
│
├── docs/
│   ├── screenshots/
│   └── streamlit_demo/
```

---

# 🧪 Test Coverage

Current automated validation includes:

- prompt generation
- knowledge retrieval
- validation logic
- OCR processing
- context injection
- structured outputs
- shopping generation

Run:

```bash
python manage.py test
```

Current suite:

```text
17 automated tests passing
```

---

# 🛠 Installation

```bash
git clone https://github.com/beatriangu/NutriPrompt.git
cd NutriPrompt

python3 -m venv venv
source venv/bin/activate

python -m pip install --upgrade pip
pip install -r requirements.txt
```

---

# ▶ Run Django App

```bash
python manage.py runserver
```

Open:

```text
http://127.0.0.1:8000/
```

---

# ▶ Run Streamlit Demo

```bash
streamlit run streamlit_demo/app.py
```

---

# ⚠ Disclaimer

NutriPrompt provides informational guidance only.

It does not replace medical, nutritional or healthcare advice.

Outputs should be reviewed by qualified professionals where appropriate.

---

# 👩‍💻 Author

**Bea Lamiquiz**

🌐 Portfolio: https://bchill.net  
💻 GitHub: https://github.com/beatriangu  
💼 LinkedIn: https://www.linkedin.com/in/bealamiquiz/

---

# 🤝 Let's Connect

If you’re working on AI products, LLM systems, RAG pipelines or GenAI workflows, I’d love to connect.

Open to:

- AI product conversations
- technical collaboration
- architecture discussions
- generative AI opportunities
