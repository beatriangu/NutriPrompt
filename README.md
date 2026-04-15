🥦 NutriPrompt — AI-Powered Nutritional Plan Generator
<img src="https://raw.githubusercontent.com/beatriangu/nutriprompt/main/nutriprompt1.png" width="260" alt="NutriPrompt logo">








🧠 What is NutriPrompt?

NutriPrompt is an AI-powered system that transforms user input into personalized weekly nutrition plans using:

Prompt Engineering
Generative AI (Google Gemini)
Django backend
Structured data (JSON → HTML → PDF)

👉 It evolved from a prompt generator into a fully functional product.

🎯 Problem It Solves

Creating personalized nutrition plans requires:

Collecting user data
Structuring information correctly
Designing effective prompts
Generating high-quality outputs

❌ Time-consuming
❌ Highly dependent on prompt quality

👉 NutriPrompt automates the entire workflow end-to-end

🚀 Current Workflow
User Form → Django Backend → Prompt Generator → Gemini API → JSON → HTML → PDF
🔹 Step-by-step:
User fills out a form
System builds a structured prompt
Prompt is sent to Gemini API
AI generates structured JSON
JSON is rendered into HTML
Plan is exported as downloadable PDF
💥 Key Features
🧾 Dynamic form (Django)
🧠 Automated prompt generation
🤖 Gemini API integration
📊 Structured output (JSON → HTML)
📄 PDF generation (WeasyPrint)
⚠️ Fallback system if AI fails
🎨 Clean and product-oriented UI
🧪 Example
Input:
Goal: Weekly organization  
Restrictions: Lactose-free, low FODMAP  
Preferences: Chicken, fish  
Output:

✔ Full weekly plan
✔ Adapted to restrictions
✔ Structured by days
✔ Downloadable as PDF

🧠 Tech Stack
Backend: Django
Language: Python 3
AI: Google Gemini API
Frontend: HTML + CSS
PDF: WeasyPrint
Data Handling: JSON + Pandas
Prompt Engineering: Structured design
🏗️ Architecture
User
 ↓
Django Form
 ↓
Prompt Generator
 ↓
Gemini API
 ↓
Structured JSON
 ↓
HTML Rendering
 ↓
PDF Output
🔗 Integrations

NutriPrompt integrates with:

Google Colab → experimentation and prompt validation
Notion API → structured data management (user inputs & workflows)
Gemini API → AI generation engine
⚙️ Workflow (Technical)
Input data is collected (form / structured text)
Prompt is dynamically generated
AI model produces structured JSON
JSON is transformed into HTML
HTML is converted into a downloadable PDF
📁 Project Structure
nutriprompt/
├── nutriprompt_app/
│   ├── services/        # AI logic (Gemini)
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
🚀 Phase 5 — Full web application (current)
🧠 Product Decisions
Why Prompt Engineering?
Full control over output
No need for fine-tuning
Fast iteration
Why Django?
Full backend control
Scalable architecture
Easy AI integration
Why fallback system?
AI can fail (quota / latency)
System remains usable → better UX
⚙️ Installation
git clone https://github.com/beatriangu/nutriprompt.git
cd nutriprompt

python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt
Environment variables (.env)
GOOGLE_API_KEY=your_api_key
DJANGO_SECRET_KEY=your_secret_key
DEBUG=True
Run the project
python manage.py runserver

👉 http://127.0.0.1:8000/

🎯 Professional Value

This project demonstrates:

✔ Real AI integration
✔ Advanced prompt engineering
✔ Backend architecture (Django)
✔ Product thinking
✔ UX resilience (fallback system)

⚠️ Disclaimer

This system provides informational recommendations only
and does not replace professional medical advice.

👩‍💻 Author

Bea Lamiquiz

🌐 Portfolio: https://bchill.net
💻 GitHub: https://github.com/beatriangu
💼 LinkedIn: https://www.linkedin.com/in/bealamiquiz/
⭐ If you like it
Give it a star
Connect with me
Or share ideas 🚀


