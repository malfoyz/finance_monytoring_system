import numpy as np
import pandas as pd


def load_operations(uploaded_file, default_path="data/operations.csv"):
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_csv(default_path)

    df["date"] = pd.to_datetime(df["date"])
    return df


def prepare_monthly_summary(df):
    df = df.copy()
    df["month"] = df["date"].dt.to_period("M").astype(str)

    monthly = df.pivot_table(
        index="month",
        columns="operation_type",
        values="amount",
        aggfunc="sum",
        fill_value=0,
    ).reset_index()

    if "income" not in monthly.columns:
        monthly["income"] = 0

    if "expense" not in monthly.columns:
        monthly["expense"] = 0

    monthly["profit"] = monthly["income"] - monthly["expense"]
    monthly["month_number"] = np.arange(1, len(monthly) + 1)

    return monthly
