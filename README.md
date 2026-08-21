# Nifty 50 Market Intelligence Dashboard

Started as a 5-stock EDA project, grew into a full market analytics platform covering the Nifty 50. I built this to go beyond just plotting price charts — it now covers technical analysis, backtesting, portfolio construction, and statistical simulation, the kind of layered analysis a research desk would actually use before making a call.

Search any Nifty 50 stock by name or filter by sector, pick your own basket of stocks, and every tab recalculates live.

🔗 **[Live Demo](#)** ← https://stockmarketanalysis-13.streamlit.app/

---

## Features

**14 tabs, organized from beginner-friendly to advanced:**

- **Overview** — price trends, cumulative returns, 52-week high/low tracker
- **Sectors** — average return and risk by sector (IT, Banking, Pharma, Auto, FMCG, Energy, and more)
- **Returns** — daily return distribution, raw returns table, CSV export
- **Volatility** — rolling 20-day annualized volatility, Risk vs Return scatter, Sharpe Ratio comparison
- **Bollinger Bands** — overbought/oversold zones per stock
- **Signals & Correlation** — MA20/MA50 crossover signals, correlation heatmap
- **Compare Stocks** — normalized head-to-head comparison
- **Investment Simulator** — enter any ₹ amount and date, see current value across all selected stocks
- **Price Race** — animated bar chart race with adjustable speed
- **Backtest** — MA crossover strategy vs buy-and-hold, with trade log
- **SIP Simulator** — monthly SIP vs lump sum comparison, annualized return
- **News Feed** — live headlines per stock
- **Portfolio Builder** — custom-weighted multi-stock portfolio vs equal-weight benchmark, contribution breakdown
- **Monte Carlo Simulation** — thousands of simulated future price paths using Geometric Brownian Motion, with percentile bands and outcome distribution

Includes a built-in beginner's guide and plain-English explainers under every advanced metric (Sharpe Ratio, Bollinger Bands, Monte Carlo, etc.) for anyone new to financial analysis.

---

## Tech Stack

| Tool | Purpose |
|------|---------|
| Python | Core language |
| Streamlit | Dashboard framework and deployment |
| yfinance | Live NSE stock data, real-time prices, news |
| Pandas | Data manipulation and analysis |
| NumPy | Monte Carlo simulation (Geometric Brownian Motion) |
| Plotly | All interactive charts, animations, and fan charts |

---

## Running Locally

```bash
git clone https://github.com/Samarthsj1013/Stock_Market_Analysis.git
cd Stock_Market_Analysis/stock
pip install -r requirements.txt
python -m streamlit run app.py
```

---

## Project Structure

```
Stock_Market_Analysis/
├── README.md
└── stock/
    ├── app.py                  # Main dashboard (14 tabs)
    ├── requirements.txt
    ├── data/
    │   ├── fetch_data.py       # Price, live price, and news fetching
    │   └── nifty50.py          # Nifty 50 stock list with sectors, search
    ├── analysis/
    │   ├── returns.py          # Returns, volatility, cumulative returns
    │   ├── bollinger.py        # Bollinger Bands
    │   └── signals.py          # MA crossover signals
    └── visuals/
        ├── charts.py           # Plotly chart functions
        └── heatmap.py          # Correlation heatmap
```

---

## Notable technical decisions

- Switched from a fixed 5-stock list to the full Nifty 50 with sector tagging and name-based search
- Guarded every `dropna()` call after finding that a single bad ticker or missing day could silently wipe out the entire dataset (`dropna(how="any")` vs `dropna(how="all")` matters a lot when working with multi-stock time series)
- Monte Carlo simulation uses log returns and Geometric Brownian Motion — the same underlying model used in options pricing — rather than naive linear extrapolation
- All analysis is stock-agnostic: pick any combination of Nifty 50 stocks and every tab recalculates against that selection and date range

---

## Key Insights from the Data

- Backtesting shows buy-and-hold beats the MA crossover strategy for most stocks over 2020–2024 — trend-following works better in strongly directional markets, and this period had a lot of sideways movement
- IT stocks (TCS, INFY, WIPRO) are highly correlated with each other, while Banking, Pharma, and Auto sectors move more independently
- The COVID period (March–July 2020) shows annualized volatility spiking well above the normal range across almost every stock

---

## Author

**Samarth Jayant**
B.E. Information Science & Engineering — Global Academy of Technology, Bangalore
samarthsj1013@gmail.com | [LinkedIn](https://linkedin.com/in/samarth-jayant-0a947b35b) | [GitHub](https://github.com/Samarthsj1013)