🥦 NutriPrompt

AI-powered nutrition intelligence platform designed to transform structured health data into contextualized, explainable and actionable nutrition plans.

Built with Django, Prompt Engineering, Retrieval-Augmented Generation (RAG), OCR pipelines, compatibility engines and multi-provider AI orchestration.

NutriPrompt is a product-oriented AI system that demonstrates how modern intelligent applications can combine structured user data, domain knowledge, retrieval systems and resilient orchestration to create reliable, explainable and production-ready nutrition workflows.












✨ Product Vision

Nutrition planning is not just a content generation problem.

A reliable AI nutrition system must understand:

personal goals
dietary restrictions
digestive conditions
ingredient compatibility
nutritional context
budget constraints
real-life lifestyle habits

NutriPrompt approaches this challenge as an intelligent decision-support workflow, not as a simple AI chatbot.

Its architecture enriches every request before generation.

This produces:

✅ more reliable outputs
✅ fewer hallucinations
✅ explainable recommendations
✅ compatibility-aware suggestions
✅ resilient provider orchestration
✅ production-oriented AI workflows

🎯 Problem Statement

Most AI nutrition tools rely on direct prompting.

This creates critical limitations:

no domain grounding
weak restriction handling
no ingredient validation
no compatibility analysis
no retrieval logic
no fallback architecture

For healthcare-adjacent workflows, this is not enough.

NutriPrompt addresses this gap.

💡 Solution

NutriPrompt introduces a layered AI workflow that combines:

Prompt Engineering
Retrieval-Augmented Generation (RAG)
OCR-based document analysis
Nutrition knowledge systems
Compatibility engines
Multi-provider AI orchestration

Instead of sending raw user input directly to a language model, NutriPrompt enriches every request through multiple intelligence layers.

This improves:

contextual consistency
explainability
reliability
resilience
🏗 System Architecture
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
Shopping Intelligence
      ↓
PDF Generation
📸 Product Walkthrough · Django Application
1. Smart Nutrition Intake

NutriPrompt transforms structured user information into personalized nutrition plans through:

goal understanding
food preferences
digestive symptoms
dietary restrictions
budget-aware logic
real-life context

2. Generated Nutrition Plan

The AI output includes:

structured weekly meal planning
compatibility-aware recommendations
personalized meal logic
practical tupper adaptation
explainable profile tags
downloadable PDF

3. Intelligent Shopping List

NutriPrompt automatically transforms the generated plan into an organized shopping list:

grouped by category
structured by nutritional logic
optimized for planning
practical for real-life execution

This post-processing layer turns AI output into actionable utility.

🚀 Streamlit Technical Demo

NutriPrompt also includes a dedicated Streamlit demo built to showcase the internal AI workflow in a simplified and recruiter-friendly way.

This demo simulates the orchestration layer and explains the system logic step-by-step.

It is designed for:

technical presentations
architecture walkthroughs
AI product demonstrations
portfolio storytelling
Intake Layer

Structured nutrition intake.

AI Workflow Orchestration

Full end-to-end AI pipeline.

OCR Intelligence Layer

Ingredient extraction and incompatibility detection.

Structured Output Layer

Weekly plan generation.

Technical Dashboard

Stack overview and workflow observability.

AI Copilot Layer

NutriPrompt includes an explainability assistant capable of:

explaining generated plans
reviewing dietary restrictions
validating ingredient compatibility
providing contextual reasoning to the user

This transforms NutriPrompt from a generator into an interactive AI decision-support system.

🧠 Core Capabilities
Personalized Nutrition Planning

Generate structured weekly plans based on:

user objectives
dietary restrictions
symptoms
food preferences
activity levels
budget
daily routines
Retrieval-Augmented Generation (RAG)

Before generation, NutriPrompt retrieves contextual nutrition rules.

Examples:

Low FODMAP recommendations
gluten-free alternatives
lactose-free substitutions
digestive-safe planning
shopping optimization logic

This improves consistency and reduces hallucinations.

OCR + Ingredient Intelligence

NutriPrompt can analyze:

product labels
nutrition PDFs
pantry inventories
fridge scans
ingredient lists

OCR results are cross-validated against user restrictions.

Compatibility Engine

NutriPrompt evaluates:

user restrictions
retrieved nutrition rules
OCR-detected ingredients

to detect incompatibilities before recommendation.

Shopping Intelligence Layer

Generated plans are transformed into categorized shopping lists.

This creates:

better planning
practical usability
easier execution
lower friction for the user
⚡ Resilient AI Orchestration

NutriPrompt implements fault-tolerant provider logic:

Gemini API
      ↓
OpenAI Fallback
      ↓
Structured Mock Generation

Benefits:

stable demos
graceful degradation
provider independence
predictable outputs
🧠 AI Engineering Concepts Demonstrated

This project showcases practical implementation of:

Prompt Engineering
Retrieval-Augmented Generation (RAG)
OCR Pipelines
Multi-provider AI orchestration
Structured AI outputs
Explainable AI workflows
Rule-based reasoning
Compatibility engines
Shopping intelligence
Product-oriented AI design
Service-oriented architecture
Resilient fallback systems
⚙️ Technology Stack
Layer	Technology
Backend	Django
Language	Python 3.13
AI Providers	Gemini API + OpenAI API
Retrieval	Custom Nutrition RAG
OCR	Tesseract OCR
Data	JSON
PDF Rendering	WeasyPrint
Frontend	HTML + CSS
Demo Layer	Streamlit
Testing	Django Test Framework
Architecture	Service-Oriented Design
📁 Project Structure
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
│   │   ├── 01_home.png
│   │   ├── 02_plan.png
│   │   └── 03_shopping_list.png
│   └── streamlit_demo/
🧪 Test Coverage

Current automated validation includes:

prompt generation
knowledge base loading
RAG retrieval
compatibility analysis
OCR logic
context injection
structured output generation
shopping list generation

Run tests:

python manage.py test

Current suite:

17 automated tests passing
🛠 Installation
git clone https://github.com/beatriangu/NutriPrompt.git
cd NutriPrompt

python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt
▶️ Run Django App
python manage.py runserver

Open:

http://127.0.0.1:8000/
▶️ Run Streamlit Demo
streamlit run ./scripts/nutriprompt_demo.py
⚠️ Disclaimer

NutriPrompt provides informational guidance only.

It does not replace professional medical, nutritional or healthcare advice.

All outputs should be reviewed by qualified professionals when appropriate.

👩‍💻 Author

Bea Lamiquiz

🌐 Portfolio: https://bchill.net
💻 GitHub: https://github.com/beatriangu
💼 LinkedIn: https://www.linkedin.com/in/bealamiquiz/

⭐ Support

If you find this project interesting:

⭐ Star the repository
🤝 Connect on LinkedIn
💬 Share feedback, ideas or improvements