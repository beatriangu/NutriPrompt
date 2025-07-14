import os
from datetime import datetime
from django.conf import settings
from django.shortcuts import render, redirect
from fpdf import FPDF
from .forms import FormularioClienteForm
from .models import DemoVideo
from prompt_generator_optimo import generar_plan_desde_pdf  # ✅ Uso correcto

def bienvenida(request):
    return render(request, 'videos/bienvenida.html')

def ver_video(request):
    video = DemoVideo.objects.last()
    return render(request, 'videos/ver_video.html', {'video': video})

def formulario_demo(request):
    if request.method == 'POST':
        form = FormularioClienteForm(request.POST)
        if form.is_valid():
            datos = form.cleaned_data

            with open("datos_cliente_ejemplo.txt", "w", encoding="utf-8") as f:
                for k, v in datos.items():
                    f.write(f"{k}: {', '.join(v) if isinstance(v, list) else v}\n")

            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            texto = "\n".join([f"{k.capitalize()}: {', '.join(v) if isinstance(v, list) else v}" for k, v in datos.items()])
            pdf.multi_cell(0, 10, txt="Formulario NutriPrompt\n\n" + texto)

            carpeta = os.path.join(settings.MEDIA_ROOT, 'formularios')
            os.makedirs(carpeta, exist_ok=True)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            archivo_nombre = f"{datos['nombre'].replace(' ', '_')}_{timestamp}.pdf"
            ruta_pdf = os.path.join(carpeta, archivo_nombre)
            pdf.output(ruta_pdf)

            request.session['archivo_pdf'] = archivo_nombre
            return redirect('procesar_plan_directo')
    else:
        form = FormularioClienteForm()

    return render(request, 'videos/formulario_demo.html', {'form': form})

def procesar_plan_directo(request):
    archivo_pdf = request.session.get('archivo_pdf')
    if not archivo_pdf:
        return redirect('formulario')

    ruta_pdf = os.path.join(settings.MEDIA_ROOT, 'formularios', archivo_pdf)

    salida = generar_plan_desde_pdf(ruta_pdf)
    if not salida:
        return render(request, 'videos/error.html', {'mensaje': '❌ Error al generar el plan con IA'})

    with open(salida, 'r', encoding='utf-8') as f:
        contenido = f.read()

    nombre = "-"
    coste = "-"
    fecha = datetime.today().strftime("%d/%m/%Y")

    if "–" in contenido:
        nombre = contenido.split("–")[1].split("\n")[0].strip()

    for linea in contenido.splitlines():
        if "💰 Total semanal estimado:" in linea:
            coste = linea.split("**")[-2].replace("€", "").strip()
        if "📅 Generado el:" in linea:
            fecha = linea.split("**")[-2].strip()

    return render(request, 'videos/plan_resultado.html', {
        'plan': contenido,
        'plan_nombre': nombre,
        'plan_fecha': fecha,
        'plan_coste': coste,
    })
