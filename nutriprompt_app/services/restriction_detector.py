from transformers import pipeline

# Usamos un modelo más eficiente y compatible para clasificación zero-shot
classifier = pipeline(
    "zero-shot-classification",
    model="MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli",
    device=-1  # CPU explícito (cambia a 0 si tienes GPU disponible)
)

# Lista de etiquetas que queremos identificar automáticamente
ETIQUETAS_RESTRICCIONES = [
    "sin gluten",
    "sin lactosa",
    "digestiones pesadas",
    "vegetariano",
    "no pescado azul",
    "prefiere cenas ligeras",
    "evitar impacto en rodillas",
    "comidas rápidas de preparar",
    "prefiere snacks saludables"
]

def detectar_restricciones(texto):
    """
    Aplica zero-shot classification al texto del formulario
    y devuelve etiquetas detectadas con una confianza ≥ 0.5
    """
    resultado = classifier(texto, ETIQUETAS_RESTRICCIONES)

    restricciones_detectadas = [
        (etiqueta, round(score, 2))
        for etiqueta, score in zip(resultado["labels"], resultado["scores"])
        if score >= 0.5
    ]
    return restricciones_detectadas


# Test de consola (para desarrollo)
if __name__ == "__main__":
    ejemplo = "Me cuesta digerir por la noche, prefiero cenas suaves y suelo tener molestias con la lactosa"
    resultado = detectar_restricciones(ejemplo)
    print("Restricciones detectadas:")
    for etiqueta, score in resultado:
        print(f"- {etiqueta} ({score})")

