import matplotlib.pyplot as plt


def build_dynamics_chart(monthly):
    fig, ax = plt.subplots()

    ax.plot(monthly["month"], monthly["income"], marker="o", label="Доходы")
    ax.plot(monthly["month"], monthly["expense"], marker="o", label="Расходы")
    ax.plot(monthly["month"], monthly["profit"], marker="o", label="Прибыль")

    ax.set_xlabel("Месяц")
    ax.set_ylabel("Сумма, ₽")
    ax.legend()
    plt.xticks(rotation=45)

    return fig


def build_forecast_chart(monthly, future):
    fig, ax = plt.subplots()

    ax.plot(
        monthly["month_number"],
        monthly["profit"],
        marker="o",
        label="Фактическая прибыль",
    )

    ax.plot(
        future["month_number"],
        future["predicted_profit"],
        marker="o",
        linestyle="--",
        label="Прогноз прибыли",
    )

    ax.set_xlabel("Номер месяца")
    ax.set_ylabel("Прибыль, ₽")
    ax.legend()

    return fig
