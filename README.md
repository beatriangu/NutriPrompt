🥦 NutriPrompt — Plan Semanal Saludable con IA
<img src="https://raw.githubusercontent.com/beatriangu/nutriprompt/main/nutriprompt1.png" width="250" alt="NutriPrompt logo">
NutriPrompt es una herramienta inteligente que genera planes de alimentación y ejercicio personalizados a partir de un formulario rellenado por el cliente, utilizando técnicas de Prompt Engineering.

Este proyecto demuestra cómo, a partir de un simple formulario, se puede construir un prompt estructurado y eficaz que sirve como entrada para herramientas de IA como ChatGPT.

📌 ¿Qué hace?
🔹 Extrae los datos del cliente desde un formulario (texto plano)
🔹 Construye un prompt seguro y bien estructurado
🔹 El prompt puede copiarse y pegarse en ChatGPT para generar un plan personalizado
🔹 Incluye ejemplos reales anonimizados

🧠 Tecnologías utilizadas
Prompt Engineering

Python (para estructurar los datos)

ChatGPT (uso manual del prompt generado)

📄 Ejemplo de formulario
Se incluye un formulario real (anonimizado) con los datos de un cliente y un ejemplo del prompt generado a partir de esos datos.

🚀 Próximos pasos
Integración con una interfaz web interactiva

Automatización de la extracción desde formularios PDF

Generación de un plan final en PDF para entregar al cliente

✳️ Proyecto creado como parte de la formación en IA aplicada a servicios personalizados.

⚙️ ¿Cómo ejecutar este proyecto?
Clona este repositorio:

bash
Copiar código
git clone https://github.com/beatriangu/nutriprompt.git
cd nutriprompt
Crea y activa un entorno virtual:

bash
Copiar código
python3 -m venv venv
source venv/bin/activate
Instala los requisitos:

bash
Copiar código
pip install -r requirements.txt
Genera el prompt:

bash
Copiar código
python prompt_generator.py
Esto creará un archivo prompt_generado.txt que podrás copiar directamente y pegar en ChatGPT (o cualquier herramienta de IA compatible) para obtener el plan semanal personalizado.

