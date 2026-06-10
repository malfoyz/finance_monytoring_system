import streamlit as st

from modules.ai_advisor import build_ai_prompt, format_ai_error, generate_ai_conclusion
from modules.analytics import (
    apply_scenario,
    assess_risk,
    build_local_conclusion,
    calculate_financial_metrics,
)
from modules.charts import build_dynamics_chart, build_forecast_chart
from modules.data_loader import load_operations, prepare_monthly_summary
from modules.forecasting import build_future_forecast, train_forecast_models


st.set_page_config(
    page_title="Мониторинг финансовых показателей",
    layout="wide",
)

st.title("Информационная система мониторинга финансово-экономических показателей")
st.write(
    "Система выполняет загрузку финансовых операций, расчет показателей, "
    "прогнозирование прибыли и формирование аналитического заключения."
)


# ---------- Загрузка данных ----------

uploaded_file = st.sidebar.file_uploader(
    "Загрузите CSV-файл с операциями",
    type=["csv"],
)

df = load_operations(uploaded_file)

st.subheader("Исходные финансовые операции")
st.dataframe(df, width="stretch")


# ---------- Подготовка данных ----------

monthly = prepare_monthly_summary(df)


# ---------- Сценарный анализ ----------

st.subheader("Сценарный анализ")

scenario_col1, scenario_col2 = st.columns(2)

expense_growth = scenario_col1.slider(
    "Рост расходов (%)",
    min_value=0,
    max_value=50,
    value=10,
)

income_decline = scenario_col2.slider(
    "Снижение доходов (%)",
    min_value=0,
    max_value=50,
    value=0,
)

analysis_monthly = apply_scenario(
    monthly,
    expense_growth=expense_growth,
    income_decline=income_decline,
)

metrics = calculate_financial_metrics(analysis_monthly)

total_income = metrics["total_income"]
total_expense = metrics["total_expense"]
total_profit = metrics["total_profit"]
profitability = metrics["profitability"]
average_profit = metrics["average_profit"]
min_monthly_profit = metrics["min_monthly_profit"]


# ---------- Основные показатели ----------

col1, col2, col3, col4 = st.columns(4)

col1.metric("Доходы", f"{total_income:,.0f} ₽")
col2.metric("Расходы", f"{total_expense:,.0f} ₽")
col3.metric("Прибыль", f"{total_profit:,.0f} ₽")
col4.metric("Рентабельность", f"{profitability:.2%}")


# ---------- Таблица по месяцам ----------

st.subheader("Свод по месяцам")
st.dataframe(
    analysis_monthly[["month", "income", "expense", "profit"]],
    width="stretch",
)


# ---------- График динамики ----------

st.subheader("Динамика доходов, расходов и прибыли")
st.pyplot(build_dynamics_chart(analysis_monthly))


# ---------- Прогнозирование ----------

st.subheader("Прогнозирование прибыли")

try:
    (
        forecast_monthly,
        models_results,
        best_model_name,
        best_model,
        long_term_model,
    ) = train_forecast_models(analysis_monthly)
except ValueError as error:
    st.error(str(error))
    st.stop()

forecast_model_name = "Linear Regression"

train_months_count = (forecast_monthly["sample_type"] == "train").sum()
test_months_count = (forecast_monthly["sample_type"] == "test").sum()

st.caption(
    f"Оценка моделей выполнена на временном разбиении без перемешивания: "
    f"{train_months_count} мес. train и {test_months_count} мес. test."
)

metric_col1, metric_col2, metric_col3 = st.columns(3)

metric_col1.metric("MAE Linear Regression", f"{models_results['Linear Regression']['mae']:,.0f}")
metric_col1.metric("RMSE Linear Regression", f"{models_results['Linear Regression']['rmse']:,.0f}")

metric_col2.metric("MAE Random Forest", f"{models_results['Random Forest']['mae']:,.0f}")
metric_col2.metric("RMSE Random Forest", f"{models_results['Random Forest']['rmse']:,.0f}")

metric_col3.metric("MAE Gradient Boosting", f"{models_results['Gradient Boosting']['mae']:,.0f}")
metric_col3.metric("RMSE Gradient Boosting", f"{models_results['Gradient Boosting']['rmse']:,.0f}")

future_months_count = st.slider(
    "Количество месяцев для прогноза",
    min_value=1,
    max_value=6,
    value=3,
)

future = build_future_forecast(forecast_monthly, long_term_model, future_months_count)
predicted_average_profit = future["predicted_profit"].mean()

st.write(f"Лучшая модель по тестовой MAE: **{best_model_name}**")
st.write(f"Модель для долгосрочного прогноза: **{forecast_model_name}**")

st.subheader("Прогноз прибыли на следующие периоды")
st.dataframe(future, width="stretch")


# ---------- График прогноза ----------

st.pyplot(build_forecast_chart(forecast_monthly, future))


# ---------- AI / экспертное заключение ----------

risk_level, risk_score, risk_messages, risk_factors = assess_risk(
    total_income,
    total_expense,
    total_profit,
    profitability,
    average_profit,
    predicted_average_profit,
    min_monthly_profit,
)

st.subheader("Оценка риска предприятия")

risk_col1, risk_col2 = st.columns(2)
risk_col1.metric("Итоговый балл риска", f"{risk_score} из 100")
risk_col2.metric("Уровень риска", risk_level.capitalize())

risk_table = [
    {
        "Условие": factor["condition"],
        "Баллы": factor["points"],
        "Выполнено": "Да" if factor["triggered"] else "Нет",
        "Начислено": factor["points"] if factor["triggered"] else 0,
    }
    for factor in risk_factors
]

st.dataframe(risk_table, width="stretch", hide_index=True)

st.caption("0-30 — низкий риск; 31-60 — средний риск; 61-100 — высокий риск.")

conclusion = build_local_conclusion(
    total_income=total_income,
    total_expense=total_expense,
    total_profit=total_profit,
    average_profit=average_profit,
    predicted_average_profit=predicted_average_profit,
    best_model_name=best_model_name,
    forecast_model_name=forecast_model_name,
    risk_level=risk_level,
    risk_score=risk_score,
    risk_messages=risk_messages,
)

st.subheader("AI-интерпретация финансового состояния")

use_ai = st.checkbox("Сформировать заключение с помощью OpenAI API", value=True)

best_model_result = models_results[best_model_name]
prompt = build_ai_prompt(
    total_income=total_income,
    total_expense=total_expense,
    total_profit=total_profit,
    profitability=profitability,
    average_profit=average_profit,
    predicted_average_profit=predicted_average_profit,
    best_model_name=best_model_name,
    forecast_model_name=forecast_model_name,
    best_model_mae=best_model_result["mae"],
    best_model_rmse=best_model_result["rmse"],
    risk_level=risk_level,
    expense_growth=expense_growth,
    income_decline=income_decline,
)

if use_ai:
    try:
        ai_conclusion = generate_ai_conclusion(prompt)
        st.success(ai_conclusion)

    except Exception as error:
        st.warning("Не удалось получить ответ от OpenAI API. Показано локальное заключение.")
        st.error(format_ai_error(error))
        st.info(conclusion)
else:
    st.info(conclusion)
