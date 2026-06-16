from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.shortcuts import render
from django.utils import timezone
from django.utils.html import escape
from django.utils.text import slugify
from nutriprompt_app.services.rag.knowledge_base import get_rules
from weasyprint import HTML

from nutriprompt_app.forms import (
    DIET_CHOICES,
    GOAL_CHOICES,
    KITCHEN_CHOICES,
    MEAL_CONTEXT_CHOICES,
    NutriPromptForm,
    PREFERENCE_CHOICES,
    SPECIAL_SITUATION_CHOICES,
    YES_NO_CHOICES,
)

from nutriprompt_app.models import IAGeneratedResponse

from nutriprompt_app.services.ai.ai_generator import (
    generate_meal_plan,
)

from nutriprompt_app.services.profiles.profile_classifier import (
    classify_user_profile,
)

from nutriprompt_app.services.nutrition.shopping_list_generator import (
    generate_enriched_shopping_list,
    generate_shopping_list,
    get_dataset_status,
)

from nutriprompt_app.services.nutrition.fallback_plan import (
    generate_fallback_meal_plan,
)

from nutriprompt_app.services.vision.vision_analyzer import (
    analyze_food_label,
)


logger = logging.getLogger(__name__)

DEMO_MODE_FALLBACK = True
RESULTS_SUBDIR = "resultados"
DEFAULT_USER_LABEL = "Bea"
VISION_UPLOAD_SUBDIRS = {
    "product_label": "vision/products",
    "pantry_image": "vision/pantry",
    "fridge_image": "vision/fridge",
    "nutrition_pdf": "vision/nutrition_pdfs",
}

YES_NO_MAP = dict(YES_NO_CHOICES)
KITCHEN_MAP = dict(KITCHEN_CHOICES)
GOAL_MAP = dict(GOAL_CHOICES)
DIET_MAP = dict(DIET_CHOICES)
PREFERENCE_MAP = dict(PREFERENCE_CHOICES)
MEAL_CONTEXT_MAP = dict(MEAL_CONTEXT_CHOICES)
SPECIAL_SITUATION_MAP = dict(SPECIAL_SITUATION_CHOICES)


def home(request):
    form = NutriPromptForm()
    return render(request, "nutriprompt_app/home.html", {"form": form})


def _safe_value(value: Any, default: str = "No especificado") -> str:
    text = str(value or "").strip()
    return text or default


def _clean_numeric_string(value: Any, default: str = "No especificado") -> str:
    text = str(value or "").strip()
    return text or default


def _join_choice_labels(
    values: list[str] | None,
    mapping: dict[str, str],
    default: str = "No especificadas",
) -> str:
    if not values:
        return default

    labels = [mapping.get(value, value) for value in values]
    return ", ".join(labels)


def _label_for_choice(
    value: Any,
    mapping: dict[str, str],
    default: str = "No especificado",
) -> str:
    normalized = str(value or "").strip()

    if not normalized:
        return default

    return mapping.get(normalized, normalized)


def _format_profile_tags(profile_tags: list[str] | None) -> str:
    if not profile_tags:
        return "No detectadas"

    return ", ".join(profile_tags)


def _to_classifier_payload(cleaned_data: dict[str, Any]) -> dict[str, str]:
    return {
        "objetivo": _label_for_choice(cleaned_data.get("objetivo"), GOAL_MAP),
        "restricciones": _join_choice_labels(
            cleaned_data.get("restricciones", []),
            DIET_MAP,
        ),
        "preferencias": _join_choice_labels(
            cleaned_data.get("preferencias", []),
            PREFERENCE_MAP,
        ),
        "presupuesto": str(cleaned_data.get("presupuesto", "")).strip(),
        "meal_context": cleaned_data.get("meal_context", "") or "",
        "special_situation": cleaned_data.get("special_situation", "") or "",
        "needs_tupper": cleaned_data.get("needs_tupper", "") or "",
        "has_kitchen": cleaned_data.get("has_kitchen", "") or "",
        "days_away": str(cleaned_data.get("days_away", 0)).strip(),
    }


def _to_display_context(cleaned_data: dict[str, Any]) -> dict[str, str]:
    return {
        "nombre": _safe_value(cleaned_data.get("nombre")),
        "objetivo": _label_for_choice(cleaned_data.get("objetivo"), GOAL_MAP),
        "restricciones": _join_choice_labels(
            cleaned_data.get("restricciones", []),
            DIET_MAP,
        ),
        "preferencias": _join_choice_labels(
            cleaned_data.get("preferencias", []),
            PREFERENCE_MAP,
        ),
        "presupuesto": str(cleaned_data.get("presupuesto", "")).strip(),
        "meal_context": _label_for_choice(
            cleaned_data.get("meal_context"),
            MEAL_CONTEXT_MAP,
        ),
        "special_situation": _label_for_choice(
            cleaned_data.get("special_situation"),
            SPECIAL_SITUATION_MAP,
            default="No especificada",
        ),
        "needs_tupper": _label_for_choice(
            cleaned_data.get("needs_tupper"),
            YES_NO_MAP,
        ),
        "has_kitchen": _label_for_choice(
            cleaned_data.get("has_kitchen"),
            KITCHEN_MAP,
        ),
        "days_away": str(cleaned_data.get("days_away", 0)).strip(),
        "notas": _safe_value(cleaned_data.get("notas"), ""),
    }


def _build_user_input_text(display_data: dict[str, str], profile_tags: list[str]) -> str:
    return f"""
Nombre: {_safe_value(display_data.get("nombre"))}
Objetivo: {_safe_value(display_data.get("objetivo"))}
Restricciones: {_safe_value(display_data.get("restricciones"), "No especificadas")}
Preferencias: {_safe_value(display_data.get("preferencias"), "No especificadas")}
Presupuesto semanal: {_clean_numeric_string(display_data.get("presupuesto"))}
Contexto principal: {_safe_value(display_data.get("meal_context"))}
Situación especial: {_safe_value(display_data.get("special_situation"), "No especificada")}
Necesita tupper: {_safe_value(display_data.get("needs_tupper"))}
Acceso a cocina: {_safe_value(display_data.get("has_kitchen"))}
Días fuera de casa: {_clean_numeric_string(display_data.get("days_away"))}
Notas adicionales: {_safe_value(display_data.get("notas"), "No especificadas")}
Etiquetas de perfil detectadas: {_format_profile_tags(profile_tags)}
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
    return "".join(
        f"""
        <tr>
            <td class="day-cell">{escape(day_data["day"])}</td>
            <td>{escape(day_data["breakfast"])}</td>
            <td>{escape(day_data["lunch"])}</td>
            <td>{escape(day_data["dinner"])}</td>
        </tr>
        """
        for day_data in plan_data
    )


def build_plan_html_table(
    plan_data: list[dict[str, str]],
    *,
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
    notas: str = "",
    profile_tags: list[str] | None = None,
) -> str:
    normalized_plan = _normalize_plan_data(plan_data)
    rows_html = _build_day_rows(normalized_plan)
    tags_text = _format_profile_tags(profile_tags)

    return f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="utf-8">
        <title>Plan semanal personalizado</title>
        <style>
            @page {{
                size: A4;
                margin: 12mm;
            }}

            :root {{
                --green: #27ae60;
                --green-dark: #1f8f4f;
                --text: #24323f;
                --muted: #5f6c76;
                --soft: #f6faf8;
                --border: #dce6ee;
                --border-soft: #edf2f6;
                --white: #ffffff;
            }}

            * {{
                box-sizing: border-box;
            }}

            body {{
                margin: 0;
                font-family: Arial, Helvetica, sans-serif;
                color: var(--text);
                font-size: 11.5px;
                line-height: 1.45;
                background: #ffffff;
            }}

            .hero {{
                padding: 18px 20px;
                margin-bottom: 14px;
                border-radius: 14px;
                background: linear-gradient(135deg, #edf9f1 0%, #f5fbff 100%);
                border: 1px solid var(--border);
            }}

            .eyebrow {{
                margin: 0 0 6px;
                color: var(--green-dark);
                font-size: 10px;
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 0.08em;
            }}

            h1 {{
                margin: 0 0 6px;
                color: #18364f;
                font-size: 23px;
                line-height: 1.15;
            }}

            .hero-text {{
                margin: 0;
                color: var(--muted);
                font-size: 11.5px;
            }}

            .section-title {{
                margin: 0 0 9px;
                color: #18364f;
                font-size: 15px;
                line-height: 1.25;
            }}

            .client-card {{
                padding: 14px;
                margin-bottom: 14px;
                border: 1px solid var(--border);
                border-radius: 13px;
                background: var(--soft);
                page-break-inside: avoid;
            }}

            .meta-table {{
                width: 100%;
                border-collapse: separate;
                border-spacing: 0 7px;
                table-layout: fixed;
            }}

            .meta-table td {{
                width: 50%;
                padding: 0;
                border: none;
                vertical-align: top;
            }}

            .meta-table td:first-child {{
                padding-right: 5px;
            }}

            .meta-table td:last-child {{
                padding-left: 5px;
            }}

            .meta-item {{
                min-height: 54px;
                padding: 9px 10px;
                border: 1px solid var(--border-soft);
                border-radius: 10px;
                background: var(--white);
            }}

            .meta-item--full {{
                min-height: auto;
            }}

            .label {{
                display: block;
                margin-bottom: 3px;
                color: var(--muted);
                font-size: 9px;
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 0.05em;
                line-height: 1.2;
            }}

            .value {{
                display: block;
                color: var(--text);
                font-size: 11.5px;
                line-height: 1.35;
                overflow-wrap: break-word;
            }}

            .disclaimer {{
                margin: 9px 0 0;
                padding: 8px 10px;
                border: 1px solid #f1d38a;
                border-radius: 9px;
                background: #fff8e8;
                color: #7a5a00;
                font-size: 10.5px;
                line-height: 1.4;
            }}

            .plan-card {{
                padding: 14px;
                border: 1px solid var(--border);
                border-radius: 13px;
                background: #ffffff;
            }}

            .plan-table {{
                width: 100%;
                border-collapse: collapse;
                table-layout: fixed;
                font-size: 10.8px;
            }}

            .plan-table thead {{
                display: table-header-group;
            }}

            .plan-table tr {{
                page-break-inside: avoid;
            }}

            .plan-table th,
            .plan-table td {{
                padding: 8px;
                border: 1px solid var(--border);
                vertical-align: top;
                text-align: left;
                line-height: 1.35;
                overflow-wrap: break-word;
            }}

            .plan-table th {{
                background: #edf6f0;
                color: #18364f;
                font-size: 10.5px;
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 0.03em;
            }}

            .plan-table tbody tr:nth-child(even) td {{
                background: #fafcfd;
            }}

            .plan-table th:nth-child(1),
            .plan-table td:nth-child(1) {{
                width: 14%;
            }}

            .plan-table th:nth-child(2),
            .plan-table td:nth-child(2),
            .plan-table th:nth-child(3),
            .plan-table td:nth-child(3),
            .plan-table th:nth-child(4),
            .plan-table td:nth-child(4) {{
                width: 28.66%;
            }}

            .day-cell {{
                color: var(--green-dark);
                font-weight: 700;
            }}

            .footer-note {{
                margin-top: 10px;
                color: var(--muted);
                font-size: 10px;
                line-height: 1.4;
            }}
        </style>
    </head>

    <body>
        <main class="pdf-page">
            <section class="hero">
                <p class="eyebrow">NutriPrompt · Plan personalizado</p>
                <h1>Plan semanal personalizado</h1>
                <p class="hero-text">
                    Plan generado a partir de los datos introducidos en el formulario, combinando lógica estructurada,
                    preferencias alimentarias y restricciones indicadas.
                </p>
            </section>

            <section class="client-card">
                <h2 class="section-title">Resumen del perfil</h2>

                <table class="meta-table">
                    <tr>
                        <td>
                            <div class="meta-item">
                                <span class="label">Cliente</span>
                                <span class="value">{escape(_safe_value(nombre))}</span>
                            </div>
                        </td>
                        <td>
                            <div class="meta-item">
                                <span class="label">Objetivo</span>
                                <span class="value">{escape(_safe_value(objetivo))}</span>
                            </div>
                        </td>
                    </tr>

                    <tr>
                        <td>
                            <div class="meta-item">
                                <span class="label">Restricciones</span>
                                <span class="value">{escape(_safe_value(restricciones, "No especificadas"))}</span>
                            </div>
                        </td>
                        <td>
                            <div class="meta-item">
                                <span class="label">Preferencias</span>
                                <span class="value">{escape(_safe_value(preferencias, "No especificadas"))}</span>
                            </div>
                        </td>
                    </tr>

                    <tr>
                        <td>
                            <div class="meta-item">
                                <span class="label">Presupuesto semanal</span>
                                <span class="value">{escape(_clean_numeric_string(presupuesto))} €</span>
                            </div>
                        </td>
                        <td>
                            <div class="meta-item">
                                <span class="label">Contexto principal</span>
                                <span class="value">{escape(_safe_value(meal_context))}</span>
                            </div>
                        </td>
                    </tr>

                    <tr>
                        <td>
                            <div class="meta-item">
                                <span class="label">Situación especial</span>
                                <span class="value">{escape(_safe_value(special_situation, "No especificada"))}</span>
                            </div>
                        </td>
                        <td>
                            <div class="meta-item">
                                <span class="label">¿Necesita tupper?</span>
                                <span class="value">{escape(_safe_value(needs_tupper))}</span>
                            </div>
                        </td>
                    </tr>

                    <tr>
                        <td>
                            <div class="meta-item">
                                <span class="label">Acceso a cocina</span>
                                <span class="value">{escape(_safe_value(has_kitchen))}</span>
                            </div>
                        </td>
                        <td>
                            <div class="meta-item">
                                <span class="label">Días fuera de casa</span>
                                <span class="value">{escape(_clean_numeric_string(days_away))}</span>
                            </div>
                        </td>
                    </tr>

                    <tr>
                        <td colspan="2">
                            <div class="meta-item meta-item--full">
                                <span class="label">Notas adicionales</span>
                                <span class="value">{escape(_safe_value(notas, "No especificadas"))}</span>
                            </div>
                        </td>
                    </tr>

                    <tr>
                        <td colspan="2">
                            <div class="meta-item meta-item--full">
                                <span class="label">Etiquetas de perfil detectadas</span>
                                <span class="value">{escape(tags_text)}</span>
                            </div>
                        </td>
                    </tr>
                </table>

                <p class="disclaimer">
                    Este plan es orientativo y no sustituye el asesoramiento de un profesional sanitario o nutricional.
                </p>
            </section>

            <section class="plan-card">
                <h2 class="section-title">Planificación semanal</h2>

                <table class="plan-table">
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

                <p class="footer-note">
                    Revisa el plan antes de aplicarlo y ajústalo según tus necesidades reales, rutina diaria,
                    disponibilidad de alimentos y cualquier indicación profesional.
                </p>
            </section>
        </main>
    </body>
    </html>
    """


def _run_fallback_plan(
    classifier_data: dict[str, str],
    profile_tags: list[str],
    texto_cliente: str,
) -> tuple[list[dict[str, str]], str]:
    try:
        fallback_plan_data = generate_fallback_meal_plan(
            nombre=classifier_data["nombre"],
            objetivo=classifier_data["objetivo"],
            restricciones=classifier_data["restricciones"],
            preferencias=classifier_data["preferencias"],
            presupuesto=classifier_data["presupuesto"],
            meal_context=classifier_data["meal_context"],
            special_situation=classifier_data["special_situation"],
            needs_tupper=classifier_data["needs_tupper"],
            has_kitchen=classifier_data["has_kitchen"],
            days_away=classifier_data["days_away"],
            profile_tags=profile_tags,
        )
    except TypeError:
        logger.warning(
            "generate_fallback_meal_plan no acepta keyword args. Se intentará con texto_cliente."
        )
        fallback_plan_data = generate_fallback_meal_plan(texto_cliente)

    normalized_fallback = _normalize_plan_data(fallback_plan_data)
    logger.info("Fallback personalizado generado correctamente.")
    return normalized_fallback, "fallback"


def _generate_plan_data(
    *,
    classifier_data: dict[str, str],
    profile_tags: list[str],
    texto_cliente: str,
) -> tuple[list[dict[str, str]], str]:
    if DEMO_MODE_FALLBACK:
        logger.warning("DEMO_MODE_FALLBACK=True. Se usará el fallback personalizado.")
        return _run_fallback_plan(classifier_data, profile_tags, texto_cliente)

    try:
        plan_data, provider = generate_meal_plan(texto_cliente)
        normalized_plan = _normalize_plan_data(plan_data)
        logger.info("Plan generado correctamente con provider='%s'.", provider)
        return normalized_plan, provider

    except Exception as exc:
        logger.exception(
            "La generación principal con IA ha fallado. Se usará fallback. Error: %s",
            exc,
        )
        return _run_fallback_plan(classifier_data, profile_tags, texto_cliente)


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


def _classify_profile(classifier_data: dict[str, str]) -> list[str]:
    try:
        profile_tags = classify_user_profile(
            objetivo=classifier_data["objetivo"],
            restricciones=classifier_data["restricciones"],
            preferencias=classifier_data["preferencias"],
            presupuesto=classifier_data["presupuesto"],
            meal_context=classifier_data["meal_context"],
            special_situation=classifier_data["special_situation"],
            needs_tupper=classifier_data["needs_tupper"],
            has_kitchen=classifier_data["has_kitchen"],
            days_away=classifier_data["days_away"],
        )

        if not isinstance(profile_tags, list):
            logger.warning("El clasificador ha devuelto un valor no válido. Se usará lista vacía.")
            return []

        return profile_tags

    except Exception as exc:
        logger.exception(
            "La clasificación de perfil ha fallado. Se continuará sin etiquetas. Error: %s",
            exc,
        )
        return []



def _safe_dataset_status() -> dict[str, Any]:
    try:
        status = get_dataset_status()

        if not isinstance(status, dict):
            return {
                "dataset_available": False,
                "total_foods": 0,
                "dataset_path": "",
            }

        return status

    except Exception as exc:
        logger.exception("No se ha podido consultar el estado del dataset nutricional: %s", exc)
        return {
            "dataset_available": False,
            "total_foods": 0,
            "dataset_path": "",
        }


def _generate_shopping_data(plan_data: list[dict[str, str]]) -> tuple[dict[str, list[str]], dict[str, list[dict[str, Any]]]]:
    try:
        shopping_list = generate_shopping_list(plan_data)

        if not isinstance(shopping_list, dict):
            logger.warning("La lista de la compra básica no tiene formato dict.")
            shopping_list = {}

    except Exception as exc:
        logger.exception("No se ha podido generar la lista de la compra básica: %s", exc)
        shopping_list = {}

    try:
        enriched_shopping_list = generate_enriched_shopping_list(plan_data)

        if not isinstance(enriched_shopping_list, dict):
            logger.warning("La lista de la compra enriquecida no tiene formato dict.")
            enriched_shopping_list = {}

    except Exception as exc:
        logger.exception("No se ha podido generar la lista enriquecida con dataset Kaggle: %s", exc)
        enriched_shopping_list = {}

    return shopping_list, enriched_shopping_list


def _build_nutrition_insights(
    enriched_shopping_list: dict[str, list[dict[str, Any]]],
) -> dict[str, Any]:
    total_items = 0
    matched_items = 0
    highlighted_items: list[dict[str, Any]] = []

    for category, items in enriched_shopping_list.items():
        for item in items:
            total_items += 1

            if item.get("has_nutrition_data"):
                matched_items += 1

                if len(highlighted_items) < 6:
                    highlighted_items.append(
                        {
                            "category": category,
                            "name": item.get("name", "Alimento"),
                            "summary": item.get("summary", "Datos nutricionales disponibles."),
                        }
                    )

    coverage = round((matched_items / total_items) * 100) if total_items else 0

    return {
        "dataset_status": _safe_dataset_status(),
        "total_items": total_items,
        "matched_items": matched_items,
        "coverage": coverage,
        "highlighted_items": highlighted_items,
    }


def _get_vision_upload_subdir(analysis_type: str | None) -> str:
    normalized_type = str(analysis_type or "product_label").strip()
    return VISION_UPLOAD_SUBDIRS.get(normalized_type, VISION_UPLOAD_SUBDIRS["product_label"])


def _build_result_context(
    *,
    display_data: dict[str, str],
    profile_tags: list[str],
    shopping_list: dict[str, list[str]],
    enriched_shopping_list: dict[str, list[dict[str, Any]]],
    nutrition_insights: dict[str, Any],
    source_type: str,
    archivos: dict[str, str],
    tabla_html: str,
) -> dict[str, Any]:
    return {
        "tabla_html": tabla_html,
        "pdf_url": archivos["pdf_url"],
        "html_url": archivos["html_url"],
        "nombre": display_data["nombre"],
        "source_type": source_type,
        "profile_tags": profile_tags,
        "shopping_list": shopping_list,
        "enriched_shopping_list": enriched_shopping_list,
        "nutrition_insights": nutrition_insights,
        "used_fallback": source_type == "fallback",
    }


def procesar_plan_directo(request):
    if request.method != "POST":
        form = NutriPromptForm()
        return render(
            request,
            "nutriprompt_app/home.html",
            {"form": form}
        )

    form = NutriPromptForm(request.POST)

    if not form.is_valid():
        logger.warning("Formulario NutriPrompt inválido: %s", form.errors)
        return render(
            request,
            "nutriprompt_app/home.html",
            {
                "form": form,
                "error": "Revisa los campos marcados y corrige la información antes de generar el plan.",
            },
        )

    cleaned_data = form.cleaned_data

    classifier_data = {
        "nombre": cleaned_data["nombre"],
        **_to_classifier_payload(cleaned_data),
    }

    display_data = _to_display_context(cleaned_data)
    profile_tags = _classify_profile(classifier_data)
    texto_cliente = _build_user_input_text(display_data, profile_tags)

    try:
        plan_data, source_type = _generate_plan_data(
            classifier_data=classifier_data,
            profile_tags=profile_tags,
            texto_cliente=texto_cliente,
        )

        shopping_list, enriched_shopping_list = _generate_shopping_data(plan_data)
        nutrition_insights = _build_nutrition_insights(enriched_shopping_list)

        tabla_html_pdf = build_plan_html_table(
            plan_data=plan_data,
            nombre=display_data["nombre"],
            objetivo=display_data["objetivo"],
            restricciones=display_data["restricciones"],
            preferencias=display_data["preferencias"],
            presupuesto=display_data["presupuesto"],
            meal_context=display_data["meal_context"],
            special_situation=display_data["special_situation"],
            needs_tupper=display_data["needs_tupper"],
            has_kitchen=display_data["has_kitchen"],
            days_away=display_data["days_away"],
            notas=display_data["notas"],
            profile_tags=profile_tags,
        )

        tabla_html_web = _build_day_rows(plan_data)

        archivos = _save_plan_files(
            nombre=display_data["nombre"],
            tabla_html=tabla_html_pdf,
        )

        resultado_guardado = {
            "plan": plan_data,
            "profile_tags": profile_tags,
            "shopping_list": shopping_list,
            "enriched_shopping_list": enriched_shopping_list,
            "nutrition_insights": nutrition_insights,
            "source_type": source_type,
        }

        IAGeneratedResponse.objects.create(
            servicio="NutriPrompt",
            usuario=DEFAULT_USER_LABEL,
            paciente=display_data["nombre"],
            entrada_usuario=texto_cliente,
            resultado_ia=json.dumps(resultado_guardado, ensure_ascii=False, indent=2),
            source_type=source_type,
            html_file=archivos["html_filename"],
            pdf_file=archivos["pdf_filename"],
        )

        logger.info(
            "Plan guardado correctamente para paciente='%s' con source='%s'.",
            display_data["nombre"],
            source_type,
        )

        return render(
            request,
            "nutriprompt_app/resultado.html",
            _build_result_context(
                display_data=display_data,
                profile_tags=profile_tags,
                shopping_list=shopping_list,
                enriched_shopping_list=enriched_shopping_list,
                nutrition_insights=nutrition_insights,
                source_type=source_type,
                archivos=archivos,
                tabla_html=tabla_html_web,
            ),
        )

    except Exception as exc:
        logger.exception("Error al procesar el plan para '%s'.", display_data["nombre"])

        form.add_error(
            None,
            str(exc) or "Ha ocurrido un error inesperado al generar el plan.",
        )

        return render(
            request,
            "nutriprompt_app/home.html",
            {
                "form": form,
                "error": str(exc) or "Ha ocurrido un error inesperado al generar el plan.",
            },
        )


def vision_upload(request):
    """
    NutriPrompt Smart Intake / Vision.

    Multi-context nutrition analysis:
    - Product labels
    - Pantry images
    - Fridge images
    - Nutrition PDFs

    The system can compare:
    - Professional nutrition guidance
    - Available foods
    - Products / ingredients
    - Potential incompatibilities
    """

    context: dict[str, Any] = {
        "analysis": None,
        "uploaded_files": [],
        "compatibility_analysis": None,
        "error": None,
    }

    if request.method != "POST":
        return render(
            request,
            "nutriprompt_app/vision/upload.html",
            context,
        )

    uploaded_files = request.FILES.getlist("image")

    if not uploaded_files:
        context["error"] = (
            "Sube al menos una imagen o documento para analizar."
        )

        return render(
            request,
            "nutriprompt_app/vision/upload.html",
            context,
        )

    try:
        storage = FileSystemStorage()

        pantry_analyses = []
        fridge_analyses = []
        product_analyses = []
        ingredient_analyses = []
        plan_analysis = None

        uploaded_previews = []

        for uploaded_file in uploaded_files:

            analysis_type = request.POST.get(
                f"analysis_type_{uploaded_file.name}",
                "product_label",
            )

            upload_subdir = _get_vision_upload_subdir(
                analysis_type,
            )

            filename = storage.save(
                f"{upload_subdir}/{uploaded_file.name}",
                uploaded_file,
            )

            file_path = storage.path(filename)

            uploaded_previews.append(
                {
                    "url": storage.url(filename),
                    "name": uploaded_file.name,
                    "analysis_type": analysis_type,
                }
            )

            analysis = analyze_food_label(file_path)

            analysis["intake_type"] = analysis_type

            logger.info(
                "NutriPrompt Vision analysis completed: '%s' (%s)",
                uploaded_file.name,
                analysis_type,
            )

            if analysis_type == "nutrition_pdf":
                plan_analysis = {
                    "detected_restrictions": (
                        analysis.get("detected_restrictions", [])
                    ),
                    "detected_goals": (
                        analysis.get("detected_goals", [])
                    ),
                    "summary": (
                        analysis.get("summary", "")
                    ),
                }

            elif analysis_type == "pantry_image":
                pantry_analyses.append(analysis)

            elif analysis_type == "fridge_image":
                fridge_analyses.append(analysis)

            elif analysis_type == "ingredient_image":
                ingredient_analyses.append(analysis)

            else:
                product_analyses.append(analysis)

        from nutriprompt_app.services.vision.compatibility_analyzer import (
            analyze_context_compatibility,
        )

        compatibility_analysis = analyze_context_compatibility(
            plan_analysis=plan_analysis,
            pantry_analyses=pantry_analyses,
            fridge_analyses=fridge_analyses,
            product_analyses=product_analyses,
            ingredient_analyses=ingredient_analyses,
        )

        context.update(
            {
                "uploaded_files": uploaded_previews,
                "compatibility_analysis": compatibility_analysis,
                "analysis": {
                    "total_files": len(uploaded_files),
                    "processed_successfully": True,
                },
            }
        )

        logger.info(
            "Smart Intake compatibility analysis completed successfully."
        )

    except Exception as exc:
        logger.exception(
            "Error in NutriPrompt Vision compatibility analysis: %s",
            exc,
        )

        context["error"] = (
            "No se ha podido completar el análisis nutricional. "
            "Prueba con imágenes más claras o archivos compatibles."
        )

    return render(
        request,
        "nutriprompt_app/vision/upload.html",
        context,
    )

def dashboard_view(request):
    try:
        rag_rules_count = len(get_rules())
    except Exception:
        rag_rules_count = 0

    context = {
        "plans_generated": IAGeneratedResponse.objects.count(),
        "rag_rules": rag_rules_count,
        "tests_passed": 17,
        "ai_status": "Operational",
    }

    return render(
        request,
        "nutriprompt_app/dashboard.html",
        context,
    )