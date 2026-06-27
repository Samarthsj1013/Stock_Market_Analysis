import pandas as pd

def compute_daily_returns(close_df: pd.DataFrame) -> pd.DataFrame:
    return close_df.pct_change(fill_method=None).dropna()

def compute_rolling_volatility(close_df: pd.DataFrame, window: int = 20) -> pd.DataFrame:
    daily_returns = compute_daily_returns(close_df)
    return daily_returns.rolling(window).std() * (252 ** 0.5)

def compute_cumulative_returns(close_df: pd.DataFrame) -> pd.DataFrame:
    daily_returns = compute_daily_returns(close_df)
    return (1 + daily_returns).cumprod() - 1