# Stock Market EDA & Volatility Tracker

I built this to get hands-on with real financial data analysis using live NSE stock data. The goal was to go beyond just plotting price charts — I wanted something that actually simulates trading decisions, models risk, and gives usable outputs like rupee-based investment outcomes.

Tracks 5 stocks — TCS, Infosys, Reliance, HDFC Bank, and Wipro — from 2020 to 2024. That date range was intentional; the COVID crash and recovery period makes the volatility analysis genuinely interesting.

🔗 **[Live Demo](#)** ← replace with your Streamlit URL

---

## Features

**10 tabs, each doing something different:**

- **Overview** — price trends for all 5 stocks, cumulative returns, and 52-week high/low tracker
- **Returns** — daily return distribution per stock, raw returns table, CSV download
- **Volatility** — rolling 20-day annualized volatility, Risk vs Return scatter, Sharpe Ratio comparison
- **Bollinger Bands** — MA20 with upper/lower bands per stock for overbought/oversold analysis
- **Signals & Correlation** — MA20 vs MA50 crossover buy/sell signals + correlation heatmap
- **Compare Stocks** — normalized head-to-head comparison with return and volatility metrics
- **Investment Simulator** — enter any ₹ amount and start date, see current value across all stocks
- **Price Race** — animated bar chart race with adjustable speed (0.25x to 4x)
- **Backtest** — MA crossover strategy vs buy-and-hold with trade log and portfolio growth chart
- **SIP Simulator** — monthly SIP simulator with annualized return and SIP vs lump sum comparison

---

## Tech Stack

| Tool | Version | Purpose |
|------|---------|---------|
| Python | 3.12 | Core language |
| Streamlit | Latest | Dashboard framework and deployment |
| yfinance | Latest | Live NSE stock data fetching |
| Pandas | Latest | Data manipulation and analysis |
| Plotly | Latest | Interactive charts and animations |
| Scikit-learn | Latest | Supporting ML utilities |

---

## Running Locally

```bash
# Clone the repo
git clone https://github.com/Samarthsj1013/Stock_Market_Analysis.git

# Navigate to project folder
cd Stock_Market_Analysis/stock

# Install dependencies
pip install -r requirements.txt

# Run the app
python -m streamlit run app.py
```

---

## Project Structure

```
Stock_Market_Analysis/
├── README.md
└── stock/
    ├── app.py                  # Main Streamlit dashboard (10 tabs)
    ├── requirements.txt        # Dependencies
    ├── data/
    │   └── fetch_data.py       # yfinance data fetching
    ├── analysis/
    │   ├── returns.py          # Daily returns, volatility, cumulative returns
    │   ├── bollinger.py        # Bollinger Bands calculation
    │   └── signals.py          # MA crossover signal generation
    └── visuals/
        ├── charts.py           # All Plotly chart functions
        └── heatmap.py          # Correlation heatmap
```

---

## Stocks Tracked

| Ticker | Company |
|--------|---------|
| TCS.NS | Tata Consultancy Services |
| INFY.NS | Infosys |
| RELIANCE.NS | Reliance Industries |
| HDFCBANK.NS | HDFC Bank |
| WIPRO.NS | Wipro |

---

## Key Insights from the Data

- INFY returned ~192% over 2020–2024, the best performer by a significant margin
- WIPRO had the highest volatility but middling returns — worst risk-adjusted performance of the five
- TCS and INFY are highly correlated (0.71) as expected for large-cap IT peers
- COVID period (March–July 2020) shows annualized volatility spiking above 1.0, vs the normal 0.15–0.25 range
- Buy-and-hold beat the MA crossover strategy for most stocks — trend-following works better in strongly directional markets

---

## Author

**Samarth Jayant**
B.E. Information Science & Engineering — Global Academy of Technology, Bangalore
samarthsj1013@gmail.com | [LinkedIn](https://linkedin.com/in/samarth-jayant-0a947b35b) | [GitHub](https://github.com/Samarthsj1013)