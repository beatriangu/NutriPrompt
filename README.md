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

**Beatriz Angulo**
- Portfolio: [bchill.es](https://bchill.es)
- GitHub: [@beatriangu](https://github.com/beatriangu)
- LinkedIn: [beatriz-angulo](https://linkedin.com/in/beatriz-angulo)

---

## 🙏 Agradecimientos

- Ejemplos de formularios proporcionados por clientes reales (anonimizados)
- Inspirado en mejores prácticas de prompt engineering de OpenAI
- Proyecto creado como parte de formación en IA aplicada a servicios personalizados

---

## 📊 Stats

⭐ Si este proyecto te resultó útil, ¡dale una estrella!

🐛 ¿Encontraste un bug? [Abre un issue](https://github.com/beatriangu/NutriPrompt/issues)

