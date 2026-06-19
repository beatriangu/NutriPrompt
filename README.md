
# 🥦 NutriPrompt

> **NutriPrompt is a domain-specific AI workflow system designed to demonstrate production-grade Prompt Engineering, Retrieval-Augmented Generation (RAG), OCR pipelines, validation layers and resilient multi-provider LLM orchestration.**

Built with **Django**, **Prompt Engineering**, **RAG**, **OCR pipelines**, **Validation Layers**, **Shopping Intelligence**, **PDF generation**, and **multi-provider AI orchestration**.

NutriPrompt is not a meal-plan generator.

It is an **AI decision-support system for contextual nutrition planning**.

---

# 🔗 Live Demo

### Public Streamlit Demo

**👉 https://nutriprompt-live.streamlit.app**

This public demo exposes NutriPrompt’s internal workflow in a recruiter-friendly format.

---

# 🧠 What This Project Demonstrates

NutriPrompt is designed as an AI systems engineering project.

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

Reliable AI systems must understand:

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

---

# 🎯 Why This Matters

Most AI nutrition tools rely on direct prompting.

That creates serious limitations:

- no domain grounding
- weak restriction handling
- no ingredient validation
- no retrieval layer
- no fallback resilience
- no explainability

NutriPrompt addresses this through **layered AI architecture**.

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

# ⚙ Design Decisions

NutriPrompt was intentionally designed around:

- Controlled generation over open-ended prompting
- Retrieval before inference
- Validation before recommendation
- Explainability over black-box outputs
- Provider abstraction for portability
- Separation between core product and public demo layer
- Structured outputs for downstream usability

These decisions reflect product-oriented AI architecture principles.

---

# ⚡ Core AI Capabilities

- Personalized Nutrition Planning
- Retrieval-Augmented Generation (RAG)
- OCR + Ingredient Intelligence
- Validation Layer
- Shopping Intelligence
- AI Copilot explainability
- Resilient provider orchestration

---

# ⚡ Resilient AI Orchestration

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

| Layer         | Technology              |
|---------------|-------------------------|
| Backend       | Django                  |
| Language      | Python 3.13             |
| AI Providers  | Gemini API + OpenAI API |
| Retrieval     | Custom Nutrition RAG    |
| OCR           | Tesseract OCR           |
| Data          | JSON                    |
| PDF Rendering | WeasyPrint              |
| Frontend      | HTML + CSS              |
| Demo Layer    | Streamlit               |
| Testing       | Django Test Framework   |
| Architecture  | Service-Oriented Design |

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
- compatibility analysis
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
