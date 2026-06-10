import numpy as np
import pandas as pd

from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error


def train_forecast_models(monthly):
    monthly = monthly.copy()

    X = monthly[["month_number"]]
    y = monthly["profit"]
    test_size = max(2, int(np.ceil(len(monthly) * 0.25)))
    test_size = min(test_size, len(monthly) - 2)

    if test_size < 1:
        raise ValueError("Для оценки моделей требуется минимум 3 месяца данных.")

    train = monthly.iloc[:-test_size]
    test = monthly.iloc[-test_size:]

    X_train = train[["month_number"]]
    y_train = train["profit"]
    X_test = test[["month_number"]]
    y_test = test["profit"]

    linear_model = LinearRegression()
    linear_model.fit(X_train, y_train)

    forest_model = RandomForestRegressor(
        n_estimators=100,
        random_state=42,
    )
    forest_model.fit(X_train, y_train)

    boosting_model = GradientBoostingRegressor(random_state=42)
    boosting_model.fit(X_train, y_train)

    monthly["sample_type"] = "train"
    monthly.loc[test.index, "sample_type"] = "test"

    monthly["linear_prediction"] = linear_model.predict(X)
    monthly["forest_prediction"] = forest_model.predict(X)
    monthly["boosting_prediction"] = boosting_model.predict(X)

    linear_test_prediction = linear_model.predict(X_test)
    forest_test_prediction = forest_model.predict(X_test)
    boosting_test_prediction = boosting_model.predict(X_test)

    models_results = {
        "Linear Regression": {
            "model": linear_model,
            "mae": mean_absolute_error(y_test, linear_test_prediction),
            "rmse": np.sqrt(mean_squared_error(y_test, linear_test_prediction)),
        },
        "Random Forest": {
            "model": forest_model,
            "mae": mean_absolute_error(y_test, forest_test_prediction),
            "rmse": np.sqrt(mean_squared_error(y_test, forest_test_prediction)),
        },
        "Gradient Boosting": {
            "model": boosting_model,
            "mae": mean_absolute_error(y_test, boosting_test_prediction),
            "rmse": np.sqrt(mean_squared_error(y_test, boosting_test_prediction)),
        },
    }

    best_model_name = min(models_results, key=lambda name: models_results[name]["mae"])
    best_model = models_results[best_model_name]["model"]
    long_term_model = LinearRegression()
    long_term_model.fit(X, y)

    return monthly, models_results, best_model_name, best_model, long_term_model


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
