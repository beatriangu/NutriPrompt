# 🥦 NutriPrompt

> AI-powered nutrition intelligence platform that combines Prompt Engineering, Retrieval-Augmented Generation (RAG), OCR workflows and nutrition compatibility analysis to transform structured user data into personalized weekly nutrition plans.

![NutriPrompt Banner](nutriprompt.png)

![Python](https://img.shields.io/badge/Python-3.13-blue)
![Django](https://img.shields.io/badge/Django-5.x-green)
![OpenAI](https://img.shields.io/badge/OpenAI-API-black)
![Gemini](https://img.shields.io/badge/Gemini-AI-orange)
![OCR](https://img.shields.io/badge/OCR-Vision-purple)
![RAG](https://img.shields.io/badge/RAG-Nutrition%20Knowledge-red)

---

# ✨ Overview

NutriPrompt is an AI-powered nutrition workflow platform designed to demonstrate how modern intelligent applications combine structured data, domain knowledge and AI orchestration to generate consistent, contextualized outputs.

Rather than generating content directly from a prompt, NutriPrompt enriches every request with nutrition rules, dietary restrictions, OCR-extracted information and compatibility analysis.

The result is a more controlled and explainable AI workflow.

---

# 🎯 Problem

Generating nutrition plans with AI is not simply a text generation problem.

A reliable system must be able to:

* Understand user goals and dietary restrictions
* Interpret nutrition forms and documents
* Detect potentially conflicting ingredients
* Incorporate domain knowledge consistently
* Generate structured outputs suitable for real workflows

Large Language Models alone do not guarantee this consistency.

---

# 💡 Solution

NutriPrompt introduces a layered AI architecture that combines:

* Prompt Engineering
* Retrieval-Augmented Generation (RAG)
* OCR-based information extraction
* Rule-based nutrition intelligence
* Compatibility analysis
* Multi-provider AI orchestration

This allows the platform to generate personalized plans while reducing contradictions and improving contextual consistency.

---

# 🧠 Core Capabilities

### Personalized Nutrition Planning

Generate structured weekly plans based on:

* User objectives
* Dietary restrictions
* Food preferences
* Budget considerations
* Lifestyle context

### Nutrition Knowledge Retrieval (RAG)

Before generating a response, NutriPrompt retrieves relevant nutrition rules from its knowledge base.

Examples:

* Low FODMAP guidance
* Gluten-free guidance
* Lactose-free guidance
* Planning recommendations
* Shopping logic

This context is injected into the prompt to improve consistency and reduce hallucinations.

### OCR & Nutrition Intelligence

The platform can analyze:

* Nutrition PDFs
* Product labels
* Pantry inventories
* Fridge contents

OCR extraction is combined with nutrition rules to identify ingredients that may require review.

### Compatibility Analysis

NutriPrompt compares:

* User restrictions
* Retrieved nutrition rules
* OCR-detected ingredients

to identify potential incompatibilities before generating recommendations.

---

# 🏗 System Architecture

```text
User Input
      ↓
Django Forms
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

# 🧠 AI Engineering Concepts Demonstrated

This project showcases practical implementation of:

* Prompt Engineering
* Retrieval-Augmented Generation (RAG)
* Multi-provider AI orchestration
* OCR pipelines
* Rule-based reasoning
* Structured AI outputs
* Nutrition compatibility systems
* Product-oriented AI architecture
* Resilient fallback workflows
* Explainable AI pipelines

---

# ⚡ Resilient AI Orchestration

NutriPrompt implements a fault-tolerant generation workflow:

```text
Gemini API
      ↓
OpenAI Fallback
      ↓
Structured Mock Generation
```

This guarantees:

* Stable demonstrations
* Consistent user experience
* Graceful degradation
* Continuous workflow execution

---

# ⚙️ Technology Stack

| Layer        | Technology              |
| ------------ | ----------------------- |
| Backend      | Django                  |
| Language     | Python 3.13             |
| AI Providers | Gemini API + OpenAI API |
| Retrieval    | Custom Nutrition RAG    |
| OCR          | Tesseract OCR           |
| Data         | JSON                    |
| PDF          | WeasyPrint              |
| Frontend     | HTML + CSS              |
| Testing      | Django Test Framework   |
| Architecture | Service-Oriented Design |

---

# 📁 Project Structure

```text
nutriprompt_app/
├── services/
│   ├── ai/
│   ├── nutrition/
│   ├── profiles/
│   ├── rag/
│   ├── vision/
│   └── presentation/
├── templates/
├── tests/
└── views.py
```

---

# 🧪 Test Coverage

Current automated validation includes:

* Prompt generation
* JSON parsing
* Knowledge base loading
* RAG retrieval
* Context building
* Prompt enrichment
* Compatibility workflows

```bash
python manage.py test
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

# ▶️ Run

```bash
python manage.py runserver
```

Open:

```text
http://127.0.0.1:8000/
```

---

# ⚠️ Disclaimer

NutriPrompt provides informational guidance only.

It does not replace professional medical, nutritional or healthcare advice.

Any recommendation generated by the system should be reviewed by qualified professionals when appropriate.

---

# 👩‍💻 Author

**Bea Lamiquiz**

🌐 Portfolio: https://bchill.net
💻 GitHub: https://github.com/beatriangu
💼 LinkedIn: https://www.linkedin.com/in/bealamiquiz/

---

# ⭐ Support

If you find the project interesting:

⭐ Star the repository
🤝 Connect on LinkedIn
💬 Share feedback or ideas




