def calculate_financial_metrics(monthly):
    total_income = monthly["income"].sum()
    total_expense = monthly["expense"].sum()
    total_profit = monthly["profit"].sum()
    profitability = total_profit / total_income if total_income else 0
    average_profit = monthly["profit"].mean()
    min_monthly_profit = monthly["profit"].min()

    return {
        "total_income": total_income,
        "total_expense": total_expense,
        "total_profit": total_profit,
        "profitability": profitability,
        "average_profit": average_profit,
        "min_monthly_profit": min_monthly_profit,
    }


def apply_scenario(monthly, expense_growth, income_decline):
    scenario = monthly.copy()
    scenario["income"] = scenario["income"] * (1 - income_decline / 100)
    scenario["expense"] = scenario["expense"] * (1 + expense_growth / 100)
    scenario["profit"] = scenario["income"] - scenario["expense"]

    return scenario


def assess_risk(
    total_income,
    total_expense,
    total_profit,
    profitability,
    average_profit,
    predicted_average_profit,
    min_monthly_profit,
):
    expense_ratio = total_expense / total_income if total_income else 0

    risk_factors = [
        {
            "condition": "есть убыточный месяц или итоговая прибыль < 0",
            "points": 30,
            "triggered": total_profit < 0 or min_monthly_profit < 0,
            "message": "зафиксирована отрицательная прибыль",
        },
        {
            "condition": "прогноз ниже текущей прибыли",
            "points": 20,
            "triggered": predicted_average_profit < average_profit,
            "message": "прогнозируется снижение средней прибыли",
        },
        {
            "condition": "рентабельность < 10%",
            "points": 20,
            "triggered": profitability < 0.1,
            "message": "рентабельность ниже 10%",
        },
        {
            "condition": "рентабельность 10-20%",
            "points": 10,
            "triggered": 0.1 <= profitability < 0.2,
            "message": "рентабельность находится в зоне внимания",
        },
        {
            "condition": "расходы > 90% доходов",
            "points": 30,
            "triggered": expense_ratio > 0.9,
            "message": "расходы превышают 90% доходов",
        },
        {
            "condition": "расходы 80-90% доходов",
            "points": 20,
            "triggered": 0.8 < expense_ratio <= 0.9,
            "message": "расходы превышают 80% доходов",
        },
        {
            "condition": "расходы 70-80% доходов",
            "points": 10,
            "triggered": 0.7 < expense_ratio <= 0.8,
            "message": "расходы превышают 70% доходов",
        },
    ]

    risk_score = sum(factor["points"] for factor in risk_factors if factor["triggered"])
    risk_score = min(risk_score, 100)
    risk_messages = [
        factor["message"] for factor in risk_factors if factor["triggered"]
    ]

    if risk_score <= 30:
        risk_level = "низкий"
    elif risk_score <= 60:
        risk_level = "средний"
    else:
        risk_level = "высокий"

    return risk_level, risk_score, risk_messages, risk_factors


def build_local_conclusion(
    total_income,
    total_expense,
    total_profit,
    average_profit,
    predicted_average_profit,
    best_model_name,
    forecast_model_name,
    risk_level,
    risk_score,
    risk_messages,
):
    conclusion = f"""
По результатам анализа финансовых операций предприятия установлено, что
общая сумма доходов за рассматриваемый период составила {total_income:,.0f} ₽,
общая сумма расходов — {total_expense:,.0f} ₽, итоговая прибыль — {total_profit:,.0f} ₽.

Средняя прибыль за период составляет {average_profit:,.0f} ₽.
Прогнозное среднее значение прибыли на следующие периоды составляет
{predicted_average_profit:,.0f} ₽.

Лучшая модель по тестовой метрике MAE: {best_model_name}.
Для долгосрочного прогноза будущих периодов использована модель {forecast_model_name},
так как она способна экстраполировать линейный тренд.

Уровень финансового риска оценивается как {risk_level}.
Итоговый балл риска: {risk_score}.
"""

    if risk_messages:
        conclusion += "\nВыявленные факторы риска:\n"
        for message in risk_messages:
            conclusion += f"- {message};\n"
    else:
        conclusion += "\nКритических факторов риска по рассчитанным показателям не выявлено.\n"

    conclusion += """
Рекомендуется продолжить мониторинг динамики доходов и расходов,
контролировать изменение прибыли по периодам, а также использовать
результаты прогнозирования при планировании финансовой деятельности предприятия.
"""

    return conclusion
