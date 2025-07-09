import sys
import os
import fitz  # PyMuPDF
import subprocess

def extraer_texto_desde_pdf(ruta_pdf):
    """Extrae el texto de un PDF con PyMuPDF"""
    doc = fitz.open(ruta_pdf)
    texto = ""
    for pagina in doc:
        texto += pagina.get_text()
    return texto.strip()

def generar_prompt(texto_cliente):
    """Genera el prompt completo con instrucciones y datos del cliente"""
    instrucciones = """
<<INSTRUCCIONES>>
Actúa como un nutricionista profesional, cercano y motivador. Vas a generar un plan saludable y personalizado de 7 días para un cliente usando la información que te doy a continuación.

🔹 El plan debe incluir:
- Desayuno, comida, cena, snack
- Ejercicio adaptado a su disponibilidad
- Consejos de descanso
- Coste estimado diario, respetando su presupuesto semanal
- Recetas fáciles (cuando se indique)
- Evita alimentos contraindicados (lactosa, pescado azul excepto atún en conserva)
- Todo en una tabla clara, práctica y fácil de copiar

🔹 Condiciones:
- No sobrepasar el presupuesto de 60 €
- No recomendar ejercicio al aire libre (por alergias estacionales)
- Cocinado en máximo 30 minutos al día

🔹 Tono:
- Cercano, motivador, con frases breves de ánimo como “¡Puedes con esto!” o “¡Buen trabajo, vamos a por el siguiente día!”
<<FIN INSTRUCCIONES>>
"""

    cierre = """
Por favor, genera una tabla con 7 filas (una por día) y las siguientes columnas:
- Día
- Desayuno
- Comida
- Cena
- Snack
- Ejercicio
- Descanso
- Coste (€)
"""

    return f"{instrucciones}\n\n<<DATOS DEL CLIENTE>>\n{texto_cliente}\n<<FIN DATOS>>\n{cierre}"

def lanzar_starlit(prompt_path, salida="output_ejemplo.md"):
    """Lanza Starlit CLI con el prompt generado"""
    try:
        subprocess.run(["starlit", "prompt", "run", "--input", prompt_path, "--output", salida], check=True)
        print(f"✅ Plan generado con Starlit y guardado en {salida}")
    except FileNotFoundError:
        print("❌ No se encuentra el ejecutable 'starlit'. ¿Está instalado con npm?")
    except subprocess.CalledProcessError:
        print("❌ Ocurrió un error al ejecutar Starlit.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python prompt_generator.py ruta_del_pdf")
        sys.exit(1)

    ruta_pdf = sys.argv[1]

    if not os.path.exists(ruta_pdf):
        print(f"⚠️ No se encuentra el archivo: {ruta_pdf}")
        sys.exit(1)

    texto_cliente = extraer_texto_desde_pdf(ruta_pdf)
    prompt = generar_prompt(texto_cliente)

    prompt_path = "prompt_generado.txt"
    with open(prompt_path, "w", encoding="utf-8") as f:
        f.write(prompt)
        print(f"✅ Prompt guardado en {prompt_path}")

    lanzar_starlit(prompt_path)

