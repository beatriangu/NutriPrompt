# 🥦 NutriPrompt

> From user form to AI-generated nutrition workflows — structured, resilient and production-oriented.

![NutriPrompt Banner](nutriprompt.png)

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Django](https://img.shields.io/badge/Django-5.x-green)
![OpenAI](https://img.shields.io/badge/OpenAI-API-black)
![Gemini](https://img.shields.io/badge/Gemini-AI-orange)
![Prompt Engineering](https://img.shields.io/badge/AI-Prompt%20Engineering-purple)

---

# 🚀 Built as a Real-World AI Product Prototype

NutriPrompt was designed to simulate how modern AI-powered SaaS systems handle:

- Structured prompting
- Provider fallback systems
- Output normalization
- AI orchestration
- PDF generation
- Resilient UX workflows

---

# ✨ Overview

NutriPrompt transforms structured user data into fully personalized weekly nutrition plans.

Built using:

- Prompt Engineering
- Multi-model AI orchestration
- Structured JSON workflows
- Django backend architecture

The system automatically:

- Collects user goals and dietary constraints
- Generates optimized prompts dynamically
- Calls multiple AI providers
- Structures responses into JSON
- Renders clean HTML interfaces
- Exports downloadable PDFs

Designed with a production-oriented mindset focused on:

- Reliability
- Scalability
- Graceful degradation
- User experience
- Structured AI workflows

---

# 🚀 Core Features

| Feature | Description |
|---|---|
| 🧠 Prompt Engineering | Dynamic prompt generation from structured forms |
| 🤖 Multi-AI Providers | Gemini + OpenAI fallback architecture |
| 📊 Structured Output | AI responses normalized into JSON |
| 📄 PDF Export | Automatic printable weekly plans |
| ⚠️ Fallback System | Stable UX even if APIs fail |
| 🎨 Product UI | Clean responsive interface |
| 🛒 Shopping Lists | Auto-generated grocery planning |

---

# 🧩 System Architecture

```text
User Input
    ↓
Django Forms
    ↓
Prompt Generator
    ↓
Gemini API
    ↓ (fallback)
OpenAI API
    ↓
Structured JSON
    ↓
HTML Rendering
    ↓
PDF Generation
🧠 Why This Project Matters

Most AI demos stop at generating text.

NutriPrompt focuses on the real engineering challenges behind AI-powered products:

AI orchestration
Prompt optimization
Structured outputs
UX consistency
Backend reliability
Scalable architecture
Production-ready workflows

This project simulates how modern AI-powered SaaS systems are actually designed.

📸 Demo
User Form

(Add screenshot or GIF here)

Generated Weekly Plan

(Add screenshot here)

PDF Export

(Add screenshot here)

⚙️ Tech Stack
Layer	Technology
Backend	Django
Language	Python 3
AI Providers	Gemini API + OpenAI API
Frontend	HTML + CSS
PDF Engine	WeasyPrint
Data Format	JSON
AI Methodology	Prompt Engineering
⚡ Resilient AI Orchestration

NutriPrompt uses a resilient multi-provider architecture:

Gemini API
   ↓
OpenAI Fallback
   ↓
Demo Mock Mode

This ensures:

Graceful degradation
Stable demos
Improved reliability
Uninterrupted user experience
🛠️ Installation
git clone https://github.com/beatriangu/nutriprompt.git

cd nutriprompt

python3 -m venv venv

source venv/bin/activate

pip install -r requirements.txt
🔐 Environment Variables

Create a .env file:

GOOGLE_API_KEY=your_api_key
OPENAI_API_KEY=your_api_key
DJANGO_SECRET_KEY=your_secret_key
DEBUG=True
▶️ Run the Project
python manage.py runserver

Open:

http://127.0.0.1:8000/
🧪 Demo Mode
DEMO_MODE_FALLBACK = True

Ensures the application always produces valid output — ideal for demos and portfolio presentations.

📁 Project Structure
nutriprompt/
├── nutriprompt_app/
│   ├── services/
│   ├── templates/
│   ├── views.py
│   └── ...
├── nutriprompt_web/
├── media/
├── colab/
├── prototypes/
├── examples/
└── README.md
🧠 Engineering & Product Concepts Demonstrated
AI product architecture
Prompt Engineering
Backend engineering with Django
AI orchestration patterns
Structured AI outputs
Product-oriented thinking
UX-focused development
Resilient system design
⚠️ Disclaimer

This project provides informational recommendations only and does not replace professional medical or nutritional advice.

👩‍💻 Author

Bea Lamiquiz

🌐 Portfolio: https://bchill.net
💻 GitHub: https://github.com/beatriangu
💼 LinkedIn: https://www.linkedin.com/in/bealamiquiz/
⭐ Support

If you like the project:

Star the repository
Connect on LinkedIn
Share feedback


