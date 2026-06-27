import pandas as pd

def compute_bollinger_bands(series: pd.Series, window: int = 20) -> pd.DataFrame:
    rolling_mean = series.rolling(window).mean()
    rolling_std = series.rolling(window).std()

    upper = rolling_mean + (2 * rolling_std)
    lower = rolling_mean - (2 * rolling_std)

    return pd.DataFrame({
        "Price": series,
        "MA20": rolling_mean,
        "Upper Band": upper,
        "Lower Band": lower
    }).dropna()