# 🥦 NutriPrompt — AI-Powered Nutritional Plan Generator

<img src="https://raw.githubusercontent.com/beatriangu/nutriprompt/main/nutriprompt1.png" width="260" alt="NutriPrompt logo">

---

## 🧠 What is NutriPrompt?

NutriPrompt is an **AI-powered web application** that transforms structured user input into **personalized weekly nutrition plans** using:

- Prompt Engineering
- Generative AI (Google Gemini + OpenAI fallback)
- Django backend
- Structured data (JSON → HTML → PDF)

👉 It evolved from a simple prompt generator into a **fully functional AI product**.

---

## 🎯 Problem It Solves

Creating personalized nutrition plans requires:

- Collecting user data  
- Structuring information correctly  
- Designing effective prompts  
- Generating consistent outputs  

❌ Time-consuming  
❌ Highly dependent on prompt quality  

👉 NutriPrompt automates the entire workflow end-to-end.

---

## 🚀 Current Workflow


User Form → Django Backend → Prompt Generator → AI → JSON → HTML → PDF


### 🔹 Step-by-step:

1. User fills out a form  
2. System builds a structured prompt  
3. Prompt is sent to AI provider  
4. AI generates structured JSON  
5. JSON is rendered into HTML  
6. Plan is exported as downloadable PDF  

---

## 🤖 AI Architecture (Key Feature)

NutriPrompt uses a **multi-provider fallback system**:


Gemini (primary) → OpenAI (fallback) → Mock (optional demo mode)


### Why this matters:

- ✅ Improves reliability  
- ✅ Handles API failures gracefully  
- ✅ Ensures consistent UX  
- ✅ Demonstrates production-ready architecture  

---

## 💥 Key Features

- 🧾 Dynamic form (Django)
- 🧠 Automated prompt generation
- 🤖 Multi-AI integration (Gemini + OpenAI)
- 📊 Structured output (JSON → HTML)
- 📄 PDF generation (WeasyPrint)
- ⚠️ Intelligent fallback system
- 🎨 Clean and product-oriented UI

---

## 🧪 Example

**Input:**

Goal: Weekly organization
Restrictions: Lactose-free, low FODMAP
Preferences: Chicken, fish


**Output:**

✔ Full weekly plan  
✔ Adapted to restrictions  
✔ Structured by days  
✔ Downloadable as PDF  

---

## 🧠 Tech Stack

- **Backend:** Django  
- **Language:** Python 3  
- **AI:** Google Gemini API + OpenAI API  
- **Frontend:** HTML + CSS  
- **PDF:** WeasyPrint  
- **Data Handling:** JSON  
- **Prompt Engineering:** Structured design  

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

## 🔗 Integrations

NutriPrompt integrates with:

- **Google Colab** → experimentation and prompt validation  
- **Notion API** → structured data workflows  
- **Gemini API** → primary AI engine  
- **OpenAI API** → fallback AI provider  

---

## ⚙️ Workflow (Technical)

- Input data is collected (form / structured text)  
- Prompt is dynamically generated  
- AI model produces structured JSON  
- JSON is transformed into HTML  
- HTML is converted into a downloadable PDF  

---

## 🧪 Demo Mode

If AI providers are unavailable, you can enable demo mode:

```python
DEMO_MODE_FALLBACK = True

👉 This ensures the app always returns a valid plan (useful for demos & portfolio).

📁 Project Structure
nutriprompt/
├── nutriprompt_app/
│   ├── services/        # AI logic (Gemini + OpenAI)
│   ├── templates/       # UI
│   ├── views.py         # Main flow
│   └── ...
├── nutriprompt_web/     # Django config
├── media/
│   ├── formularios/
│   └── resultados/
├── colab/               # AI experiments
├── prototypes/          # Alternative versions
├── examples/            # Real anonymized data
└── README.md
🧠 Project Evolution

This project reflects a real development journey:

✅ Phase 1 — Manual prompting
✅ Phase 2 — Python automation
✅ Phase 3 — Colab prototyping
✅ Phase 4 — AI integration (Gemini)
🚀 Phase 5 — Multi-AI system + full web app
🧠 Product Decisions
Why Prompt Engineering?
Full control over output
No need for model fine-tuning
Fast iteration
Why Django?
Full backend control
Scalable architecture
Easy integration with AI services
Why a fallback system?
AI services can fail (quota / latency / overload)
The system remains usable → better UX
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

✔ Real-world AI integration
✔ Advanced Prompt Engineering
✔ Backend architecture (Django)
✔ Product thinking
✔ Resilient system design (fallback logic)
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


