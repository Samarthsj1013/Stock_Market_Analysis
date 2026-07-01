import streamlit as st
import pandas as pd
from data.fetch_data import fetch_stock_data
from analysis.returns import compute_daily_returns, compute_rolling_volatility, compute_cumulative_returns
from analysis.bollinger import compute_bollinger_bands
from analysis.signals import compute_ma_signals
from visuals.charts import (
    plot_price_trends,
    plot_cumulative_returns,
    plot_daily_returns_distribution,
    plot_rolling_volatility,
    plot_bollinger_bands,
    plot_ma_signals
)
from visuals.heatmap import plot_correlation_heatmap
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Stock Market Tracker", layout="wide", page_icon="📈")

TICKERS = ["TCS.NS", "INFY.NS", "RELIANCE.NS", "HDFCBANK.NS", "WIPRO.NS"]
TICKER_LABELS = {t: t.replace(".NS", "") for t in TICKERS}

st.title("📈 Stock Market EDA & Volatility Tracker")
st.caption("NSE Stocks | Built with Python, yfinance & Streamlit")

# ── Sidebar: Date Range Filter ──────────────────────────────────────────────
st.sidebar.header("⚙️ Filters")
start_date = st.sidebar.date_input("Start Date", value=pd.to_datetime("2020-01-01"))
end_date = st.sidebar.date_input("End Date", value=pd.to_datetime("2024-12-31"))

if start_date >= end_date:
    st.sidebar.error("Start date must be before end date.")
    st.stop()

# ── Load Data ────────────────────────────────────────────────────────────────
@st.cache_data(show_spinner="Fetching stock data...")
def load_data(start, end):
    import yfinance as yf
    import pandas as pd
    raw = yf.download(TICKERS, start=start, end=end, auto_adjust=True, progress=False)
    if isinstance(raw.columns, pd.MultiIndex):
        close = raw["Close"]
    else:
        close = raw[["Close"]]
    if isinstance(close.columns, pd.MultiIndex):
        close.columns = close.columns.get_level_values(0)
    close.dropna(how="all", inplace=True)
    return close

close_df = load_data(str(start_date), str(end_date))
daily_returns = compute_daily_returns(close_df)
volatility_df = compute_rolling_volatility(close_df)
cum_returns = compute_cumulative_returns(close_df)

# ── KPI Cards ────────────────────────────────────────────────────────────────
st.subheader("📌 Portfolio Snapshot")

col1, col2, col3, col4 = st.columns(4)

if not close_df.empty and len(close_df) > 1:
    total_returns = (close_df.iloc[-1] / close_df.iloc[0] - 1) * 100
    total_returns = total_returns.dropna()
    avg_vol = volatility_df.mean().dropna()

    if not total_returns.empty:
        best_stock = total_returns.idxmax().replace(".NS", "")
        worst_stock = total_returns.idxmin().replace(".NS", "")
        col1.metric("🏆 Best Performer", best_stock, f"+{total_returns.max():.1f}%")
        col2.metric("📉 Worst Performer", worst_stock, f"{total_returns.min():.1f}%")
    else:
        col1.metric("🏆 Best Performer", "N/A", "")
        col2.metric("📉 Worst Performer", "N/A", "")

    if not avg_vol.empty:
        most_volatile = avg_vol.idxmax().replace(".NS", "")
        least_volatile = avg_vol.idxmin().replace(".NS", "")
        col3.metric("🌊 Most Volatile", most_volatile, f"{avg_vol.max():.2f}")
        col4.metric("🛡️ Least Volatile", least_volatile, f"{avg_vol.min():.2f}")
    else:
        col3.metric("🌊 Most Volatile", "N/A", "")
        col4.metric("🛡️ Least Volatile", "N/A", "")
else:
    col1.metric("🏆 Best Performer", "N/A", "")
    col2.metric("📉 Worst Performer", "N/A", "")
    col3.metric("🌊 Most Volatile", "N/A", "")
    col4.metric("🛡️ Least Volatile", "N/A", "")

st.divider()

# ── Tabs ─────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 Overview",
    "📉 Returns",
    "🌊 Volatility",
    "📐 Bollinger Bands",
    "🔀 Signals & Correlation",
    "⚖️ Compare Stocks"
])

# ── Tab 1: Overview ───────────────────────────────────────────────────────────
with tab1:
    st.subheader("Price Trends")
    st.plotly_chart(plot_price_trends(close_df), use_container_width=True)
    st.subheader("Cumulative Returns")
    st.plotly_chart(plot_cumulative_returns(cum_returns), use_container_width=True)

# ── Tab 2: Returns ────────────────────────────────────────────────────────────
with tab2:
    st.subheader("Daily Return Distribution")
    selected = st.selectbox("Select Stock", TICKERS,
                            format_func=lambda x: TICKER_LABELS[x], key="returns")
    st.plotly_chart(plot_daily_returns_distribution(daily_returns, selected),
                    use_container_width=True)
    st.subheader("Raw Daily Returns")
    st.dataframe(daily_returns.tail(30).style.format("{:.4f}"), use_container_width=True)

# ── Tab 3: Volatility ─────────────────────────────────────────────────────────
with tab3:
    st.subheader("Rolling 20-Day Annualized Volatility")
    st.plotly_chart(plot_rolling_volatility(volatility_df), use_container_width=True)

    st.subheader("Latest Volatility Snapshot")
if not volatility_df.empty and len(volatility_df) > 0:
    latest_vol = volatility_df.dropna().iloc[-1].reset_index()
    latest_vol.columns = ["Stock", "Volatility"]
    latest_vol["Stock"] = latest_vol["Stock"].str.replace(".NS", "", regex=False)
    st.dataframe(latest_vol, use_container_width=True)
else:
    st.warning("Volatility data unavailable — try refreshing.")

    # ── Risk vs Return Scatter ──────────────────────────────────────────────
    st.subheader("📍 Risk vs Return")
    avg_annual_return = daily_returns.mean() * 252 * 100
    avg_annual_vol = volatility_df.mean() * 100

    scatter_df = pd.DataFrame({
        "Stock": [t.replace(".NS", "") for t in TICKERS],
        "Avg Annual Return (%)": avg_annual_return.values,
        "Avg Annual Volatility (%)": avg_annual_vol.values
    })

    fig_scatter = px.scatter(
        scatter_df,
        x="Avg Annual Volatility (%)",
        y="Avg Annual Return (%)",
        text="Stock",
        size=[20] * len(scatter_df),
        color="Stock",
        title="Risk vs Return — All Stocks",
        template="plotly_dark"
    )
    fig_scatter.update_traces(textposition="top center", marker=dict(size=18))
    fig_scatter.update_layout(showlegend=False)
    st.plotly_chart(fig_scatter, use_container_width=True)

# ── Tab 4: Bollinger Bands ────────────────────────────────────────────────────
with tab4:
    st.subheader("Bollinger Bands")
    selected_bb = st.selectbox("Select Stock", TICKERS,
                               format_func=lambda x: TICKER_LABELS[x], key="bb")
    bb_df = compute_bollinger_bands(close_df[selected_bb])
    st.plotly_chart(plot_bollinger_bands(bb_df, selected_bb), use_container_width=True)

    with st.expander("What are Bollinger Bands?"):
        st.write("""
        - **MA20** = 20-day moving average
        - **Upper Band** = MA20 + 2× std deviation → potential **sell** zone
        - **Lower Band** = MA20 − 2× std deviation → potential **buy** zone
        - When price touches the lower band, it may indicate oversold conditions.
        """)

# ── Tab 5: Signals & Correlation ──────────────────────────────────────────────
with tab5:
    st.subheader("MA Crossover Buy/Sell Signals")
    selected_sig = st.selectbox("Select Stock", TICKERS,
                                format_func=lambda x: TICKER_LABELS[x], key="sig")
    signal_df = compute_ma_signals(close_df[selected_sig])
    st.plotly_chart(plot_ma_signals(signal_df, selected_sig), use_container_width=True)

    st.subheader("Correlation Heatmap")
    st.plotly_chart(plot_correlation_heatmap(daily_returns), use_container_width=True)

# ── Tab 6: Compare Stocks ─────────────────────────────────────────────────────
with tab6:
    st.subheader("⚖️ Stock Comparison Mode")

    col_a, col_b = st.columns(2)
    stock_a = col_a.selectbox("Stock A", TICKERS,
                               format_func=lambda x: TICKER_LABELS[x],
                               index=0, key="compare_a")
    stock_b = col_b.selectbox("Stock B", TICKERS,
                               format_func=lambda x: TICKER_LABELS[x],
                               index=1, key="compare_b")

    if stock_a == stock_b:
        st.warning("Please select two different stocks.")
    else:
        # Normalized price (both starting at 100)
        norm = close_df[[stock_a, stock_b]].copy()
        norm = (norm / norm.iloc[0]) * 100

        fig_compare = go.Figure()
        fig_compare.add_trace(go.Scatter(
            x=norm.index, y=norm[stock_a],
            name=stock_a.replace(".NS", ""),
            line=dict(color="cyan")
        ))
        fig_compare.add_trace(go.Scatter(
            x=norm.index, y=norm[stock_b],
            name=stock_b.replace(".NS", ""),
            line=dict(color="orange")
        ))
        fig_compare.update_layout(
            title=f"Normalized Price Comparison — {stock_a.replace('.NS','')} vs {stock_b.replace('.NS','')} (Base = 100)",
            xaxis_title="Date",
            yaxis_title="Normalized Price",
            template="plotly_dark",
            hovermode="x unified"
        )
        st.plotly_chart(fig_compare, use_container_width=True)

        # Side by side metrics
        st.subheader("Head-to-Head Metrics")
        r_a = total_returns[stock_a]
        r_b = total_returns[stock_b]
        v_a = avg_vol[stock_a]
        v_b = avg_vol[stock_b]

        m1, m2 = st.columns(2)
        m1.metric(f"{stock_a.replace('.NS','')} Total Return", f"{r_a:.1f}%")
        m2.metric(f"{stock_b.replace('.NS','')} Total Return", f"{r_b:.1f}%",
                  delta=f"{r_b - r_a:.1f}% vs {stock_a.replace('.NS','')}")

        m3, m4 = st.columns(2)
        m3.metric(f"{stock_a.replace('.NS','')} Avg Volatility", f"{v_a:.3f}")
        m4.metric(f"{stock_b.replace('.NS','')} Avg Volatility", f"{v_b:.3f}",
                  delta=f"{v_b - v_a:.3f} vs {stock_a.replace('.NS','')}",
                  delta_color="inverse")