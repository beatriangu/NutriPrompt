import sys
import os
import fitz  # PyMuPDF
from transformers import pipeline
from restricciones_detector import detectar_restricciones

# Modelos ligeros y rápidos
clasificador_comentarios = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
generador = pipeline("text-generation", model="gpt2", max_length=1024, do_sample=True)

def interpretar_comentarios_transformers(texto):
    etiquetas = [
        "viaje", "comida fuera", "día con poco tiempo", "dolor menstrual",
        "fatiga", "comida rápida", "cocinar lo justo", "recetas para llevar",
        "no usar horno", "preferencia por frío", "actividad suave", "comer en casa de familiares"
    ]
    resultado = clasificador_comentarios(sequences=texto, candidate_labels=etiquetas, multi_label=True)
    return [
        f"- {et} (confianza: {round(score, 2)})"
        for et, score in zip(resultado["labels"], resultado["scores"]) if score > 0.45
    ]

def extraer_texto_desde_pdf(ruta_pdf):
    doc = fitz.open(ruta_pdf)
    return "".join(pagina.get_text() for pagina in doc).strip()

def generar_prompt(texto_cliente):
    restricciones = detectar_restricciones(texto_cliente)
    comentarios = interpretar_comentarios_transformers(texto_cliente)

    bloque_restricciones = "\n🔍 Restricciones detectadas:\n" + \
        "\n".join([f"- {r[0]} (confianza: {r[1]})" for r in restricciones]) \
        if restricciones else "\n🔍 Sin restricciones específicas detectadas."

    bloque_comentarios = "\n🗣️ Comentarios interpretados:\n" + "\n".join(comentarios) if comentarios else ""

    instrucciones = """<<INSTRUCCIONES>>
Actúa como un nutricionista profesional, cercano y motivador. Vas a generar un plan saludable y personalizado de 7 días para un cliente usando la información que te doy a continuación.

🔹 El plan debe incluir:
- Desayuno, comida, cena, snack
- Ejercicio adaptado a su disponibilidad
- Consejos de descanso
- Coste estimado diario, respetando su presupuesto semanal
- Recetas fáciles (cuando se indique)
- Evita alimentos contraindicados (lactosa, pescado azul excepto atún en conserva)
- Todo en una tabla clara, práctica y fácil de copiar (en formato markdown con emojis si es posible)

🔹 Condiciones:
- No sobrepasar el presupuesto indicado
- No recomendar ejercicio al aire libre
- Cocinado en máximo el tiempo disponible

🔹 Tono:
- Cercano y motivador con frases como “¡Puedes con esto!” o “¡Vamos a por el siguiente día!”
<<FIN INSTRUCCIONES>>"""

    cierre = """
Por favor, genera una tabla markdown con estas columnas:
Día | Desayuno | Comida | Cena | Snack | Ejercicio | Descanso | Coste (€)
"""

    return f"{instrucciones}\n{bloque_restricciones}\n{bloque_comentarios}\n\n<<DATOS DEL CLIENTE>>\n{texto_cliente}\n<<FIN DATOS>>\n{cierre}"

def generar_plan_desde_pdf(ruta_pdf, salida="output_ejemplo.md"):
    if not os.path.exists(ruta_pdf):
        print(f"⚠️ No se encuentra el archivo: {ruta_pdf}")
        return None

    texto_cliente = extraer_texto_desde_pdf(ruta_pdf)
    prompt = generar_prompt(texto_cliente)

    resultado = generador(prompt, max_new_tokens=1024)[0]["generated_text"]

    with open(salida, "w", encoding="utf-8") as f:
        f.write(resultado)
        print(f"✅ Plan generado y guardado en {salida}")
    return salida

def generar_respuesta_personalizada(texto_cliente):
    """
    Genera el texto del plan semanal en base al contenido extraído del formulario PDF.
    Esta versión es ideal para usar dentro de una vista Django.
    """
    prompt = generar_prompt(texto_cliente)
    resultado = generador(prompt, max_new_tokens=512)[0]["generated_text"]
    return resultado

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python prompt_generator_optimo.py ruta_del_pdf")
        sys.exit(1)
    generar_plan_desde_pdf(sys.argv[1])
