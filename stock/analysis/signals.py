import pandas as pd

def compute_ma_signals(series: pd.Series) -> pd.DataFrame:
    df = pd.DataFrame({"Price": series})
    df["MA20"] = series.rolling(20).mean()
    df["MA50"] = series.rolling(50).mean()

    df["Signal"] = 0
    df.loc[df["MA20"] > df["MA50"], "Signal"] = 1   # Buy
    df.loc[df["MA20"] < df["MA50"], "Signal"] = -1  # Sell

    df["Position"] = df["Signal"].diff()  # Actual crossover points
    df.dropna(inplace=True)
    return df