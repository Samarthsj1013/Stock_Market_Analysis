import yfinance as yf
import pandas as pd
from data.nifty50 import get_tickers

START_DATE = "2020-01-01"
END_DATE = "2024-12-31"

def fetch_stock_data(tickers=None, start=START_DATE, end=END_DATE):
    if tickers is None:
        tickers = get_tickers()
    raw = yf.download(tickers, start=start, end=end,
                      auto_adjust=True, progress=False)
    if isinstance(raw.columns, pd.MultiIndex):
        close = raw["Close"]
    else:
        close = raw[["Close"]]
    if isinstance(close.columns, pd.MultiIndex):
        close.columns = close.columns.get_level_values(0)
    close.dropna(how="all", inplace=True)
    return close

def fetch_single_stock(ticker: str, start=START_DATE, end=END_DATE):
    df = yf.download(ticker, start=start, end=end,
                     auto_adjust=True, progress=False)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df.dropna(inplace=True)
    return df

def fetch_realtime_price(ticker: str):
    try:
        stock = yf.Ticker(ticker)
        info = stock.fast_info
        return {
            "price": round(info.last_price, 2),
            "change": round(info.last_price - info.previous_close, 2),
            "change_pct": round(((info.last_price - info.previous_close) / info.previous_close) * 100, 2),
            "volume": info.three_month_average_volume,
            "high": round(info.year_high, 2),
            "low": round(info.year_low, 2),
        }
    except Exception as e:
        return {"price": None, "change": None, "change_pct": None,
                "volume": None, "high": None, "low": None}

def fetch_news(ticker: str):
    try:
        stock = yf.Ticker(ticker)
        news = stock.news[:5]
        return [{"title": n.get("title", ""),
                 "link": n.get("link", ""),
                 "publisher": n.get("publisher", ""),
                 "time": pd.to_datetime(n.get("providerPublishTime", 0), unit="s").strftime("%d %b %Y")}
                for n in news]
    except:
        return []