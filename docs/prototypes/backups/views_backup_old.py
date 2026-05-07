from pathlib import Path
import json
import logging
from typing import Any

from django.conf import settings
from django.shortcuts import render
from django.utils import timezone
from django.utils.html import escape
from django.utils.text import slugify

from weasyprint import HTML

from nutriprompt_app.models import IAGeneratedResponse
from nutriprompt_app.services.ai_generator import (
    generate_meal_plan,
    get_mock_meal_plan,
)
from nutriprompt_app.services.profile_classifier import classify_user_profile
from nutriprompt_app.services.shopping_list_generator import generate_shopping_list

logger = logging.getLogger(__name__)

DEMO_MODE_FALLBACK = True
RESULTS_SUBDIR = "resultados"
DEFAULT_USER_LABEL = "Bea"


def home(request):
    return render(request, "nutriprompt_app/home.html")


def _safe_value(value: Any, default: str = "No especificado") -> str:
    text = str(value or "").strip()
    return text if text else default


def _clean_numeric_string(value: Any, default: str = "No especificado") -> str:
    text = str(value or "").strip()
    return text if text else default


def _format_yes_no_value(value: str) -> str:
    mapping = {
        "yes": "Sí",
        "no": "No",
        "sí": "Sí",
        "si": "Sí",
    }
    normalized = str(value or "").strip().lower()
    return mapping.get(normalized, _safe_value(value))


def _format_context_value(value: str) -> str:
    mapping = {
        "home": "Casa",
        "restaurant": "Restaurante / comer fuera",
        "travel": "Viaje",
        "work": "Trabajo",
        "normal": "Rutina normal",
        "weekend": "Fin de semana",
        "event": "Evento / celebración",
        "limited": "Acceso limitado",
        "yes": "Sí",
        "no": "No",
    }
    normalized = str(value or "").strip().lower()
    return mapping.get(normalized, _safe_value(value))


def _extract_form_data(request) -> dict[str, str]:
    fields = (
        "nombre",
        "objetivo",
        "restricciones",
        "preferencias",
        "presupuesto",
        "meal_context",
        "special_situation",
        "needs_tupper",
        "has_kitchen",
        "days_away",
        "accept_privacy",
    )
    return {field: request.POST.get(field, "").strip() for field in fields}


def _format_profile_tags(profile_tags: list[str]) -> str:
    if not profile_tags:
        return "No detectadas"
    return ", ".join(profile_tags)


def _build_user_input_text(
    nombre: str,
    objetivo: str,
    restricciones: str,
    preferencias: str,
    presupuesto: str,
    meal_context: str = "",
    special_situation: str = "",
    needs_tupper: str = "",
    has_kitchen: str = "",
    days_away: str = "",
    profile_tags: list[str] | None = None,
) -> str:
    tags_text = _format_profile_tags(profile_tags or [])

    return f"""
Nombre: {nombre}
Objetivo: {objetivo}
Restricciones: {_safe_value(restricciones, "No especificadas")}
Preferencias: {_safe_value(preferencias, "No especificadas")}
Presupuesto semanal: {_clean_numeric_string(presupuesto)}
Contexto principal: {_format_context_value(meal_context)}
Situación especial: {_format_context_value(special_situation)}
Necesita tupper: {_format_yes_no_value(needs_tupper)}
Acceso a cocina: {_format_context_value(has_kitchen)}
Días fuera de casa: {_clean_numeric_string(days_away)}
Etiquetas de perfil detectadas: {tags_text}
""".strip()


def _normalize_plan_data(plan_data: Any) -> list[dict[str, str]]:
    if not isinstance(plan_data, list):
        raise ValueError("El plan generado no tiene un formato válido.")

    normalized: list[dict[str, str]] = []

    for index, item in enumerate(plan_data, start=1):
        if not isinstance(item, dict):
            raise ValueError(f"El elemento {index} del plan no es válido.")

        normalized_item = {
            "day": str(item.get("day", "")).strip(),
            "breakfast": str(item.get("breakfast", "")).strip(),
            "lunch": str(item.get("lunch", "")).strip(),
            "dinner": str(item.get("dinner", "")).strip(),
        }

        if not all(normalized_item.values()):
            raise ValueError(f"El día {index} contiene campos vacíos.")

        normalized.append(normalized_item)

    return normalized


def _build_day_rows(plan_data: list[dict[str, str]]) -> str:
    rows: list[str] = []

    for day_data in plan_data:
        rows.append(
            f"""
            <tr>
                <td class="day-cell">{escape(day_data["day"])}</td>
                <td>{escape(day_data["breakfast"])}</td>
                <td>{escape(day_data["lunch"])}</td>
                <td>{escape(day_data["dinner"])}</td>
            </tr>
            """
        )

    return "".join(rows)


def build_plan_html_table(
    plan_data: list[dict[str, str]],
    nombre: str = "",
    objetivo: str = "",
    restricciones: str = "",
    preferencias: str = "",
    presupuesto: str = "",
    meal_context: str = "",
    special_situation: str = "",
    needs_tupper: str = "",
    has_kitchen: str = "",
    days_away: str = "",
    profile_tags: list[str] | None = None,
) -> str:
    plan_data = _normalize_plan_data(plan_data)
    rows_html = _build_day_rows(plan_data)
    tags_text = _format_profile_tags(profile_tags or [])

    info_cliente = f"""
        <section class="client-info">
            <h1>Plan semanal personalizado</h1>
            <div class="meta-grid">
                <div class="meta-item"><span class="label">Cliente</span><span class="value">{escape(_safe_value(nombre, "No especificado"))}</span></div>
                <div class="meta-item"><span class="label">Objetivo</span><span class="value">{escape(_safe_value(objetivo, "No especificado"))}</span></div>
                <div class="meta-item"><span class="label">Restricciones</span><span class="value">{escape(_safe_value(restricciones, "No especificadas"))}</span></div>
                <div class="meta-item"><span class="label">Preferencias</span><span class="value">{escape(_safe_value(preferencias, "No especificadas"))}</span></div>
                <div class="meta-item"><span class="label">Presupuesto semanal</span><span class="value">{escape(_clean_numeric_string(presupuesto))}</span></div>
                <div class="meta-item"><span class="label">Contexto principal</span><span class="value">{escape(_safe_value(meal_context))}</span></div>
                <div class="meta-item"><span class="label">Situación especial</span><span class="value">{escape(_safe_value(special_situation, "No especificada"))}</span></div>
                <div class="meta-item"><span class="label">¿Necesita tupper?</span><span class="value">{escape(_safe_value(needs_tupper))}</span></div>
                <div class="meta-item"><span class="label">Acceso a cocina</span><span class="value">{escape(_safe_value(has_kitchen))}</span></div>
                <div class="meta-item"><span class="label">Días fuera de casa</span><span class="value">{escape(_clean_numeric_string(days_away))}</span></div>
                <div class="meta-item" style="grid-column: 1 / -1;"><span class="label">Etiquetas de perfil detectadas</span><span class="value">{escape(tags_text)}</span></div>
            </div>
            <p class="disclaimer">
                Este plan es orientativo y no sustituye el asesoramiento de un profesional sanitario.
            </p>
        </section>
    """

    return f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="utf-8">
        <title>Plan semanal personalizado</title>
        <style>
            @page {{
                size: A4;
                margin: 16mm;
            }}

            :root {{
                --texto: #24323f;
                --texto-secundario: #5f6c76;
                --borde: #d9e2ea;
                --borde-suave: #e9eff4;
                --fondo-cabecera: #eef4f8;
                --fondo-caja: #f8fbfd;
                --fondo-fila: #fafcfd;
            }}

            * {{
                box-sizing: border-box;
            }}

            body {{
                font-family: Arial, sans-serif;
                color: var(--texto);
                font-size: 13px;
                line-height: 1.5;
                margin: 0;
            }}

            h1 {{
                margin: 0 0 12px 0;
                color: #1f3b57;
                font-size: 24px;
                line-height: 1.2;
            }}

            .client-info {{
                margin-bottom: 22px;
                padding: 16px;
                border: 1px solid var(--borde);
                border-radius: 10px;
                background: var(--fondo-caja);
            }}

            .meta-grid {{
                display: grid;
                grid-template-columns: 1fr;
                gap: 10px;
                margin-top: 10px;
            }}

            .meta-item {{
                border: 1px solid var(--borde-suave);
                border-radius: 8px;
                background: #ffffff;
                padding: 10px;
            }}

            .label {{
                display: block;
                margin-bottom: 4px;
                font-size: 11px;
                font-weight: bold;
                text-transform: uppercase;
                color: var(--texto-secundario);
                letter-spacing: 0.02em;
            }}

            .value {{
                display: block;
                color: var(--texto);
                word-wrap: break-word;
                overflow-wrap: break-word;
            }}

            .disclaimer {{
                margin: 14px 0 0;
                font-size: 11px;
                color: var(--texto-secundario);
            }}

            table {{
                width: 100%;
                border-collapse: collapse;
                table-layout: fixed;
                font-size: 12px;
            }}

            thead {{
                display: table-header-group;
            }}

            tbody {{
                display: table-row-group;
            }}

            tr {{
                page-break-inside: avoid;
            }}

            th, td {{
                border: 1px solid var(--borde);
                padding: 10px;
                vertical-align: top;
                text-align: left;
                word-wrap: break-word;
                overflow-wrap: break-word;
            }}

            th {{
                background-color: var(--fondo-cabecera);
                color: #1f3b57;
                font-weight: bold;
            }}

            tbody tr:nth-child(even) td {{
                background-color: var(--fondo-fila);
            }}

            th:first-child,
            td.day-cell {{
                width: 14%;
                font-weight: bold;
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
                {rows_html}
            </tbody>
        </table>
    </body>
    </html>
    """


def _generate_plan_data(texto_cliente: str) -> tuple[list[dict[str, str]], str]:
    try:
        plan_data, provider = generate_meal_plan(texto_cliente)
        normalized_plan = _normalize_plan_data(plan_data)
        logger.info("Meal plan generated successfully with provider='%s'.", provider)
        return normalized_plan, provider

    except Exception as exc:
        logger.exception("AI meal plan generation failed: %s", exc)

        if DEMO_MODE_FALLBACK:
            logger.warning(
                "Using mock meal plan because DEMO_MODE_FALLBACK=True. Error: %s",
                exc,
            )
            return _normalize_plan_data(get_mock_meal_plan()), "mock"

        raise ValueError(f"Error real al generar el plan: {exc}") from exc


def _save_plan_files(nombre: str, tabla_html: str) -> dict[str, str]:
    output_dir = Path(settings.MEDIA_ROOT) / RESULTS_SUBDIR
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = timezone.now().strftime("%Y%m%d%H%M%S")
    safe_name = slugify(nombre) or "cliente"

    html_filename = f"plan_{safe_name}_{timestamp}.html"
    pdf_filename = f"plan_{safe_name}_{timestamp}.pdf"

    html_path = output_dir / html_filename
    pdf_path = output_dir / pdf_filename

    html_path.write_text(tabla_html, encoding="utf-8")
    HTML(
        string=tabla_html,
        base_url=str(Path(settings.BASE_DIR)),
    ).write_pdf(str(pdf_path))

    return {
        "html_filename": html_filename,
        "pdf_filename": pdf_filename,
        "html_url": f"{settings.MEDIA_URL}{RESULTS_SUBDIR}/{html_filename}",
        "pdf_url": f"{settings.MEDIA_URL}{RESULTS_SUBDIR}/{pdf_filename}",
    }


def _render_home_with_error(
    request,
    error_message: str,
    previous_data: dict[str, Any] | None = None,
):
    context: dict[str, Any] = {"error": error_message}
    if previous_data:
        context.update(previous_data)
    return render(request, "nutriprompt_app/home.html", context)


def procesar_plan_directo(request):
    if request.method != "POST":
        return render(request, "nutriprompt_app/home.html")

    form_data = _extract_form_data(request)
    previous_data = dict(form_data)

    nombre = form_data["nombre"]
    objetivo = form_data["objetivo"]
    restricciones = form_data["restricciones"]
    preferencias = form_data["preferencias"]
    presupuesto = form_data["presupuesto"]
    meal_context = form_data["meal_context"]
    special_situation = form_data["special_situation"]
    needs_tupper = form_data["needs_tupper"]
    has_kitchen = form_data["has_kitchen"]
    days_away = form_data["days_away"]
    accept_privacy = form_data["accept_privacy"]

    if not nombre or not objetivo:
        return _render_home_with_error(
            request,
            "Completa al menos el nombre y el objetivo principal.",
            previous_data,
        )

    if not accept_privacy:
        return _render_home_with_error(
            request,
            "Debes aceptar la política de privacidad antes de generar el plan.",
            previous_data,
        )

    profile_tags = classify_user_profile(
        objetivo=objetivo,
        restricciones=restricciones,
        preferencias=preferencias,
        presupuesto=presupuesto,
        meal_context=meal_context,
        special_situation=special_situation,
        needs_tupper=needs_tupper,
        has_kitchen=has_kitchen,
        days_away=days_away,
    )

    texto_cliente = _build_user_input_text(
        nombre=nombre,
        objetivo=objetivo,
        restricciones=restricciones,
        preferencias=preferencias,
        presupuesto=presupuesto,
        meal_context=meal_context,
        special_situation=special_situation,
        needs_tupper=needs_tupper,
        has_kitchen=has_kitchen,
        days_away=days_away,
        profile_tags=profile_tags,
    )

    try:
        plan_data, source_type = _generate_plan_data(texto_cliente)
        shopping_list = generate_shopping_list(plan_data)

        tabla_html = build_plan_html_table(
            plan_data=plan_data,
            nombre=nombre,
            objetivo=objetivo,
            restricciones=restricciones,
            preferencias=preferencias,
            presupuesto=presupuesto,
            meal_context=_format_context_value(meal_context),
            special_situation=_format_context_value(special_situation),
            needs_tupper=_format_yes_no_value(needs_tupper),
            has_kitchen=_format_context_value(has_kitchen),
            days_away=_clean_numeric_string(days_away),
            profile_tags=profile_tags,
        )

        archivos = _save_plan_files(nombre=nombre, tabla_html=tabla_html)

        resultado_guardado = {
            "plan": plan_data,
            "profile_tags": profile_tags,
            "shopping_list": shopping_list,
        }

        IAGeneratedResponse.objects.create(
            servicio="NutriPrompt",
            usuario=DEFAULT_USER_LABEL,
            paciente=nombre,
            entrada_usuario=texto_cliente,
            resultado_ia=json.dumps(resultado_guardado, ensure_ascii=False, indent=2),
            html_file=archivos["html_filename"],
            pdf_file=archivos["pdf_filename"],
        )

        logger.info(
            "Plan saved successfully for patient='%s' with source='%s', tags=%s and shopping_list=%s.",
            nombre,
            source_type,
            profile_tags,
            shopping_list,
        )

        return render(
            request,
            "nutriprompt_app/resultado.html",
            {
                "tabla_html": tabla_html,
                "pdf_url": archivos["pdf_url"],
                "html_url": archivos["html_url"],
                "nombre": nombre,
                "source_type": source_type,
                "profile_tags": profile_tags,
                "shopping_list": shopping_list,
            },
        )

    except Exception as exc:
        logger.exception("Error while processing plan for '%s'.", nombre)
        return _render_home_with_error(
            request,
            str(exc) or "Ha ocurrido un error inesperado al generar el plan.",
            previous_data,
        )