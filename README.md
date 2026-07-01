# Stock Market EDA & Volatility Tracker

I built this to get hands-on with financial data analysis — something I hadn't touched before. The idea was simple: take real NSE stock data, run some analysis on it, and make it actually usable through a dashboard rather than just notebooks.

Tracks 5 stocks — TCS, Infosys, Reliance, HDFC Bank, and Wipro — from 2020 to 2024. That range was intentional, COVID crash and recovery makes the data a lot more interesting to analyze.

---

## What it does

The dashboard has 9 tabs:

**Overview** — price trends and cumulative returns for all 5 stocks side by side

**Returns** — daily return distribution per stock, plus a raw returns table for the last 30 days

**Volatility** — rolling 20-day annualized volatility. The COVID spike in mid-2020 is very visible here. Also includes a Risk vs Return scatter plot which I found genuinely useful — shows HDFCBANK is the safest bet but also the lowest return over this period

**Bollinger Bands** — upper and lower bands around the 20-day moving average, per stock. Useful for spotting overbought/oversold zones

**Signals & Correlation** — MA20 vs MA50 crossover signals plotted on the price chart, plus a correlation heatmap. TCS and INFY came out at 0.71 which makes sense given they're both large-cap IT

**Compare Stocks** — pick any two stocks, see them on a normalized chart (both starting at 100 so the comparison is fair), with total return and volatility metrics side by side

- **Investment Simulator** — Enter any amount, pick a stock and start date, see current value + comparison across all stocks
- **Price Race** — Animated bar chart race of all 5 stocks with adjustable speed (0.25x to 4x)
- **MA Crossover Backtest** — Simulates buy/sell signals vs buy & hold, with trade log and signal chart
There's also a sidebar date filter so you can zoom into any time range, and KPI cards at the top showing best/worst performer and volatility rankings for the selected period.

---

## Stack

- Python
- yfinance for data
- Pandas for all the number crunching
- Plotly for charts
- Streamlit for the dashboard

---

## Running it locally

```bash
git clone https://github.com/Samarthsj1013/stock-market-tracker.git
cd stock-market-tracker
pip install -r requirements.txt
python -m streamlit run app.py
```

---

## Project structure

```
stock/
├── app.py
├── data/
│   └── fetch_data.py
├── analysis/
│   ├── returns.py
│   ├── bollinger.py
│   └── signals.py
├── visuals/
│   ├── charts.py
│   └── heatmap.py
└── requirements.txt
```

---

## A few things I noticed in the data

INFY returned ~192% over this period which was surprising — it outperformed TCS by a significant margin. WIPRO had the highest volatility but middling returns, which puts it in a bad spot on the risk-return chart. The correlation heatmap showed IT stocks (TCS, INFY, WIPRO) moving together more than I expected, while HDFC Bank and Reliance were more independent.

The COVID period (roughly March to July 2020) is the most interesting stretch in the data — volatility spiked to over 1.0 annualized for most stocks, which is extreme compared to the 0.2 range they sit at normally.

---

## Live demo

🔗 [Add Streamlit URL here after deployment]

---

Samarth Jayant
samarthsj1013@gmail.com
[LinkedIn](https://linkedin.com/in/samarth-jayant-0a947b35b)