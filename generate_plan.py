from dotenv import load_dotenv
import os
import openai

# Cargar variables del archivo .env
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Leer el prompt desde el archivo generado
with open("prompt_generado.txt", "r", encoding="utf-8") as f:
    prompt = f.read()

# Llamar al modelo GPT-4o
response = openai.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "user", "content": prompt}
    ]
)

# Extraer la respuesta del modelo
contenido = response.choices[0].message.content

# Guardar la salida en Markdown
with open("output_ejemplo.md", "w", encoding="utf-8") as f:
    f.write(contenido)

print("✅ Plan generado y guardado en output_ejemplo.md")
