# 🥦 NutriPrompt

> **AI-powered nutrition intelligence platform designed to transform structured health data into contextualized, explainable and actionable nutrition plans.**
>
> Built with **Django**, **Prompt Engineering**, **Retrieval-Augmented Generation (RAG)**, **OCR pipelines** and **multi-provider AI orchestration**.

NutriPrompt is a product-oriented AI system that demonstrates how modern intelligent applications can combine structured user data, domain knowledge, retrieval systems and resilient orchestration to create reliable, explainable and production-ready workflows.

![Python](https://img.shields.io/badge/Python-3.13-blue)
![Django](https://img.shields.io/badge/Django-5.x-green)
![OpenAI](https://img.shields.io/badge/OpenAI-API-black)
![Gemini](https://img.shields.io/badge/Gemini-AI-orange)
![OCR](https://img.shields.io/badge/OCR-Vision-purple)
![RAG](https://img.shields.io/badge/RAG-Knowledge%20Retrieval-red)

---

# ✨ Product Vision

Nutrition planning is not just a content generation problem.

A reliable AI nutrition system must understand:

* personal goals
* dietary restrictions
* digestive conditions
* ingredient compatibility
* nutritional context
* budget constraints
* real-life lifestyle habits

NutriPrompt approaches this challenge as an **intelligent decision-support workflow**, not as a simple AI chatbot.

Its architecture enriches every request before generation.

This produces:

✅ more reliable outputs
✅ fewer hallucinations
✅ explainable recommendations
✅ compatibility-aware suggestions
✅ resilient provider orchestration
✅ production-oriented AI workflows

---

# 🎯 Problem Statement

Most AI nutrition tools rely on direct prompting.

This creates critical limitations:

* no domain grounding
* weak restriction handling
* no ingredient validation
* no compatibility analysis
* no retrieval logic
* no fallback architecture

For healthcare-adjacent workflows, this is not enough.

NutriPrompt addresses this gap.

---

# 💡 Solution

NutriPrompt introduces a layered AI workflow that combines:

* Prompt Engineering
* Retrieval-Augmented Generation (RAG)
* OCR-based document analysis
* Nutrition knowledge systems
* Compatibility engines
* Multi-provider AI orchestration

Instead of sending raw user input directly to a language model, NutriPrompt enriches every request through multiple intelligence layers.

This improves:

* contextual consistency
* explainability
* reliability
* resilience

---

# 🏗 System Architecture

```text
User Input
      ↓
Structured Forms
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
Compatibility Analysis
      ↓
HTML Rendering
      ↓
PDF Generation
```

---

# 📸 Product Walkthrough · Django Application

## 1. Smart Nutrition Intake

NutriPrompt transforms structured user information into personalized nutrition plans through:

* goal understanding
* food preferences
* digestive symptoms
* dietary restrictions
* budget-aware logic

![Home](docs/screenshots/home.png)

---

## 2. OCR + Nutrition Intelligence

NutriPrompt Vision analyzes:

* product labels
* pantry inventories
* fridge contents
* nutrition PDFs

Combining OCR extraction with nutrition-specific compatibility logic.

![Vision](docs/screenshots/vision.png)

---

## 3. Intelligence Dashboard

A product-oriented observability layer designed to explain the AI workflow.

### Dashboard Overview

![Dashboard Overview](docs/screenshots/dashboard-top.png)

### AI Workflow Pipeline

![Dashboard Pipeline](docs/screenshots/dashboard-pipeline.png)

---

## 4. Generated Nutrition Plan

Final output includes:

* personalized weekly meal planning
* structured recommendations
* smart shopping logic
* compatibility insights
* downloadable PDF

![Generated Plan](docs/screenshots/result-plan.png)

---

# 🚀 Streamlit Technical Demo

NutriPrompt also includes a dedicated **Streamlit demo** built to showcase the internal AI workflow in a simplified and recruiter-friendly way.

This demo simulates the orchestration layer and explains the system logic step-by-step.

It is designed for:

* technical presentations
* architecture walkthroughs
* AI product demonstrations
* portfolio storytelling

---

## Intake Layer

Structured nutrition intake.

![Intake](docs/streamlit_demo/01_Intake.png)

---

## AI Workflow Orchestration

Full end-to-end AI pipeline.

![Workflow](docs/streamlit_demo/02_AI_Workflow.png)

---

## OCR Intelligence Layer

Ingredient extraction and incompatibility detection.

![OCR](docs/streamlit_demo/03_Vision_OCR.png)

---

## Structured Output Layer

Weekly plan generation.

![Plan](docs/streamlit_demo/04_Plan.png)

---

## Technical Dashboard

Stack overview and workflow observability.

![Dashboard](docs/streamlit_demo/05_Dashboard.png)

---

# 🧠 Core Capabilities

## Personalized Nutrition Planning

Generate structured weekly plans based on:

* user objectives
* dietary restrictions
* symptoms
* food preferences
* activity levels
* budget

---

## Retrieval-Augmented Generation (RAG)

Before generation, NutriPrompt retrieves contextual nutrition rules.

Examples:

* Low FODMAP recommendations
* gluten-free alternatives
* lactose-free substitutions
* digestive-safe planning
* shopping optimization logic

This improves consistency and reduces hallucinations.

---

## OCR + Ingredient Intelligence

NutriPrompt can analyze:

* product labels
* nutrition PDFs
* pantry inventories
* fridge scans

OCR results are cross-validated against user restrictions.

---

## Compatibility Engine

NutriPrompt evaluates:

* user restrictions
* retrieved nutrition rules
* OCR-detected ingredients

to detect incompatibilities before recommendation.

---

# ⚡ Resilient AI Orchestration

NutriPrompt implements fault-tolerant provider logic:

```text
Gemini API
      ↓
OpenAI Fallback
      ↓
Structured Mock Generation
```

Benefits:

* stable demos
* graceful degradation
* provider independence
* predictable outputs

---

# 🧠 AI Engineering Concepts Demonstrated

This project showcases practical implementation of:

* Prompt Engineering
* Retrieval-Augmented Generation (RAG)
* OCR Pipelines
* Multi-provider AI orchestration
* Structured AI outputs
* Explainable AI workflows
* Rule-based reasoning
* Compatibility engines
* Product-oriented AI design
* Service-oriented architecture
* Resilient fallback systems

---

# ⚙️ Technology Stack

| Layer         | Technology              |
| ------------- | ----------------------- |
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
├── scripts/
│   └── nutriprompt_demo.py
│
├── docs/
│   ├── screenshots/
│   └── streamlit_demo/
```

---

# 🧪 Test Coverage

Current automated validation includes:

* prompt generation
* knowledge base loading
* RAG retrieval
* compatibility analysis
* OCR logic
* context injection
* structured output generation

Run tests:

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

pip install -r requirements.txt
```

---

# ▶️ Run Django App

```bash
python manage.py runserver
```

Open:

```text
http://127.0.0.1:8000/
```

---

# ▶️ Run Streamlit Demo

```bash
streamlit run ./scripts/nutriprompt_demo.py
```

---

# ⚠️ Disclaimer

NutriPrompt provides informational guidance only.

It does not replace professional medical, nutritional or healthcare advice.

All outputs should be reviewed by qualified professionals when appropriate.

---

# 👩‍💻 Author

**Bea Lamiquiz**

🌐 Portfolio: https://bchill.net
💻 GitHub: https://github.com/beatriangu
💼 LinkedIn: https://www.linkedin.com/in/bealamiquiz/

---

# ⭐ Support

If you find this project interesting:

⭐ Star the repository
🤝 Connect on LinkedIn
💬 Share feedback, ideas or improvements







