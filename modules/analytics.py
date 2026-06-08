def calculate_financial_metrics(monthly):
    total_income = monthly["income"].sum()
    total_expense = monthly["expense"].sum()
    total_profit = monthly["profit"].sum()
    profitability = total_profit / total_income if total_income else 0
    average_profit = monthly["profit"].mean()

    return {
        "total_income": total_income,
        "total_expense": total_expense,
        "total_profit": total_profit,
        "profitability": profitability,
        "average_profit": average_profit,
    }


def assess_risk(monthly, total_profit, average_profit, predicted_average_profit):
    risk_messages = []

    if total_profit <= 0:
        risk_messages.append("общая прибыль за период отрицательная")

    if predicted_average_profit < average_profit:
        risk_messages.append("прогнозируется снижение средней прибыли")

    average_income = monthly["income"].mean()
    expense_share = monthly["expense"].mean() / average_income if average_income else 0

    if expense_share > 0.8:
        risk_messages.append("расходы занимают высокую долю в структуре доходов")

    risk_level = "низкий" if len(risk_messages) == 0 else "повышенный"

    return risk_level, risk_messages


def build_local_conclusion(
    total_income,
    total_expense,
    total_profit,
    average_profit,
    predicted_average_profit,
    best_model_name,
    risk_level,
    risk_messages,
):
    conclusion = f"""
По результатам анализа финансовых операций предприятия установлено, что
общая сумма доходов за рассматриваемый период составила {total_income:,.0f} ₽,
общая сумма расходов — {total_expense:,.0f} ₽, итоговая прибыль — {total_profit:,.0f} ₽.

Средняя прибыль за период составляет {average_profit:,.0f} ₽.
Прогнозное среднее значение прибыли на следующие периоды составляет
{predicted_average_profit:,.0f} ₽.

Для прогнозирования использована модель {best_model_name}, выбранная на
основании значения метрики MAE.

Уровень финансового риска оценивается как {risk_level}.
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
