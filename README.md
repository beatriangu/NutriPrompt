🥦 NutriPrompt — AI-Powered Nutritional Plan Generator
<img src="https://raw.githubusercontent.com/beatriangu/nutriprompt/main/nutriprompt1.png" width="260" alt="NutriPrompt logo">
🧠 Overview

NutriPrompt is a production-oriented AI web application that transforms structured user input into personalized weekly nutrition plans.

It combines:

Prompt Engineering
Generative AI (Google Gemini + OpenAI fallback)
Django backend architecture
Structured data pipelines (JSON → HTML → PDF)

👉 Built as a real AI product, not just a demo.

🎯 Problem

Creating personalized nutrition plans requires:

Collecting structured user data
Designing high-quality prompts
Ensuring consistent outputs
Adapting to real-life constraints (budget, time, context)

❌ Time-consuming
❌ Hard to scale
❌ Highly dependent on prompt quality

👉 NutriPrompt automates the entire workflow end-to-end.

🚀 Product Experience
User Form → Backend → Prompt → AI → JSON → HTML → PDF
What the user gets:

✔ Weekly structured plan
✔ Context-aware recommendations
✔ Shopping list
✔ Clean visual output
✔ Downloadable PDF

🤖 AI Architecture (Core Innovation)

NutriPrompt uses a multi-provider fallback system:

Gemini (primary) → OpenAI (fallback) → Mock (demo mode)
Why this matters:
✅ High reliability
✅ Graceful degradation
✅ Consistent UX
✅ Production-ready mindset
💡 Key Features
🧾 Guided dynamic form (UX-focused)
🧠 Automated prompt generation
🤖 Multi-AI integration (Gemini + OpenAI)
📊 Structured output (JSON-based)
📄 PDF generation (WeasyPrint)
⚠️ Intelligent fallback system
🎨 Product-level UI/UX
🧪 Example

Input

Goal: Weight loss
Restrictions: Gluten-free
Preferences: Eggs

Output

✔ Weekly meal plan
✔ Adapted to constraints
✔ Structured by days
✔ Shopping list generated
✔ Exportable as PDF

🧠 Tech Stack
Backend: Django
Language: Python 3
AI: Google Gemini API + OpenAI API
Frontend: HTML + CSS
PDF: WeasyPrint
Data: JSON
Approach: Prompt Engineering
🏗️ Architecture
User
↓
Django Form
↓
Prompt Generator
↓
AI Providers (Gemini → OpenAI)
↓
Structured JSON
↓
HTML Rendering
↓
PDF Output
🔗 Integrations
Google Colab → prompt experimentation
Notion API → structured workflows
Gemini API → primary AI engine
OpenAI API → fallback provider
⚙️ Technical Workflow
User input is collected via form
Prompt is dynamically generated
AI produces structured JSON
JSON is transformed into HTML
HTML is converted into PDF
🧪 Demo Mode
DEMO_MODE_FALLBACK = True

👉 Ensures the app always returns a valid result
(ideal for demos, presentations and portfolio)

📁 Project Structure
nutriprompt/
├── nutriprompt_app/
│   ├── services/        # AI logic
│   ├── templates/       # UI
│   ├── views.py         # Core flow
│   └── ...
├── nutriprompt_web/     # Django config
├── media/
├── colab/               # Experiments
├── prototypes/
├── examples/
└── README.md
🧠 Project Evolution
Phase 1 — Manual prompting
Phase 2 — Python automation
Phase 3 — Colab prototyping
Phase 4 — Gemini integration
Phase 5 — Multi-AI + full web app

👉 Evolution from prompt tool → AI product

🧠 Product Thinking

Why Prompt Engineering?

Full control over output
No fine-tuning needed
Fast iteration

Why Django?

Full backend control
Scalable structure
Easy AI integration

Why fallback architecture?

AI APIs fail (quota, latency, overload)
UX must remain stable
⚙️ Installation
git clone https://github.com/beatriangu/nutriprompt.git
cd nutriprompt

python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt
Environment variables (.env)
GOOGLE_API_KEY=your_api_key
OPENAI_API_KEY=your_api_key
DJANGO_SECRET_KEY=your_secret_key
DEBUG=True
▶️ Run the project
python manage.py runserver

👉 http://127.0.0.1:8000/

🎯 Professional Value

This project demonstrates:

✔ AI integration in real workflows
✔ Advanced Prompt Engineering
✔ Backend architecture (Django)
✔ Product thinking & UX
✔ Resilient system design

⚠️ Disclaimer

This system provides informational recommendations only
and does not replace professional medical or nutritional advice.

👩‍💻 Author

Bea Lamiquiz

🌐 Portfolio: https://bchill.net

💻 GitHub: https://github.com/beatriangu

💼 LinkedIn: https://www.linkedin.com/in/bealamiquiz/

⭐ If you like it

Give it a star ⭐
Connect with me
Or share ideas 🚀


