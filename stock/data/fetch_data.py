import yfinance as yf
import pandas as pd

TICKERS = ["TCS.NS", "INFY.NS", "RELIANCE.NS", "HDFCBANK.NS", "WIPRO.NS"]
START_DATE = "2020-01-01"
END_DATE = "2024-12-31"

def fetch_stock_data():
    raw = yf.download(TICKERS, start=START_DATE, end=END_DATE, auto_adjust=True, progress=False)
    
    # Handle MultiIndex columns from newer yfinance versions
    if isinstance(raw.columns, pd.MultiIndex):
        close = raw["Close"]
    else:
        close = raw[["Close"]]
    
    # Flatten column names if needed
    if isinstance(close.columns, pd.MultiIndex):
        close.columns = close.columns.get_level_values(0)
    
    close.dropna(how="all", inplace=True)
    return close

def fetch_single_stock(ticker: str):
    df = yf.download(ticker, start=START_DATE, end=END_DATE, auto_adjust=True, progress=False)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df.dropna(inplace=True)
    return df