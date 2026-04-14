# 🥦 NutriPrompt — Generador Inteligente de Planes Nutricionales

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-MVP-orange.svg)]()

Sistema de **Prompt Engineering** que transforma formularios de clientes en prompts estructurados y optimizados para IA generativa (ChatGPT). Diseñado como MVP para demostrar cómo aplicar técnicas de IA a servicios personalizados de nutrición.

---

## 🎯 Problema que Resuelve

Crear planes nutricionales personalizados requiere:
- ✅ Recopilar datos del cliente (objetivos, restricciones, preferencias)
- ✅ Estructurar la información de forma coherente
- ✅ Generar un plan balanceado y seguro
- ❌ **Pero escribir prompts efectivos es difícil y consume tiempo**

**NutriPrompt automatiza la construcción del prompt perfecto.**

---

## 🚀 ¿Qué Hace?
```
Formulario del cliente → Parser Python → Prompt optimizado → ChatGPT → Plan de 7 días
```

1. **Extrae** datos estructurados desde formularios (PDF o texto plano)
2. **Construye** un prompt siguiendo mejores prácticas de prompt engineering
3. **Genera** un archivo `.txt` listo para copiar a ChatGPT
4. El usuario obtiene un **plan nutricional de calidad profesional** en segundos

---

## 🧠 Stack Técnico

- **Lenguaje:** Python 3.8+
- **Prompt Engineering:** Diseño modular con contexto + instrucciones + formato
- **Parser:** Extracción de datos con expresiones regulares
- **Automatización:** Scripts bash para flujo completo
- **Output:** Texto plano optimizado para IA generativa

---

## 📦 Instalación

### Prerrequisitos
```bash
python >= 3.8
pip
```

### Setup
```bash
# 1. Clona el repositorio
git clone https://github.com/beatriangu/NutriPrompt.git
cd NutriPrompt

# 2. Crea entorno virtual
python3 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# 3. Instala dependencias
pip install -r requirements.txt
```

---

## 🎮 Uso Rápido

### Generar un prompt desde formulario de ejemplo:
```bash
python prompt_generator_optimo.py
```

Esto creará `prompt_generado.txt` que puedes copiar directamente a ChatGPT.

### Usando el script automatizado:
```bash
bash generar_plan.sh
```

### Limpiar archivos generados:
```bash
bash limpiar.sh
```

---

## 🏗️ Arquitectura
```
┌─────────────────────┐
│  Formulario PDF     │
│  (cliente real)     │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Parser Python      │
│  • restricciones    │
│  • objetivos        │
│  • preferencias     │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Prompt Generator   │
│  • System context   │
│  • User data        │
│  • Output format    │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  prompt.txt         │
│  (optimizado)       │
└──────────┬──────────┘
           │
           ▼
    [ ChatGPT-4 ]
           │
           ▼
┌─────────────────────┐
│  Plan de 7 días     │
│  • Desayunos        │
│  • Comidas          │
│  • Cenas            │
│  • Snacks           │
└─────────────────────┘
```

---

## 🧪 Ejemplo Real

### Input: `Formulario_nutricionista_ejemplo.pdf`
```
Nombre: Carla R. (anonimizado)
Edad: 32 años
Objetivo: Pérdida de peso saludable
Restricciones: Intolerancia a lactosa
Presupuesto: Medio-bajo
Preferencias: Cocina mediterránea, < 30 min
```

### Output: `prompt_generado.txt` (fragmento)
```
Actúa como un nutricionista certificado especializado en planes personalizados...

Cliente:
- Edad: 32 años, peso: 68kg, altura: 165cm
- Objetivo: Pérdida de peso gradual (-0.5kg/semana)
- Restricciones: Sin lactosa
- Presupuesto: €40-60/semana
- Cocina mediterránea, preparación rápida

Genera un plan de 7 días con:
1. 1,600 kcal/día (40% carbs, 30% proteína, 30% grasas)
2. 3 comidas + 2 snacks
3. Lista de compras organizada por categorías
4. Tiempo de preparación < 30 min por comida
...
```

### Resultado ChatGPT:
Plan completo de 7 días con recetas, macros, lista de compras y consejos.

---

## 🎯 Decisiones de Producto (Product Owner)

### ¿Por qué empezar con un MVP simple?

1. **Validación rápida:** Probar si el prompt engineering funciona antes de construir infraestructura compleja
2. **Control total:** El usuario puede revisar y ajustar el prompt antes de ejecutarlo
3. **Transparencia:** Se ve exactamente qué se le está pidiendo a la IA
4. **Iteración rápida:** Mejorar los prompts es más fácil que refactorizar código

### ¿Por qué no integrar la API de OpenAI directamente?

- **Costos:** Cada llamada a GPT-4 cuesta $0.03-0.06. Con copy-paste manual, el usuario controla el gasto
- **Flexibilidad:** Permite usar ChatGPT gratuito, Claude, o cualquier LLM
- **Debugging:** Más fácil identificar por qué un prompt falla si lo ves completo

---

## 🗺️ Roadmap

### ✅ Fase 1: MVP (Completado)
- [x] Parser de formularios
- [x] Generador de prompts optimizado
- [x] Scripts de automatización
- [x] Ejemplos reales anonimizados

### 🚧 Fase 2: Web App (En desarrollo)
- [ ] Interfaz Django para subir formularios
- [ ] Visualización del prompt generado
- [ ] Descarga de .txt o copiar al portapapeles

### 🔮 Fase 3: Automatización Completa
- [ ] Integración con API de OpenAI
- [ ] Generación automática de PDFs con el plan
- [ ] Sistema de versiones de prompts (A/B testing)
- [ ] Dashboard para nutricionistas (historial de clientes)

### 💡 Fase 4: Inteligencia Avanzada
- [ ] Fine-tuning de modelo propio
- [ ] Recomendaciones basadas en feedback del cliente
- [ ] Integración con apps de tracking nutricional

---

## 🧪 Testing
```bash
# Ejecutar tests de prompt engineering
python -m pytest tests/

# Validar estructura de prompt generado
python tests/validate_prompt.py
```

---

## 📚 Prompt Engineering: Técnicas Aplicadas

Este proyecto implementa varias técnicas avanzadas:

1. **Few-shot prompting:** Incluye ejemplos de salida esperada
2. **Chain-of-thought:** Descompone la tarea en pasos lógicos
3. **Constraints explícitos:** Define claramente qué NO debe hacer
4. **Output structuring:** Especifica formato JSON/tabla según necesidad
5. **Context injection:** Inserta datos del cliente de forma estructurada

### Ejemplo de técnica aplicada:
```python
# ❌ Prompt débil
"Dame un plan de dieta para una persona de 32 años"

# ✅ Prompt optimizado (NutriPrompt)
"""
Actúa como nutricionista certificado...

Contexto del cliente:
- [datos estructurados]

Restricciones:
- Sin lactosa
- Presupuesto: €50/semana

Output esperado:
1. Plan de 7 días en formato tabla
2. Cada día: desayuno, comida, cena, 2 snacks
3. Macros por comida
4. Lista de compras agrupada

Ejemplo de formato:
[ejemplo concreto]
"""
```

---

## 📄 Estructura del Proyecto
```
NutriPrompt/
├── prompt_generator_optimo.py    # Generador principal
├── restricciones_detector.py     # Parser de restricciones alimentarias
├── nutriprompt_demo.py           # Demo interactivo
├── generar_plan.sh               # Automatización completa
├── limpiar.sh                    # Limpieza de archivos generados
├── Formulario_nutricionista_ejemplo.pdf
├── ejemplo_prompt.txt            # Ejemplo de output
├── requirements.txt
└── README.md
```

---

## 🤝 Contribuir

¿Ideas para mejorar el prompt? ¡PRs bienvenidos!

1. Fork el proyecto
2. Crea tu rama (`git checkout -b feature/MejorPrompt`)
3. Commit tus cambios (`git commit -m 'Añade técnica X de prompt engineering'`)
4. Push a la rama (`git push origin feature/MejorPrompt`)
5. Abre un Pull Request

---

## 📜 Licencia

MIT License - ver [LICENSE](LICENSE) para detalles

---

## 👤 Autor

**Bea Lamiquiz**
- Portfolio: [bchill.net](https://bchill.net)
- GitHub: [@beatriangu](https://github.com/beatriangu)
- LinkedIn: [bealamiquiz](https://www.linkedin.com/in/bealamiquiz/)

---

## 🙏 Agradecimientos

- Ejemplos de formularios proporcionados por clientes reales (anonimizados)
- Inspirado en mejores prácticas de prompt engineering de OpenAI
- Proyecto creado como parte de formación en IA aplicada a servicios personalizados

---

## 📊 Stats

⭐ Si este proyecto te resultó útil, ¡dale una estrella!

🐛 ¿Encontraste un bug? [Abre un issue](https://github.com/beatriangu/NutriPrompt/issues)
=======
🥦 NutriPrompt — Generador Inteligente de Planes Nutricionales con IA
<img src="https://raw.githubusercontent.com/beatriangu/nutriprompt/main/nutriprompt1.png" width="260" alt="NutriPrompt logo">




🧠 Qué es NutriPrompt
NutriPrompt es una aplicación que transforma datos de un usuario en un plan semanal personalizado de alimentación, utilizando IA generativa + Prompt Engineering + Django.
👉 Pasa de ser un generador de prompts a un producto completo funcional.

🎯 Problema que resuelve
Crear planes personalizados implica:


Recoger datos del cliente


Estructurarlos correctamente


Diseñar prompts eficaces


Generar contenido útil con IA


❌ Todo esto consume tiempo
❌ Y depende mucho de la calidad del prompt
👉 NutriPrompt automatiza todo el proceso end-to-end

🚀 Qué hace ahora (versión actual)
Formulario web → Backend Django → Prompt estructurado → Gemini API → JSON → HTML → PDF
🔹 Flujo completo


Usuario completa un formulario web


El sistema construye un prompt estructurado automáticamente


Se envía a IA (Google Gemini)


Se genera un plan semanal en JSON


Se renderiza en HTML


Se exporta como PDF descargable



💥 Funcionalidades principales


🧾 Formulario dinámico (Django)


🧠 Generación automática de prompts


🤖 Integración con Gemini API


📊 Salida estructurada (JSON → HTML)


📄 Generación automática de PDF


⚠️ Sistema de fallback si la IA falla


🎨 Interfaz cuidada y orientada a producto



🧪 Ejemplo de uso
Input:
Nombre: Bea  Objetivo: Organización semanal  Restricciones: Sin lactosa, bajo FODMAPs  Preferencias: Pollo y pescado  
Output:
✔ Plan semanal completo
✔ Adaptado a restricciones
✔ Estructurado por días
✔ Descargable en PDF

🧠 Stack técnico


Backend: Django


Lenguaje: Python 3


IA: Google Gemini API


Frontend: HTML + CSS


PDF: WeasyPrint


Data handling: JSON + Pandas


Prompt Engineering: Diseño estructurado



🏗️ Arquitectura
Usuario  ↓Formulario Django  ↓Generador de prompt  ↓Gemini API  ↓JSON estructurado  ↓HTML renderizado  ↓PDF descargable

📁 Estructura del proyecto
nutriprompt/├── nutriprompt_app/│   ├── services/        # Lógica IA (Gemini)│   ├── templates/       # UI (home + resultado)│   ├── views.py         # Flujo principal│   └── ...├── nutriprompt_web/     # Configuración Django├── media/│   ├── formularios/     # Imágenes / assets│   └── resultados/      # PDFs generados (ignored)├── colab/               # Experimentos iniciales├── prototypes/          # Versiones experimentales├── examples/            # Datos reales anonimizados└── README.md

🧠 Evolución del proyecto
Este proyecto refleja un proceso real de desarrollo:
✅ Fase 1 — Prompt manual


Generación en ChatGPT


✅ Fase 2 — Automatización en Python


Generador de prompts


✅ Fase 3 — Prototipo en Colab


Validación de IA


✅ Fase 4 — Integración IA real


Gemini API


🚀 Fase 5 — Aplicación web (actual)


Django + UX + PDF + fallback



⚠️ Nota importante

Este sistema genera recomendaciones orientativas.
No sustituye el asesoramiento de un profesional sanitario.


🧠 Decisiones de producto
🔹 ¿Por qué usar Prompt Engineering?


Control total sobre la salida


Mejora de calidad sin necesidad de fine-tuning


Iteración rápida


🔹 ¿Por qué Django?


Control backend completo


Escalabilidad


Integración sencilla con IA


🔹 ¿Por qué fallback?


La IA puede fallar (cuotas / saturación)


El sistema sigue funcionando → mejor UX



⚙️ Instalación
git clone https://github.com/beatriangu/nutriprompt.gitcd nutriprompt
1. Entorno virtual
python3 -m venv venvsource venv/bin/activate
2. Dependencias
pip install -r requirements.txt
3. Variables de entorno
Crea .env:
GOOGLE_API_KEY=tu_api_keyDJANGO_SECRET_KEY=tu_secret_keyDEBUG=True

4. Ejecutar
python manage.py runserver
👉 http://127.0.0.1:8000/

🧪 Prototipos incluidos


📓 /colab → experimentos con IA


🧪 /prototypes → versiones alternativas (Streamlit)


📄 /examples → datos reales anonimizados



🎯 Enfoque profesional
Este proyecto demuestra:
✔ Integración real con IA
✔ Diseño de prompts robustos
✔ Arquitectura backend clara
✔ Pensamiento de producto
✔ UX resiliente

👩‍💻 Autora
Beatriz Lamiquiz


GitHub: https://github.com/beatriangu


LinkedIn: https://www.linkedin.com/in/bealamiquiz/



⭐ Si te interesa
Si te gusta el proyecto:
👉 dale una estrella
👉 o conecta conmigo para compartir ideas


