import matplotlib.pyplot as plt


FIGURE_SIZE = (10.5, 4.2)
FIGURE_DPI = 110


def _style_chart(ax):
    ax.grid(True, axis="y", alpha=0.22)
    ax.tick_params(axis="both", labelsize=9)
    ax.xaxis.label.set_size(10)
    ax.yaxis.label.set_size(10)
    ax.legend(fontsize=9, frameon=True)


def build_dynamics_chart(monthly):
    fig, ax = plt.subplots(figsize=FIGURE_SIZE, dpi=FIGURE_DPI)

    ax.plot(
        monthly["month"],
        monthly["income"],
        marker="o",
        linewidth=1.8,
        markersize=5,
        label="Доходы",
    )
    ax.plot(
        monthly["month"],
        monthly["expense"],
        marker="o",
        linewidth=1.8,
        markersize=5,
        label="Расходы",
    )
    ax.plot(
        monthly["month"],
        monthly["profit"],
        marker="o",
        linewidth=1.8,
        markersize=5,
        label="Прибыль",
    )

    ax.set_xlabel("Месяц")
    ax.set_ylabel("Сумма, ₽")
    _style_chart(ax)
    ax.tick_params(axis="x", labelrotation=35)
    fig.tight_layout()

    return fig


def build_forecast_chart(monthly, future):
    fig, ax = plt.subplots(figsize=FIGURE_SIZE, dpi=FIGURE_DPI)

    ax.plot(
        monthly["month_number"],
        monthly["profit"],
        marker="o",
        linewidth=1.8,
        markersize=5,
        label="Фактическая прибыль",
    )

    ax.plot(
        future["month_number"],
        future["predicted_profit"],
        marker="o",
        linestyle="--",
        linewidth=1.8,
        markersize=5,
        label="Прогноз прибыли",
    )

    ax.set_xlabel("Номер месяца")
    ax.set_ylabel("Прибыль, ₽")
    _style_chart(ax)
    fig.tight_layout()

    return fig
