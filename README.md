# 🥦 NutriPrompt

### AI-powered system that transforms structured user data into production-ready weekly nutrition plans using prompt engineering and multi-model AI orchestration.

![NutriPrompt Banner](nutriprompt.png)

---

## 📸 Demo

> *(Add screenshots or GIF here to showcase the real user experience)*

- Form input
- Generated weekly plan
- PDF output

---

## 🧠 What is NutriPrompt?

**NutriPrompt** is a production-oriented AI web application that transforms structured user input into **personalized weekly nutrition plans**.

👉 Built as a **real AI product**, not just a demo.

---

## 🚀 Product Experience

**User flow:**


User Input → Django Backend → Prompt Generation → AI → JSON → HTML → PDF


### ✔ What the user gets:

- Weekly structured meal plan  
- Context-aware recommendations  
- Auto-generated shopping list  
- Clean visual UI  
- Downloadable PDF  

---

## 🎯 The Problem

Creating personalized nutrition plans is:

- ❌ Time-consuming  
- ❌ Hard to scale  
- ❌ Highly dependent on prompt quality  

👉 **NutriPrompt automates the entire workflow end-to-end.**

---

## 🤖 AI Architecture (Core Innovation)

Multi-provider fallback system:


Gemini (primary)
↓
OpenAI (fallback)
↓
Mock mode (demo)


### ✅ Why this matters:

- High reliability  
- Graceful degradation  
- Stable UX  
- Production-ready mindset  

---

## 💡 Key Features

- 🧾 UX-focused dynamic form  
- 🧠 Automated prompt generation  
- 🤖 Multi-AI integration (Gemini + OpenAI)  
- 📊 Structured JSON output  
- 📄 PDF generation (WeasyPrint)  
- ⚠️ Intelligent fallback system  
- 🎨 Clean product UI  

---

## 🧪 Example

**Input:**

- Goal: Weight loss  
- Restrictions: Gluten-free  
- Preferences: Eggs  

**Output:**

- ✔ Weekly meal plan  
- ✔ Adapted to constraints  
- ✔ Structured by days  
- ✔ Shopping list  
- ✔ Exportable PDF  

---

## 🏗️ Architecture


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


---

## ⚙️ Tech Stack

- **Backend:** Django  
- **Language:** Python 3  
- **AI:** Google Gemini API + OpenAI API  
- **Frontend:** HTML + CSS  
- **PDF:** WeasyPrint  
- **Data:** JSON  
- **Approach:** Prompt Engineering  

---

## 🔗 Integrations

- Google Colab → Prompt experimentation  
- Notion API → Structured workflows  
- Gemini API → Primary AI engine  
- OpenAI API → Fallback provider  

---

## ⚙️ Installation

```bash
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

🧪 Demo Mode
DEMO_MODE_FALLBACK = True

👉 Ensures the app always returns a valid result (perfect for demos & portfolio)

📁 Project Structure
nutriprompt/
├── nutriprompt_app/
│   ├── services/        # AI logic
│   ├── templates/       # UI
│   ├── views.py         # Core flow
│   └── ...
├── nutriprompt_web/     # Django config
├── media/
├── colab/
├── prototypes/
├── examples/
└── README.md
🧠 Product Thinking

Why Prompt Engineering?

Full control over output
No fine-tuning required
Fast iteration

Why Django?

Scalable backend
Full control
Easy AI integration

Why fallback architecture?

AI APIs fail (quota, latency…)
UX must remain stable
🎯 Professional Value

This project demonstrates:

AI integration in real workflows
Advanced prompt engineering
Backend architecture (Django)
Product thinking & UX
Resilient system design
Ability to transform user needs into scalable AI-driven solutions
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


