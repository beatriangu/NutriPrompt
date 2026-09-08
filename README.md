# 🥦 NutriPrompt

> **NutriPrompt is an AI decision-support system designed to transform nutrition planning into a contextual, retrieved, validated and explainable workflow.**

NutriPrompt is not simply a meal-plan generator.

It is a production-minded Applied AI project built to explore how modern GenAI products can move beyond open-ended prompting into structured, domain-grounded and resilient workflows.

The system combines:

- structured user context
- domain-specific Retrieval-Augmented Generation (RAG)
- controlled prompt construction
- multi-provider LLM orchestration
- deterministic validation rules
- structured JSON outputs
- OCR-based ingredient analysis
- execution-oriented outputs
- explainability and demo observability

Built with **Django**, **Python**, **Gemini**, **OpenAI**, **custom RAG**, **OCR**, **validation services**, **PDF generation**, and **Streamlit**.

Its purpose is simple:

> **to demonstrate how AI can evolve from content generation into reliable product workflows.**

![Python](https://img.shields.io/badge/Python-3.13-blue)
![Django](https://img.shields.io/badge/Django-5.x-green)
![OpenAI](https://img.shields.io/badge/OpenAI-API-black)
![Gemini](https://img.shields.io/badge/Gemini-AI-orange)
![OCR](https://img.shields.io/badge/OCR-Vision-purple)
![RAG](https://img.shields.io/badge/RAG-Domain%20Retrieval-red)

---

# 🚀 Live Demo

## Public Technical Demo

👉 **https://nutriprompt-live.streamlit.app**

The public Streamlit demo exposes NutriPrompt's internal AI workflow in a recruiter-friendly and technical format.

It demonstrates:

- structured intake
- profile classification
- RAG retrieval
- prompt construction
- LLM orchestration
- OCR processing
- validation layers
- structured outputs
- AI workflow explainability

The demo is intentionally separated from the Django application so the AI pipeline can be inspected and tested interactively.

---

# 🧠 What This Project Demonstrates

NutriPrompt is an **Applied AI / AI Systems Engineering project**.

It demonstrates how different AI and software-engineering components can be combined into a controlled product workflow:

- Prompt Engineering for controlled generation
- Retrieval-Augmented Generation (RAG)
- Domain-specific knowledge retrieval
- Structured context injection
- OCR ingestion and ingredient parsing
- Deterministic validation after generation
- Multi-provider LLM orchestration
- Provider fallback strategies
- Structured JSON generation
- Explainable workflow outputs
- Human-readable reports
- Machine-readable outputs
- Product-oriented AI UX
- Context-first AI workflows

The project reflects a core design principle:

> **Reliable AI products require more than a prompt and an LLM.**

---

# 🔎 Retrieval-Augmented Generation

NutriPrompt implements a lightweight, domain-specific RAG architecture over a curated nutrition knowledge base.

The current retrieval strategy is intentionally simple, transparent and testable:

```text
User Profile
     ↓
RAG Query Builder
     ↓
Nutrition Knowledge Base
     ↓
Keyword / Rule Scoring
     ↓
Top-K Relevant Rules
     ↓
Retrieved Context
     ↓
Prompt Augmentation
     ↓
LLM Generation

The knowledge base is stored as structured JSON rules.

For every user request, NutriPrompt:

extracts relevant profile information
builds a retrieval query
scores nutrition rules against the query
retrieves the most relevant rules
injects the retrieved context into the final prompt
asks the LLM to generate a structured plan grounded in that context

This is a rule-based / keyword-scored RAG implementation.

It does not currently rely on vector embeddings or a vector database.

That distinction is intentional: the current architecture keeps retrieval transparent, inspectable and easy to validate.

A future evolution can replace the lexical retriever with semantic retrieval using embeddings without changing the rest of the RAG pipeline.

🧩 RAG Architecture
nutrition_rules.json
        ↓
knowledge_base.py
        ↓
retriever.py
        ↓
rag_context_builder.py
        ↓
prompt_builder.py
        ↓
Gemini / OpenAI

The architecture separates:

knowledge storage
retrieval
context construction
prompt generation
LLM inference

This makes the retrieval layer independently testable and replaceable.

💼 Business Value

NutriPrompt demonstrates how AI can support real product workflows by helping to:

reduce planning friction
improve recommendation consistency
personalize outputs using structured context
validate critical restrictions
reduce user decision fatigue
transform recommendations into actionable plans
isolate provider failures
improve output reliability through post-generation validation

This project is not only about nutrition.

It demonstrates a reusable pattern for building AI products around business rules, domain knowledge and controlled generation.

🌍 Why This Architecture Matters Beyond Nutrition

The architecture is transferable to other domains where AI must combine user context, domain knowledge and validation.

The same pattern can be applied to:

healthcare decision-support
legal document analysis
HR screening workflows
customer-support copilots
insurance validation
procurement workflows
industrial compliance
internal knowledge assistants

The reusable pattern is:

Structured Input
      ↓
Context Analysis
      ↓
Knowledge Retrieval
      ↓
Controlled Generation
      ↓
Validation
      ↓
Actionable Output
✨ Product Vision

Nutrition planning is not only a content-generation problem.

A useful planning system must take into account:

personal goals
dietary restrictions
ingredient compatibility
food preferences
lifestyle constraints
budget
time available
cooking access
eating outside the home
execution friction

NutriPrompt treats nutrition planning as an intelligent workflow problem, not as a chatbot interaction.

The system enriches requests before generation and validates outputs afterwards.

This creates:

✅ domain-grounded generation
✅ context-aware personalization
✅ explicit validation layers
✅ explainable decision flows
✅ compatibility-aware planning
✅ provider resilience
✅ structured AI outputs

🎯 Why I Built This

I built NutriPrompt to explore how AI products evolve beyond content generation into decision-support and workflow architectures.

The goal was not simply to generate meal plans.

The goal was to design and implement a system that demonstrates:

structured decision flows
domain grounding
retrieval orchestration
controlled generation
validation
explainability
resilient fallbacks
product-oriented thinking
real-world execution

This project reflects how I approach Applied AI and AI Product design:

connecting business logic, data, software architecture and Generative AI into usable systems.

🏗 System Architecture
User Input
      ↓
Structured Intake
      ↓
Profile Analysis
      ↓
RAG Query Builder
      ↓
Domain Knowledge Retrieval
      ↓
Prompt Builder
      ↓
Gemini API
      ↓
Validation
      ↓
Retry if required
      ↓
OpenAI Fallback
      ↓
Structured JSON Output
      ↓
Nutrition Rules Engine
      ↓
Presentation Layer
      ↓
Shopping Intelligence
      ↓
HTML / PDF Output
      ↓
AI Copilot / Explainability
🛡 Validation-First AI Workflow

NutriPrompt does not rely exclusively on the LLM to respect business rules.

The system combines three complementary layers.

1. Deterministic input interpretation

User restrictions and profile tags are identified explicitly.

Examples:

vegan
vegetarian
pescetarian
lactose-free
gluten-free
low-FODMAP
limited kitchen access
tupper requirements
budget constraints
2. Retrieved domain context

Relevant nutrition rules are retrieved from the knowledge base and injected into the prompt.

3. Post-generation validation

Generated plans are parsed and validated before being accepted.

When validation fails, NutriPrompt can construct a corrective retry prompt containing:

the validation error
the previous invalid output
the original user context
the retrieved RAG context

This creates a controlled regeneration loop rather than accepting the first LLM response blindly.

🤖 Multi-Provider LLM Orchestration

NutriPrompt abstracts generation from a single AI provider.

Gemini
   ↓
Validate output
   ↓
Retry if required
   ↓
Provider failure
   ↓
OpenAI fallback
   ↓
Validate output

Current models:

Gemini 2.5 Flash
GPT-5 mini

Benefits:

reduced provider dependency
graceful fallback
improved demo reliability
provider abstraction
consistent validation across models

This is multi-provider orchestration, not a multi-agent architecture.

📸 Product Walkthrough
1. Smart Nutrition Intake

Transforms structured user input into contextual AI workflows.

The intake captures:

goals
dietary restrictions
digestive context
food preferences
budget
lifestyle context
cooking access
tupper requirements
days outside the home

2. Generated Nutrition Plan

Produces:

seven-day meal plans
compatibility-aware recommendations
context-aware adaptations
structured outputs
explainable profile tags
downloadable reports

3. Shopping Intelligence Layer

Transforms recommendations into execution-oriented outputs.

It supports:

categorized shopping lists
grouped ingredients
reusable ingredients
practical weekly planning

👁 OCR + Ingredient Intelligence

NutriPrompt also explores multimodal AI workflows.

OCR and vision-related services can extract and analyze information from:

food labels
ingredient lists
nutrition information
product images

The extracted information can then be processed by compatibility and nutrition-risk rules.

This demonstrates how unstructured visual information can be transformed into structured product logic.

⚡ Core AI Capabilities
Personalized AI Planning
Domain-Specific RAG
Keyword-Scored Knowledge Retrieval
Controlled Prompt Engineering
OCR + Ingredient Intelligence
Rule-Based Validation
Structured JSON Generation
Multi-Provider LLM Orchestration
Retry / Fallback Logic
Shopping Intelligence
AI Workflow Explainability
Streamlit Technical Demo
⚙ Design Principles

NutriPrompt was intentionally designed around:

Context before generation
Retrieval before inference
Controlled generation over open prompting
Validation over blind trust
Explainability over black-box outputs
Provider abstraction over vendor dependency
Structured outputs over free-form text
Modular services over monolithic AI functions
Product workflows over chatbot interactions
⚙️ Technology Stack
Layer	Technology
Backend	Django 5.x
Language	Python 3.13
Primary LLM	Gemini 2.5 Flash
LLM Fallback	GPT-5 mini
Retrieval	Custom rule-based RAG
Knowledge Base	Structured JSON
Retrieval Strategy	Keyword / relevance scoring
OCR	Tesseract OCR
Output Format	Structured JSON
PDF Rendering	WeasyPrint
Frontend	HTML + CSS
Technical Demo	Streamlit
Testing	Django Test Framework
📁 AI Service Architecture
nutriprompt_app/
└── services/
    ├── ai/
    │   ├── ai_generator.py
    │   ├── gemini_client.py
    │   ├── openai_client.py
    │   ├── prompt_builder.py
    │   ├── json_parser.py
    │   ├── validator.py
    │   └── rules.py
    │
    ├── rag/
    │   ├── knowledge_base.py
    │   ├── retriever.py
    │   ├── rag_context_builder.py
    │   └── embeddings.py
    │
    ├── profiles/
    │   └── profile_classifier.py
    │
    ├── vision/
    │   ├── label_reader.py
    │   ├── compatibility_analyzer.py
    │   ├── nutrition_risk_rules.py
    │   └── vision_analyzer.py
    │
    └── nutrition/
        ├── meal_rules.py
        ├── fallback_plan.py
        └── shopping_list_generator.py

The service-oriented architecture keeps retrieval, generation, validation, vision and presentation concerns separated.

🧪 Test Coverage

Automated tests cover critical parts of the AI workflow, including:

knowledge-base loading
rule serialization
RAG retrieval
low-FODMAP retrieval
gluten-related retrieval
RAG context construction
RAG injection into prompts
prompt generation
AI output validation
OCR processing
compatibility analysis
fallback behaviour
structured outputs
shopping generation

Run the test suite with:

python manage.py test

17 automated tests passing

🔬 Example RAG Flow

Example user context:

Restrictions: gluten-free, low-FODMAP
Preferences: rice, chicken, onion soup
Needs tupper: yes

NutriPrompt builds a retrieval query from the profile.

The retriever may recover domain rules related to:

Gluten
Wheat
Low-FODMAP
Onion

The resulting context is injected into the LLM prompt:

CONTEXTO NUTRICIONAL RECUPERADO MEDIANTE RAG

- Category: low_fodmap
- Rule: ...
- Risk level: high

- Category: sin_gluten
- Rule: ...
- Risk level: ...

The LLM generates the weekly plan using both:

the user profile
the retrieved domain knowledge

The generated output is then validated before being accepted.

🔄 Resilience Strategy

NutriPrompt is designed to fail gracefully.

The generation workflow includes:

Gemini
   ↓
Validation
   ↓
Retry
   ↓
OpenAI Fallback
   ↓
Validation
   ↓
Controlled failure if no provider returns a valid result

This reduces dependency on a single provider and keeps validation logic independent from the selected LLM.

🗺 Technical Roadmap

Potential future improvements include:

semantic retrieval with embeddings
vector similarity search
configurable Top-K retrieval
retrieval evaluation metrics
provenance / source attribution
richer RAG knowledge ingestion
agentic tool orchestration
automated RAG quality evaluation
enhanced observability
CI/CD quality gates

The current modular architecture allows the lexical retriever to be replaced by a semantic retriever without redesigning the complete generation pipeline.

🛠 Installation
git clone https://github.com/beatriangu/NutriPrompt.git
cd NutriPrompt

python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt

Run Django:

python manage.py runserver

Run the Streamlit demo:

streamlit run streamlit_demo/app.py
⚠️ Disclaimer

NutriPrompt provides informational and organizational guidance only.

It does not replace medical, nutritional or healthcare advice.

The system is designed as an Applied AI technical demonstration.

People with medical conditions, persistent symptoms or complex dietary requirements should consult qualified healthcare or nutrition professionals.

👩‍💻 Author

Bea Lamiquiz

🌐 Portfolio: https://bchill.net
💻 GitHub: https://github.com/beatriangu
💼 LinkedIn: https://www.linkedin.com/in/bealamiquiz/

🤝 Let's Connect

I build AI systems at the intersection of:

Product
Data
Business Logic
Software Engineering
Generative AI

Interested in:

AI Product
Applied AI
AI Systems Engineering
Product & Technology
AI architecture
technical collaborations
product strategy

From prompts to products: building AI systems that retrieve, reason within constraints, validate and deliver usable outcomes.

