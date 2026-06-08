import numpy as np
import pandas as pd

from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error


def train_forecast_models(monthly):
    monthly = monthly.copy()

    X = monthly[["month_number"]]
    y = monthly["profit"]

    linear_model = LinearRegression()
    linear_model.fit(X, y)

    forest_model = RandomForestRegressor(
        n_estimators=100,
        random_state=42,
    )
    forest_model.fit(X, y)

    boosting_model = GradientBoostingRegressor(random_state=42)
    boosting_model.fit(X, y)

    monthly["linear_prediction"] = linear_model.predict(X)
    monthly["forest_prediction"] = forest_model.predict(X)
    monthly["boosting_prediction"] = boosting_model.predict(X)

    linear_mae = mean_absolute_error(y, monthly["linear_prediction"])
    forest_mae = mean_absolute_error(y, monthly["forest_prediction"])
    boosting_mae = mean_absolute_error(y, monthly["boosting_prediction"])

    linear_rmse = np.sqrt(mean_squared_error(y, monthly["linear_prediction"]))
    forest_rmse = np.sqrt(mean_squared_error(y, monthly["forest_prediction"]))
    boosting_rmse = np.sqrt(mean_squared_error(y, monthly["boosting_prediction"]))

    models_results = {
        "Linear Regression": {
            "model": linear_model,
            "mae": linear_mae,
            "rmse": linear_rmse,
        },
        "Random Forest": {
            "model": forest_model,
            "mae": forest_mae,
            "rmse": forest_rmse,
        },
        "Gradient Boosting": {
            "model": boosting_model,
            "mae": boosting_mae,
            "rmse": boosting_rmse,
        },
    }

    best_model_name = min(models_results, key=lambda name: models_results[name]["mae"])
    best_model = models_results[best_model_name]["model"]

    return monthly, models_results, best_model_name, best_model


def build_future_forecast(monthly, model, future_months_count):
    last_month_number = monthly["month_number"].max()

    future = pd.DataFrame({
        "month_number": np.arange(
            last_month_number + 1,
            last_month_number + future_months_count + 1,
        )
    })

    future["predicted_profit"] = model.predict(future[["month_number"]])

    return future
