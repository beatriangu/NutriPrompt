#!/bin/bash

echo "🧹 Limpiando archivos generados..."

# Archivos de salida
rm -f output_ejemplo.md datos_cliente_ejemplo.txt prompt_generado.txt

# PDFs
rm -f media/formularios/*.pdf

# Caché de HuggingFace
echo "🧠 Borrando caché de HuggingFace..."
rm -rf ~/.cache/huggingface

# Memoria MPS (solo Mac con Apple Silicon)
if python3 -c "import torch; print(hasattr(torch, 'mps'))" | grep -q "True"; then
    echo "💾 Liberando memoria MPS..."
    python3 -c "import torch; torch.mps.empty_cache()"
fi

echo "✅ Limpieza completada."
