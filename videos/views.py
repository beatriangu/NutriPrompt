import os
from datetime import datetime
import subprocess

from django.shortcuts import render, redirect
from django.conf import settings

from .models import DemoVideo
from fpdf import FPDF


def ver_video(request):
    """Muestra el último vídeo subido como demo"""
    video = DemoVideo.objects.last()
    return render(request, 'videos/ver_video.html', {'video': video})


def formulario_demo(request):
    """Vista para mostrar y procesar el formulario de usuario"""
    if request.method == 'POST':
        # Recoger datos del formulario
        datos = {
            'nombre': request.POST.get('nombre'),
            'edad': request.POST.get('edad'),
            'peso': request.POST.get('peso'),
            'altura': request.POST.get('altura'),
            'presupuesto': request.POST.get('presupuesto'),
            'ejercicio': request.POST.get('ejercicio'),
            'cocina': request.POST.get('cocina'),
            'restricciones': request.POST.get('restricciones'),
            'objetivo': request.POST.get('objetivo'),
            'comentarios': request.POST.get('comentarios'),
        }

        # Crear PDF con los datos
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        texto = "\n".join([f"{k.capitalize()}: {v}" for k, v in datos.items()])
        pdf.multi_cell(0, 10, txt="Formulario NutriPrompt\n\n" + texto)

        # Guardar el PDF
        carpeta = os.path.join(settings.MEDIA_ROOT, 'formularios')
        os.makedirs(carpeta, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        archivo_nombre = f"{datos['nombre']}_{timestamp}.pdf"
        ruta_pdf = os.path.join(carpeta, archivo_nombre)
        pdf.output(ruta_pdf)

        # Guardar el nombre del PDF para la siguiente vista
        request.session['archivo_pdf'] = archivo_nombre

        return redirect('generar_plan')

    return render(request, 'videos/formulario_demo.html')


def generar_plan(request):
    """Vista intermedia tras subir PDF, con botón para ejecutar la IA"""
    archivo_pdf = request.session.get('archivo_pdf')
    if not archivo_pdf:
        return redirect('formulario')

    return render(request, 'videos/generar_plan.html', {'archivo_pdf': archivo_pdf})


def procesar_plan(request):
    """Ejecuta el script con Starlit y muestra el resultado"""
    if request.method == 'POST':
        archivo_pdf = request.POST.get('archivo_pdf')
        ruta_pdf = os.path.join(settings.MEDIA_ROOT, 'formularios', archivo_pdf)

        try:
            # Ejecutar el script de generación con Starlit
            subprocess.run(['python', 'prompt_generator.py', ruta_pdf], check=True)
        except subprocess.CalledProcessError:
            return render(request, 'videos/error.html', {'mensaje': '❌ Error al generar el plan con IA'})

        output_path = os.path.join(os.getcwd(), 'output_ejemplo.md')
        if os.path.exists(output_path):
            with open(output_path, 'r', encoding='utf-8') as f:
                contenido = f.read()
            return render(request, 'videos/plan_resultado.html', {'plan': contenido})
        else:
            return render(request, 'videos/error.html', {'mensaje': '⚠️ No se generó el archivo de salida'})

    return redirect('formulario')


def cargando(request):
    archivo_pdf = request.session.get('archivo_pdf', None)
    return render(request, 'videos/cargando.html', {'archivo_pdf': archivo_pdf})

