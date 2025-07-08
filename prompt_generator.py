# prompt_generator.py

def generar_prompt(datos_cliente_path="datos_cliente_ejemplo.txt", salida="prompt_generado.txt"):
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

    # Leer datos del cliente
    try:
        with open(datos_cliente_path, "r", encoding="utf-8") as f:
            datos_cliente = f.read().strip()
    except FileNotFoundError:
        print(f"⚠️ Archivo no encontrado: {datos_cliente_path}")
        return

    prompt_completo = f"{instrucciones}\n\n<<DATOS DEL CLIENTE>>\n{datos_cliente}\n<<FIN DATOS>>\n{cierre}"

    # Guardar prompt generado
    with open(salida, "w", encoding="utf-8") as f:
        f.write(prompt_completo)
        print(f"✅ Prompt generado con éxito en: {salida}")


if __name__ == "__main__":
    generar_prompt()
