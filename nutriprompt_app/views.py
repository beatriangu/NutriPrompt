import datetime
import os
from html import escape

from django.conf import settings
from django.shortcuts import render
from weasyprint import HTML

from nutriprompt_app.services.ai_generator import generate_meal_plan, get_mock_meal_plan


def home(request):
    return render(request, "nutriprompt_app/home.html")


def build_plan_html_table(
    plan_data,
    nombre="",
    objetivo="",
    restricciones="",
    preferencias="",
    presupuesto="",
):
    rows = []

    for day_data in plan_data:
        day = escape(str(day_data.get("day", "")))
        breakfast = escape(str(day_data.get("breakfast", "")))
        lunch = escape(str(day_data.get("lunch", "")))
        dinner = escape(str(day_data.get("dinner", "")))

        rows.append(f"""
            <tr>
                <td>{day}</td>
                <td>{breakfast}</td>
                <td>{lunch}</td>
                <td>{dinner}</td>
            </tr>
        """)

    info_cliente = f"""
        <div style="margin-bottom: 24px;">
            <h2 style="margin-bottom: 12px;">Plan semanal personalizado</h2>
            <p><strong>Cliente:</strong> {escape(nombre)}</p>
            <p><strong>Objetivo:</strong> {escape(objetivo)}</p>
            <p><strong>Restricciones:</strong> {escape(restricciones or "No especificadas")}</p>
            <p><strong>Preferencias:</strong> {escape(preferencias or "No especificadas")}</p>
            <p><strong>Presupuesto semanal:</strong> {escape(presupuesto or "No especificado")}</p>
            <p style="margin-top: 14px; font-size: 13px; color: #666;">
                Este plan es orientativo y no sustituye el asesoramiento de un profesional sanitario.
            </p>
        </div>
    """

    table_html = f"""
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 30px;
                color: #222;
            }}
            h2 {{
                color: #2c3e50;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 20px;
                font-size: 14px;
            }}
            th, td {{
                border: 1px solid #ddd;
                padding: 12px;
                vertical-align: top;
                text-align: left;
            }}
            th {{
                background-color: #f5f5f5;
            }}
            tr:nth-child(even) {{
                background-color: #fafafa;
            }}
        </style>
    </head>
    <body>
        {info_cliente}
        <table>
            <thead>
                <tr>
                    <th>Día</th>
                    <th>Desayuno</th>
                    <th>Comida</th>
                    <th>Cena</th>
                </tr>
            </thead>
            <tbody>
                {''.join(rows)}
            </tbody>
        </table>
    </body>
    </html>
    """

    return table_html


def procesar_plan_directo(request):
    if request.method != "POST":
        return render(request, "nutriprompt_app/home.html")

    nombre = request.POST.get("nombre", "").strip()
    objetivo = request.POST.get("objetivo", "").strip()
    restricciones = request.POST.get("restricciones", "").strip()
    preferencias = request.POST.get("preferencias", "").strip()
    presupuesto = request.POST.get("presupuesto", "").strip()

    if not nombre or not objetivo:
        return render(
            request,
            "nutriprompt_app/home.html",
            {
                "error": "Por favor, completa al menos el nombre y el objetivo."
            },
        )

    texto_cliente = f"""
Nombre: {nombre}
Objetivo: {objetivo}
Restricciones: {restricciones}
Preferencias: {preferencias}
Presupuesto semanal: {presupuesto}
""".strip()

    # 🔥 AQUÍ ESTÁ LA MAGIA (fallback incluido)
    try:
        plan_data = generate_meal_plan(texto_cliente)
    except Exception as e:
        print("⚠️ Usando datos mock por error en Gemini:", e)
        plan_data = get_mock_meal_plan()

    tabla_html = build_plan_html_table(
        plan_data=plan_data,
        nombre=nombre,
        objetivo=objetivo,
        restricciones=restricciones,
        preferencias=preferencias,
        presupuesto=presupuesto,
    )

    output_dir = os.path.join(settings.MEDIA_ROOT, "resultados")
    os.makedirs(output_dir, exist_ok=True)

    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    safe_name = nombre.replace(" ", "_")
    html_filename = f"plan_{safe_name}_{timestamp}.html"
    html_path = os.path.join(output_dir, html_filename)

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(tabla_html)

    pdf_filename = html_filename.replace(".html", ".pdf")
    pdf_path = os.path.join(output_dir, pdf_filename)
    HTML(string=tabla_html).write_pdf(pdf_path)

    pdf_url = f"{settings.MEDIA_URL}resultados/{pdf_filename}"

    return render(
        request,
        "nutriprompt_app/resultado.html",
        {
            "tabla_html": tabla_html,
            "pdf_url": pdf_url,
        },
    )
