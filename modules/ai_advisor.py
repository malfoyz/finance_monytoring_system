import os

from dotenv import load_dotenv
from openai import APIConnectionError, AuthenticationError, OpenAI, OpenAIError, RateLimitError


load_dotenv()


class AIAdvisorConfigError(Exception):
    """Raised when the external AI API is not configured for the app."""


def build_ai_prompt(
    total_income,
    total_expense,
    total_profit,
    profitability,
    average_profit,
    predicted_average_profit,
    best_model_name,
    best_model_mae,
    best_model_rmse,
    risk_level,
):
    return f"""
Ты выступаешь в роли финансового аналитика информационной системы мониторинга показателей эффективности предприятия.

Проанализируй финансовое состояние предприятия на основе следующих данных:

Общая сумма доходов: {total_income:,.0f} рублей.
Общая сумма расходов: {total_expense:,.0f} рублей.
Итоговая прибыль: {total_profit:,.0f} рублей.
Рентабельность: {profitability:.2%}.
Средняя прибыль за период: {average_profit:,.0f} рублей.
Прогнозная средняя прибыль на следующие периоды: {predicted_average_profit:,.0f} рублей.
Лучшая модель прогнозирования: {best_model_name}.
MAE лучшей модели: {best_model_mae:,.0f}.
RMSE лучшей модели: {best_model_rmse:,.0f}.
Уровень риска по расчетным правилам: {risk_level}.

Сформируй структурированное заключение:
1. Общая оценка финансового состояния.
2. Основные положительные факторы.
3. Основные риски.
4. Рекомендации для руководства.
5. Краткий итог.
"""


def generate_ai_conclusion(prompt):
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise AIAdvisorConfigError("Переменная OPENAI_API_KEY не задана в .env.")

    client = OpenAI(api_key=api_key)

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt,
    )

    return response.output_text


def format_ai_error(error):
    if isinstance(error, AIAdvisorConfigError):
        return str(error)

    if isinstance(error, AuthenticationError):
        return "Ключ OpenAI API недействителен или не имеет доступа к API."

    if isinstance(error, RateLimitError):
        if getattr(error, "code", None) == "insufficient_quota":
            return (
                "Квота OpenAI API исчерпана. Проверьте баланс, лимиты и billing "
                "для проекта, к которому относится OPENAI_API_KEY."
            )

        return "Превышен лимит запросов к OpenAI API. Повторите попытку позже."

    if isinstance(error, APIConnectionError):
        return "Не удалось подключиться к OpenAI API. Проверьте интернет-соединение."

    if isinstance(error, OpenAIError):
        return "OpenAI API вернул ошибку. Проверьте настройки ключа, проекта и модели."

    return "Не удалось сформировать заключение через внешний AI API."
