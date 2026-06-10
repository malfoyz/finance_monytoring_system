import os
import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from dotenv import load_dotenv


load_dotenv()


class AIAdvisorConfigError(Exception):
    """Raised when the external AI API is not configured for the app."""


class AIAdvisorAPIError(Exception):
    """Raised when the external AI API returns an error."""

    def __init__(self, message, status_code=None):
        super().__init__(message)
        self.status_code = status_code


def build_ai_prompt(
    total_income,
    total_expense,
    total_profit,
    profitability,
    average_profit,
    predicted_average_profit,
    best_model_name,
    forecast_model_name,
    best_model_mae,
    best_model_rmse,
    risk_level,
    expense_growth,
    income_decline,
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
Лучшая модель по тестовой метрике MAE: {best_model_name}.
Модель для долгосрочного прогноза: {forecast_model_name}.
MAE лучшей модели: {best_model_mae:,.0f}.
RMSE лучшей модели: {best_model_rmse:,.0f}.
Уровень риска по расчетным правилам: {risk_level}.
Сценарий анализа: рост расходов {expense_growth}%, снижение доходов {income_decline}%.

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
        raise AIAdvisorConfigError(
            "Переменная OPENAI_API_KEY не задана в .env."
        )

    model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
    url = "https://api.openai.com/v1/responses"
    payload = {
        "model": model,
        "input": prompt,
    }
    request = Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )

    try:
        with urlopen(request, timeout=60) as response:
            response_data = json.loads(response.read().decode("utf-8"))
    except HTTPError as error:
        error_message = _extract_openai_error(error)
        raise AIAdvisorAPIError(error_message, error.code) from error
    except URLError as error:
        raise AIAdvisorAPIError("Не удалось подключиться к OpenAI API.") from error

    return _extract_openai_text(response_data)


def format_ai_error(error):
    if isinstance(error, AIAdvisorConfigError):
        return str(error)

    if isinstance(error, AIAdvisorAPIError):
        if error.status_code in {401, 403}:
            return (
                "Ключ OpenAI API недействителен или не имеет доступа к выбранной модели."
            )

        if error.status_code == 429:
            return "Превышен лимит запросов OpenAI API. Повторите попытку позже."

        return str(error)

    return "Не удалось сформировать заключение через OpenAI API."


def _extract_openai_error(error):
    try:
        data = json.loads(error.read().decode("utf-8"))
        return data.get("error", {}).get("message") or "OpenAI API вернул ошибку."
    except (json.JSONDecodeError, UnicodeDecodeError):
        return "OpenAI API вернул ошибку."


def _extract_openai_text(response_data):
    output_text = response_data.get("output_text")

    if isinstance(output_text, str) and output_text.strip():
        return output_text.strip()

    try:
        output_items = response_data["output"]
    except KeyError:
        raise AIAdvisorAPIError("OpenAI API вернул ответ без текста.")

    text_parts = []
    for item in output_items:
        for content in item.get("content", []):
            if content.get("type") in {"output_text", "text"}:
                text_parts.append(content.get("text", ""))

    text = "\n".join(text_parts).strip()

    if not text:
        raise AIAdvisorAPIError("OpenAI API вернул пустой ответ.")

    return text
