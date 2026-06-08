# 🥦 NutriPrompt

> AI-powered nutrition intelligence platform combining Prompt Engineering, OCR, computer vision workflows and structured AI orchestration.

![NutriPrompt Banner](nutriprompt.png)

![Python](https://img.shields.io/badge/Python-3.13-blue)
![Django](https://img.shields.io/badge/Django-5.x-green)
![OpenAI](https://img.shields.io/badge/OpenAI-API-black)
![Gemini](https://img.shields.io/badge/Gemini-AI-orange)
![OCR](https://img.shields.io/badge/OCR-Vision-purple)
![Prompt Engineering](https://img.shields.io/badge/AI-Prompt%20Engineering-red)

---

# 🚀 NutriPrompt Vision

NutriPrompt is an AI-powered nutrition workflow platform designed to simulate how modern intelligent SaaS systems process:

* Structured nutrition forms
* OCR document interpretation
* Food label analysis
* Pantry and fridge recognition
* AI-generated meal planning
* Compatibility analysis between dietary plans and available foods

The project combines:

* Prompt Engineering
* AI orchestration
* OCR pipelines
* Nutrition intelligence
* Rule-based reasoning
* Structured outputs
* Product-oriented UX

---

# ✨ Core Product Vision

NutriPrompt is evolving beyond simple meal generation.

The goal is to create an intelligent nutrition assistant capable of understanding:

✅ What the user should eat
✅ What the user already has available
✅ What products are compatible with the nutritional plan
✅ What ingredients may conflict with dietary restrictions

---

# 🧠 Main Features

| Feature                           | Description                                                        |
| --------------------------------- | ------------------------------------------------------------------ |
| 🧠 Prompt Engineering             | Dynamic prompt generation from structured nutrition forms          |
| 🤖 Multi-AI Architecture          | Gemini + OpenAI resilient orchestration                            |
| 📄 OCR Nutrition Vision           | Extracts information from labels, products and nutrition documents |
| 🧊 Pantry & Fridge Analysis       | Detects available foods from uploaded images                       |
| ⚠️ Nutrition Compatibility Engine | Compares foods against nutritional restrictions                    |
| 📊 Structured JSON Outputs        | AI responses normalized into structured data                       |
| 📄 PDF Export                     | Printable nutrition plans                                          |
| 🛒 Smart Shopping Logic           | Generates contextual shopping suggestions                          |
| 🎨 AI Product UX                  | Modern responsive interface with AI workflows                      |
| 🧱 Resilient System Design        | Graceful degradation and fallback flows                            |

---

# 🧠 Smart Intake Compatibility System

NutriPrompt can combine multiple sources simultaneously:

```text
Nutrition PDF
      +
Pantry / Fridge Images
      +
Product Labels
      ↓
AI Compatibility Analysis
      ↓
Contextual Nutrition Guidance
```

Example workflow:

```text
PDF:
- Low FODMAP
- Lactose free

Fridge:
- Chicken
- Rice
- Yogurt

Product:
- Onion soup

Result:
⚠️ Onion soup may not be compatible
✅ Chicken and rice appear compatible
💡 Suggest lactose-free alternatives
```

---

# 🧩 System Architecture

```text
User Input
    ↓
Django Forms
    ↓
Prompt Builder
    ↓
Gemini API
    ↓ (fallback)
OpenAI API
    ↓
Structured JSON
    ↓
Nutrition Rules Engine
    ↓
OCR + Vision Analysis
    ↓
Compatibility Analysis
    ↓
HTML Rendering
    ↓
PDF Generation
```

---

# 🧠 AI Engineering Concepts Demonstrated

This project demonstrates practical implementation of:

* Prompt Engineering
* AI orchestration
* OCR pipelines
* Structured AI outputs
* Backend architecture with Django
* Product-oriented AI development
* Resilient fallback systems
* Nutrition rule engines
* Computer vision workflows
* Multi-context AI reasoning
* AI-assisted UX design

---

# 📸 Vision Module

NutriPrompt Vision supports:

✅ Product labels
✅ Pantry images
✅ Fridge analysis
✅ Nutrition PDFs
✅ OCR text extraction
✅ Nutrition alerts
✅ Restriction compatibility analysis

Supported analysis categories:

* Low FODMAP
* Lactose-free
* Gluten-free
* Ingredient warnings
* Nutritional compatibility checks

---

# 📊 Kaggle Nutrition Dataset Integration

NutriPrompt integrates nutrition datasets to enrich food analysis and future recommendation systems.

Current integration includes:

* Food nutritional values
* Macronutrients
* Sodium analysis
* Fiber analysis
* Nutrition density

Dataset source:

* Kaggle Food Nutrition Dataset

---

# ⚡ Resilient AI Orchestration

NutriPrompt uses a resilient provider architecture:

```text
Gemini API
   ↓
OpenAI Fallback
   ↓
Structured Mock Mode
```

This guarantees:

* Stable demos
* Reliable UX
* Graceful degradation
* Continuous workflow generation

---

# ⚙️ Tech Stack

| Layer           | Technology              |
| --------------- | ----------------------- |
| Backend         | Django                  |
| Language        | Python 3.13             |
| AI Providers    | Gemini API + OpenAI API |
| OCR             | Tesseract OCR           |
| Frontend        | HTML + CSS              |
| PDF Engine      | WeasyPrint              |
| Data Handling   | JSON                    |
| AI Methodology  | Prompt Engineering      |
| Nutrition Logic | Rule-based analysis     |
| Vision Pipeline | OCR + AI analysis       |

---

# 🛠️ Installation

```bash
git clone https://github.com/beatriangu/NutriPrompt.git

cd NutriPrompt

python3 -m venv venv

source venv/bin/activate

pip install -r requirements.txt
```

---

# 🔐 Environment Variables

Create a `.env` file:

```env
GOOGLE_API_KEY=your_api_key
OPENAI_API_KEY=your_api_key
DJANGO_SECRET_KEY=your_secret_key
DEBUG=True
```

---

# ▶️ Run the Project

```bash
python manage.py runserver
```

Open:

```text
http://127.0.0.1:8000/
```

---

# 🧪 Demo Mode

NutriPrompt includes resilient fallback generation for demos and portfolio presentations.

```python
DEMO_MODE_FALLBACK = True
```

This ensures stable outputs even if AI providers fail.

---

# 📁 Project Structure

```text
NutriPrompt/
├── nutriprompt_app/
│   ├── services/
│   │   ├── ai/
│   │   ├── nutrition/
│   │   ├── vision/
│   │   └── presentation/
│   ├── templates/
│   ├── tests/
│   ├── views.py
│   └── ...
├── nutriprompt_web/
├── media/
├── data/
├── docs/
├── static/
└── README.md
```

---

# ⚠️ Disclaimer

NutriPrompt provides informational guidance only.

It does not replace professional medical, nutritional or healthcare advice.

Any nutritional recommendation generated by the system should be reviewed by qualified professionals whenever necessary.

---

# 👩‍💻 Author

## Bea Lamiquiz

🌐 Portfolio: https://bchill.net
💻 GitHub: https://github.com/beatriangu
💼 LinkedIn: https://www.linkedin.com/in/bealamiquiz/

---

# ⭐ Support

If you like the project:

⭐ Star the repository
🤝 Connect on LinkedIn
💬 Share feedback or ideas



