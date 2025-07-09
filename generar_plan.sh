#!/bin/bash

# 📄 Ruta al archivo PDF (primer argumento)
PDF="$1"

if [ -z "$PDF" ]; then
  echo "❌ Debes pasar la ruta al archivo PDF como argumento."
  echo "Ejemplo: ./generar_plan.sh media/formularios/Ba_20250709_161701.pdf"
  exit 1
fi

# ✅ Generar prompt desde el PDF
echo "📄 Generando prompt desde: $PDF"
python3 prompt_generator.py "$PDF"

# ✅ Ejecutar Starlit (requiere tener starlit CLI instalada)
echo "🚀 Ejecutando Starlit..."
starlit prompt run --input prompt_generado.txt --output output_ejemplo.md

# ✅ Mostrar resultado
echo "✅ Plan generado en output_ejemplo.md"
echo "-------------------------------------"
cat output_ejemplo.md
echo "-------------------------------------"
