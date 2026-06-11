import re
from datetime import datetime
from io import BytesIO
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import registerFontFamily
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


SYSTEM_NAME = "Информационная система мониторинга финансово-экономических показателей"

FONT_CANDIDATES = [
    "/usr/share/fonts/TTF/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/noto/NotoSans-Regular.ttf",
    "/usr/share/fonts/liberation/LiberationSans-Regular.ttf",
]

BOLD_FONT_CANDIDATES = [
    "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/noto/NotoSans-Bold.ttf",
    "/usr/share/fonts/liberation/LiberationSans-Bold.ttf",
]


def generate_pdf_report(
    metrics,
    monthly_summary,
    models_results,
    best_model_name,
    forecast_model_name,
    future_forecast,
    risk_score,
    risk_level,
    risk_factors,
    ai_conclusion,
    final_summary=None,
):
    font_name = _register_cyrillic_fonts()
    styles = _build_styles(font_name)

    buffer = BytesIO()
    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=1.5 * cm,
        leftMargin=1.5 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm,
        title="Итоговый финансовый отчет",
    )

    story = [
        Paragraph("Итоговый PDF-отчет", styles["Title"]),
        Paragraph(SYSTEM_NAME, styles["ReportSubtitle"]),
        Paragraph(
            f"Дата формирования отчета: {datetime.now().strftime('%d.%m.%Y %H:%M')}",
            styles["Normal"],
        ),
        Spacer(1, 0.45 * cm),
    ]

    story.extend(
        [
            Paragraph("Основные финансовые показатели", styles["Heading2"]),
            _build_key_values_table(
                [
                    ("Доходы", _format_money(metrics["total_income"])),
                    ("Расходы", _format_money(metrics["total_expense"])),
                    ("Прибыль", _format_money(metrics["total_profit"])),
                    ("Рентабельность", _format_percent(metrics["profitability"])),
                ],
                styles,
                font_name,
            ),
            Spacer(1, 0.35 * cm),
            Paragraph("Помесячная сводка", styles["Heading2"]),
            _build_dataframe_table(
                monthly_summary[["month", "income", "expense", "profit"]],
                ["Месяц", "Доходы", "Расходы", "Прибыль"],
                styles,
                font_name,
                money_columns={"income", "expense", "profit"},
            ),
        ]
    )

    story.extend(
        [
            PageBreak(),
            Paragraph("Результаты прогнозирования", styles["Heading2"]),
            _build_models_table(models_results, styles, font_name),
            Spacer(1, 0.25 * cm),
            _build_key_values_table(
                [
                    ("Выбранная модель для прогноза", forecast_model_name),
                    ("Лучшая модель по тестовой MAE", best_model_name),
                ],
                styles,
                font_name,
            ),
            Spacer(1, 0.35 * cm),
            Paragraph("Прогноз прибыли на будущие периоды", styles["Heading2"]),
            _build_dataframe_table(
                future_forecast,
                ["Номер месяца", "Прогноз прибыли"],
                styles,
                font_name,
                money_columns={"predicted_profit"},
            ),
            Spacer(1, 0.45 * cm),
            Paragraph("Результаты риск-скоринга", styles["Heading2"]),
            _build_key_values_table(
                [
                    ("Итоговый балл риска", f"{risk_score} из 100"),
                    ("Уровень риска", str(risk_level).capitalize()),
                ],
                styles,
                font_name,
            ),
            Spacer(1, 0.25 * cm),
            _build_risk_table(risk_factors, styles, font_name),
        ]
    )

    story.extend(
        [
            PageBreak(),
            Paragraph("AI-заключение", styles["Heading2"]),
            *_build_ai_conclusion_flowables(ai_conclusion, styles),
            Spacer(1, 0.45 * cm),
            Paragraph("Краткий итоговый вывод", styles["Heading2"]),
            Paragraph(_clean_text(final_summary or _build_final_summary(metrics, risk_level)), styles["ReportBody"]),
        ]
    )

    document.build(story)
    buffer.seek(0)
    return buffer.getvalue()


def _register_cyrillic_fonts():
    regular_font_path = None
    for font_path in FONT_CANDIDATES:
        if Path(font_path).exists():
            regular_font_path = font_path
            break

    if not regular_font_path:
        return "Helvetica"

    pdfmetrics.registerFont(TTFont("ReportFont", regular_font_path))

    bold_font_path = None
    for font_path in BOLD_FONT_CANDIDATES:
        if Path(font_path).exists():
            bold_font_path = font_path
            break

    if bold_font_path:
        pdfmetrics.registerFont(TTFont("ReportFont-Bold", bold_font_path))
        registerFontFamily(
            "ReportFont",
            normal="ReportFont",
            bold="ReportFont-Bold",
            italic="ReportFont",
            boldItalic="ReportFont-Bold",
        )
    else:
        registerFontFamily(
            "ReportFont",
            normal="ReportFont",
            bold="ReportFont",
            italic="ReportFont",
            boldItalic="ReportFont",
        )

    return "ReportFont"


def _build_styles(font_name):
    styles = getSampleStyleSheet()
    styles["Title"].fontName = font_name
    styles["Title"].fontSize = 17
    styles["Title"].leading = 21
    styles["Title"].alignment = TA_CENTER
    styles["Title"].spaceAfter = 10

    styles["Normal"].fontName = font_name
    styles["Heading2"].fontName = font_name
    styles["Heading2"].fontSize = 12
    styles["Heading2"].leading = 15
    styles["Heading2"].spaceBefore = 8
    styles["Heading2"].spaceAfter = 6

    styles.add(
        ParagraphStyle(
            name="ReportSubtitle",
            parent=styles["Normal"],
            fontName=font_name,
            fontSize=10,
            leading=14,
            alignment=TA_CENTER,
            spaceAfter=16,
        )
    )
    styles.add(
        ParagraphStyle(
            name="ReportBody",
            parent=styles["Normal"],
            fontName=font_name,
            fontSize=9.5,
            leading=13,
        )
    )
    styles.add(
        ParagraphStyle(
            name="ReportAIHeading",
            parent=styles["Normal"],
            fontName=font_name,
            fontSize=11.5,
            leading=15,
            spaceBefore=6,
            spaceAfter=4,
        )
    )
    styles.add(
        ParagraphStyle(
            name="ReportAIText",
            parent=styles["Normal"],
            fontName=font_name,
            fontSize=10.5,
            leading=14.5,
            spaceAfter=5,
        )
    )
    styles.add(
        ParagraphStyle(
            name="ReportAIList",
            parent=styles["ReportAIText"],
            leftIndent=0.45 * cm,
            firstLineIndent=0,
            bulletIndent=0.1 * cm,
            spaceAfter=3,
        )
    )

    return styles


def _build_key_values_table(rows, styles, font_name):
    table_data = [
        [Paragraph(str(label), styles["ReportBody"]), Paragraph(str(value), styles["ReportBody"])]
        for label, value in rows
    ]
    table = Table(table_data, colWidths=[8 * cm, 8 * cm], hAlign="LEFT")
    table.setStyle(_base_table_style(font_name))
    return table


def _build_models_table(models_results, styles, font_name):
    table_data = [[
        Paragraph("Модель", styles["ReportBody"]),
        Paragraph("MAE", styles["ReportBody"]),
        Paragraph("RMSE", styles["ReportBody"]),
    ]]

    for model_name, result in models_results.items():
        table_data.append(
            [
                Paragraph(str(model_name), styles["ReportBody"]),
                Paragraph(_format_number(result["mae"]), styles["ReportBody"]),
                Paragraph(_format_number(result["rmse"]), styles["ReportBody"]),
            ]
        )

    table = Table(table_data, colWidths=[7 * cm, 4.5 * cm, 4.5 * cm], hAlign="LEFT")
    table.setStyle(_base_table_style(font_name, header=True))
    return table


def _build_dataframe_table(dataframe, headers, styles, font_name, money_columns=None):
    money_columns = money_columns or set()
    columns = list(dataframe.columns)
    table_data = [[Paragraph(header, styles["ReportBody"]) for header in headers]]

    for _, row in dataframe.iterrows():
        table_row = []
        for column in columns:
            value = row[column]
            if column in money_columns:
                value = _format_money(value)
            table_row.append(Paragraph(str(value), styles["ReportBody"]))
        table_data.append(table_row)

    column_width = 16 * cm / len(headers)
    table = Table(table_data, colWidths=[column_width] * len(headers), hAlign="LEFT", repeatRows=1)
    table.setStyle(_base_table_style(font_name, header=True))
    return table


def _build_risk_table(risk_factors, styles, font_name):
    table_data = [[
        Paragraph("Фактор риска", styles["ReportBody"]),
        Paragraph("Баллы", styles["ReportBody"]),
        Paragraph("Выполнено", styles["ReportBody"]),
        Paragraph("Начислено", styles["ReportBody"]),
    ]]

    for factor in risk_factors:
        triggered = factor["triggered"]
        table_data.append(
            [
                Paragraph(str(factor["condition"]), styles["ReportBody"]),
                Paragraph(str(factor["points"]), styles["ReportBody"]),
                Paragraph("Да" if triggered else "Нет", styles["ReportBody"]),
                Paragraph(str(factor["points"] if triggered else 0), styles["ReportBody"]),
            ]
        )

    table = Table(table_data, colWidths=[9 * cm, 2 * cm, 2.5 * cm, 2.5 * cm], hAlign="LEFT", repeatRows=1)
    table.setStyle(_base_table_style(font_name, header=True))
    return table


def _base_table_style(font_name, header=False):
    commands = [
        ("FONTNAME", (0, 0), (-1, -1), font_name),
        ("FONTSIZE", (0, 0), (-1, -1), 8.5),
        ("LEADING", (0, 0), (-1, -1), 11),
        ("GRID", (0, 0), (-1, -1), 0.3, colors.lightgrey),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]

    if header:
        commands.extend(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E9EEF5")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#1F2937")),
            ]
        )

    return TableStyle(commands)


def _format_money(value):
    return f"{value:,.0f} руб.".replace(",", " ")


def _format_number(value):
    return f"{value:,.0f}".replace(",", " ")


def _format_percent(value):
    return f"{value:.2%}"


def _clean_text(text):
    return "<br/>".join(escape(line) for line in str(text).strip().splitlines())


def _build_ai_conclusion_flowables(text, styles):
    flowables = []

    for raw_line in str(text).strip().splitlines():
        line = raw_line.strip()

        if not line:
            if flowables and not isinstance(flowables[-1], Spacer):
                flowables.append(Spacer(1, 0.12 * cm))
            continue

        heading = _extract_markdown_heading(line)
        if heading:
            if flowables and not isinstance(flowables[-1], Spacer):
                flowables.append(Spacer(1, 0.08 * cm))
            flowables.append(
                Paragraph(f"<b>{escape(heading)}</b>", styles["ReportAIHeading"])
            )
            continue

        list_item = _extract_markdown_list_item(line)
        if list_item:
            flowables.append(
                Paragraph(
                    _format_inline_markdown(list_item),
                    styles["ReportAIList"],
                    bulletText="-",
                )
            )
            continue

        flowables.append(
            Paragraph(_format_inline_markdown(line), styles["ReportAIText"])
        )

    return flowables or [Paragraph("Заключение отсутствует.", styles["ReportAIText"])]


def _extract_markdown_heading(line):
    line = re.sub(r"^#{1,6}\s+", "", line).strip()
    markdown_heading = re.fullmatch(
        r"(?:\d+[.)]\s*)?\*\*(.+?)\*\*\s*:?",
        line,
    )

    if markdown_heading:
        return markdown_heading.group(1).strip()

    numbered_heading = re.fullmatch(r"\d+[.)]\s+(.+)", line)
    if numbered_heading and len(numbered_heading.group(1)) <= 90:
        return numbered_heading.group(1).strip()

    return None


def _extract_markdown_list_item(line):
    list_item = re.match(r"^[-–—]\s+(.+)", line)
    if list_item:
        return list_item.group(1).strip()

    return None


def _format_inline_markdown(text):
    parts = []
    position = 0

    for match in re.finditer(r"\*\*(.+?)\*\*", text):
        parts.append(escape(text[position:match.start()]))
        parts.append(f"<b>{escape(match.group(1))}</b>")
        position = match.end()

    parts.append(escape(text[position:]))
    return "".join(parts)


def _build_final_summary(metrics, risk_level):
    return (
        "По итогам анализа система сформировала сводную оценку финансового состояния "
        f"с итоговой прибылью {_format_money(metrics['total_profit'])} и уровнем риска "
        f"\"{risk_level}\". Рекомендуется использовать прогноз и риск-факторы при "
        "планировании дальнейшей финансовой деятельности."
    )
