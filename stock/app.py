import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from data.fetch_data import fetch_stock_data, fetch_realtime_price, fetch_news
from data.nifty50 import (NIFTY50_STOCKS, SECTORS, get_tickers,
                           get_ticker_label, get_sector,
                           get_tickers_by_sector, search_stocks)
from analysis.returns import compute_daily_returns, compute_rolling_volatility, compute_cumulative_returns
from analysis.bollinger import compute_bollinger_bands
from analysis.signals import compute_ma_signals
from visuals.charts import (plot_price_trends, plot_cumulative_returns,
                             plot_daily_returns_distribution,
                             plot_rolling_volatility, plot_bollinger_bands,
                             plot_ma_signals)
from visuals.heatmap import plot_correlation_heatmap

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Nifty 50 Market Intelligence",
    layout="wide",
    page_icon="📈",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #0e1117; }
    .stock-header {
        font-size: 28px;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 0;
    }
    .sub-text {
        font-size: 13px;
        color: #8892a4;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.6rem;
        font-weight: 700;
    }
    div[data-testid="stMetricDelta"] {
        font-size: 0.9rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        background-color: #1a1d2e;
        padding: 4px;
        border-radius: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 6px 16px;
        font-size: 13px;
    }
</style>
""", unsafe_allow_html=True)

ALL_TICKERS = get_tickers()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📈 Nifty 50 Dashboard")
    st.markdown("---")

    st.markdown("### 🔍 Search & Select")
    search_query = st.text_input("Search Stock", placeholder="e.g. Infosys, TCS, Reliance")

    selected_sector = "All Sectors"

    if search_query:
        search_results = search_stocks(search_query)
        stock_pool = list(search_results.keys()) if search_results else []
        if not stock_pool:
            st.warning("No stocks found.")
    else:
        st.markdown("### 🏭 Or Filter by Sector")
        selected_sector = st.selectbox("Sector", ["All Sectors"] + SECTORS)
        stock_pool = ALL_TICKERS if selected_sector == "All Sectors" else get_tickers_by_sector(selected_sector)

    selected_tickers = st.multiselect(
        "📊 Select Stocks",
        options=stock_pool,
        default=stock_pool[:5] if not search_query else stock_pool,
        format_func=lambda x: get_ticker_label(x)
    )

    if not selected_tickers:
        st.warning("Please select at least one stock.")
        st.stop()

    st.markdown("---")
    st.markdown("### 📅 Date Range")
    start_date = st.date_input("Start", value=pd.to_datetime("2020-01-01"))
    end_date = st.date_input("End", value=pd.to_datetime("2024-12-31"))

    if start_date >= end_date:
        st.error("Start date must be before end date.")
        st.stop()

    st.markdown("---")
    st.markdown('<p class="sub-text">Data sourced from Yahoo Finance via yfinance. Not financial advice.</p>',
                unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown('<p class="stock-header">📈 Nifty 50 Market Intelligence Dashboard</p>', unsafe_allow_html=True)
scope_label = f"Search: '{search_query}'" if search_query else f"Sector: {selected_sector}"
st.markdown(f'<p class="sub-text">Analyzing {len(selected_tickers)} stocks | {start_date} to {end_date} | {scope_label}</p>', unsafe_allow_html=True)
st.markdown("---")

# ── Beginner Guide ────────────────────────────────────────────────────────────
with st.expander("👋 New here? Click to see how this dashboard works", expanded=False):
    st.markdown("""
    **Quick guide:**

    1. **Sidebar (left)** — pick which stocks you want to analyze, filter by sector or search by name, and set your date range. Everything below updates based on this.
    2. **Start simple** — the **Overview**, **Returns**, and **Volatility** tabs are the easiest to read. Start there.
    3. **Going deeper** — **Bollinger Bands**, **Backtest**, and **Portfolio Builder** use more advanced finance concepts. Each has a "What does this mean?" section if you're unsure.
    4. **Just exploring?** — Try the **Investment Simulator** tab. Enter any amount and see what it would be worth today. It's the most intuitive place to start.

    Nothing here is financial advice — it's historical data analysis for learning purposes.
    """)

# ── Load Data ────────────────────────────────────────────────────────────────
@st.cache_data(show_spinner="Fetching market data...", ttl=300)
def load_data(tickers, start, end):
    return fetch_stock_data(list(tickers), str(start), str(end))

close_df = load_data(tuple(selected_tickers), start_date, end_date)
close_df = close_df[[c for c in selected_tickers if c in close_df.columns]]

if close_df.empty:
    st.error("No data available for selected stocks and date range.")
    st.stop()

daily_returns = compute_daily_returns(close_df)
volatility_df = compute_rolling_volatility(close_df)
cum_returns = compute_cumulative_returns(close_df)

# ── Live Prices ───────────────────────────────────────────────────────────────
st.subheader("⚡ Live Market Prices")

@st.cache_data(ttl=60, show_spinner="Fetching live prices...")
def get_live_prices(tickers):
    return {t: fetch_realtime_price(t) for t in tickers}

live_data = get_live_prices(tuple(selected_tickers[:8]))
cols = st.columns(min(len(selected_tickers[:8]), 4))

for i, ticker in enumerate(selected_tickers[:8]):
    col = cols[i % 4]
    data = live_data.get(ticker, {})
    price = data.get("price")
    change = data.get("change")
    change_pct = data.get("change_pct")
    name = get_ticker_label(ticker)
    sector = get_sector(ticker)
    if price:
        col.metric(
            label=f"{name} — {sector}",
            value=f"₹{price:,.2f}",
            delta=f"{change:+.2f} ({change_pct:+.2f}%)"
        )
    else:
        col.metric(label=name, value="N/A")

if len(selected_tickers) > 8:
    st.caption(f"Showing live prices for first 8 of {len(selected_tickers)} selected stocks.")

st.markdown("---")

# ── Portfolio Snapshot KPIs ───────────────────────────────────────────────────
st.subheader("📌 Portfolio Snapshot")
col1, col2, col3, col4, col5 = st.columns(5)

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

    col5.metric("📊 Avg Return", f"{total_returns.mean():.1f}%")
else:
    for col in [col1, col2, col3, col4, col5]:
        col.metric("N/A", "N/A", "")

st.markdown("---")

# ── Tabs ─────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10, tab11, tab12, tab13 = st.tabs([
    "📊 Overview",
    "🏭 Sectors",
    "📉 Returns",
    "🌊 Volatility",
    "📐 Bollinger Bands",
    "🔀 Signals & Correlation",
    "⚖️ Compare Stocks",
    "💰 Investment Simulator",
    "🎬 Price Race",
    "🧪 Backtest",
    "📅 SIP Simulator",
    "📰 News Feed",
    "🧺 Portfolio Builder"
])

# ── Tab 1: Overview ───────────────────────────────────────────────────────────
with tab1:
    st.subheader("Price Trends")
    st.plotly_chart(plot_price_trends(close_df), use_container_width=True)

    st.subheader("Cumulative Returns")
    st.plotly_chart(plot_cumulative_returns(cum_returns), use_container_width=True)

    st.subheader("📏 52-Week High / Low Tracker")
    week52_data = []
    for ticker in selected_tickers:
        s = close_df[ticker].dropna()
        if len(s) == 0:
            continue
        rolling = s.iloc[-252:] if len(s) >= 252 else s
        high = rolling.max()
        low = rolling.min()
        current = s.iloc[-1]
        position = ((current - low) / (high - low)) * 100 if high != low else 50
        week52_data.append({
            "Stock": ticker.replace(".NS", ""),
            "Current (₹)": round(current, 2),
            "52W High (₹)": round(high, 2),
            "52W Low (₹)": round(low, 2),
            "% From High": round(((current - high) / high) * 100, 2),
            "Position in Range (%)": round(position, 2)
        })
    week52_df = pd.DataFrame(week52_data)
    if not week52_df.empty:
        fig_52 = px.bar(week52_df, x="Stock", y="Position in Range (%)",
                        color="Position in Range (%)", color_continuous_scale="RdYlGn",
                        title="52-Week Range Position (0% = at Low, 100% = at High)",
                        template="plotly_dark", text="Position in Range (%)")
        fig_52.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
        fig_52.update_layout(showlegend=False)
        st.plotly_chart(fig_52, use_container_width=True)
        st.dataframe(week52_df, use_container_width=True)

# ── Tab 2: Sector Breakdown ───────────────────────────────────────────────────
with tab2:
    st.subheader("🏭 Sector-wise Performance")
    sector_data = []
    for ticker in selected_tickers:
        if ticker not in close_df.columns:
            continue
        s = close_df[ticker].dropna()
        if len(s) < 2:
            continue
        ret = ((s.iloc[-1] / s.iloc[0]) - 1) * 100
        vol = daily_returns[ticker].std() * (252 ** 0.5) if ticker in daily_returns.columns else 0
        sector_data.append({
            "Stock": get_ticker_label(ticker),
            "Ticker": ticker.replace(".NS", ""),
            "Sector": get_sector(ticker),
            "Total Return (%)": round(ret, 2),
            "Annualized Volatility": round(vol, 3)
        })
    sector_df = pd.DataFrame(sector_data)
    if not sector_df.empty:
        sector_avg = sector_df.groupby("Sector")["Total Return (%)"].mean().reset_index()
        sector_avg.columns = ["Sector", "Avg Return (%)"]
        sector_avg = sector_avg.sort_values("Avg Return (%)", ascending=False)
        fig_sector = px.bar(sector_avg, x="Sector", y="Avg Return (%)",
                            color="Avg Return (%)", color_continuous_scale="RdYlGn",
                            title="Average Return by Sector",
                            template="plotly_dark", text="Avg Return (%)")
        fig_sector.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
        fig_sector.update_layout(showlegend=False)
        st.plotly_chart(fig_sector, use_container_width=True)

        fig_scatter_sector = px.scatter(sector_df, x="Annualized Volatility",
                                        y="Total Return (%)", color="Sector",
                                        text="Ticker", size=[20]*len(sector_df),
                                        title="Risk vs Return by Sector",
                                        template="plotly_dark")
        fig_scatter_sector.update_traces(textposition="top center", marker=dict(size=14))
        st.plotly_chart(fig_scatter_sector, use_container_width=True)

        st.subheader("Stock-wise Breakdown")
        st.dataframe(sector_df.sort_values("Total Return (%)", ascending=False),
                     use_container_width=True)

# ── Tab 3: Returns ────────────────────────────────────────────────────────────
with tab3:
    st.subheader("Daily Return Distribution")
    selected = st.selectbox("Select Stock", selected_tickers,
                            format_func=lambda x: get_ticker_label(x), key="returns")
    if selected in daily_returns.columns:
        st.plotly_chart(plot_daily_returns_distribution(daily_returns, selected),
                        use_container_width=True)
    st.subheader("Raw Daily Returns (Last 30 Days)")
    st.dataframe(daily_returns.tail(30).style.format("{:.4f}"), use_container_width=True)
    csv = daily_returns.tail(30).to_csv().encode("utf-8")
    st.download_button("📥 Download Returns CSV", csv, "daily_returns.csv", "text/csv")

# ── Tab 4: Volatility ─────────────────────────────────────────────────────────
with tab4:
    st.subheader("Rolling 20-Day Annualized Volatility")
    st.plotly_chart(plot_rolling_volatility(volatility_df), use_container_width=True)

    st.subheader("Latest Volatility Snapshot")
vol_clean = volatility_df.dropna(how="all")
if not vol_clean.empty:
    latest_vol = vol_clean.iloc[-1].dropna().reset_index()
    latest_vol.columns = ["Stock", "Volatility"]
    latest_vol["Stock"] = latest_vol["Stock"].str.replace(".NS", "", regex=False)
    st.dataframe(latest_vol, use_container_width=True)
else:
    st.warning("Volatility data unavailable for the selected stocks/date range.")

    st.subheader("📍 Risk vs Return")
    with st.expander("❓ What is Risk vs Return?"):
        st.write("""
        Each dot is one stock. **Higher on the chart** = better average return.
        **Further right** = more volatile / riskier. The ideal stock sits high and to the left —
        strong returns without much risk. In reality, most stocks trade off one for the other.
        """)
    avg_annual_return = daily_returns.mean() * 252 * 100
    avg_annual_vol = volatility_df.mean() * 100
    valid_tickers = [t for t in selected_tickers if t in avg_annual_return.index]
    scatter_df = pd.DataFrame({
        "Stock": [t.replace(".NS", "") for t in valid_tickers],
        "Avg Annual Return (%)": [avg_annual_return[t] for t in valid_tickers],
        "Avg Annual Volatility (%)": [avg_annual_vol[t] for t in valid_tickers],
        "Sector": [get_sector(t) for t in valid_tickers]
    })
    fig_scatter = px.scatter(scatter_df, x="Avg Annual Volatility (%)",
                             y="Avg Annual Return (%)", text="Stock",
                             color="Sector", size=[20]*len(scatter_df),
                             title="Risk vs Return", template="plotly_dark")
    fig_scatter.update_traces(textposition="top center", marker=dict(size=14))
    st.plotly_chart(fig_scatter, use_container_width=True)

    st.subheader("📊 Sharpe Ratio")
    with st.expander("❓ What is the Sharpe Ratio?"):
        st.write("""
        It measures **return per unit of risk** — how much reward you got for the volatility you took on.
        A Sharpe Ratio above 1 is generally considered good, above 2 is very good.
        Two stocks can have the same return, but the one with the higher Sharpe Ratio got there with less risk.
        """)
    risk_free_daily = 0.06 / 252
    excess_returns = daily_returns - risk_free_daily
    sharpe = (excess_returns.mean() / daily_returns.std()) * (252 ** 0.5)
    sharpe_df = pd.DataFrame({
        "Stock": [t.replace(".NS", "") for t in sharpe.index],
        "Sharpe Ratio": sharpe.values.round(2)
    }).sort_values("Sharpe Ratio", ascending=False)
    fig_sharpe = px.bar(sharpe_df, x="Stock", y="Sharpe Ratio",
                        color="Sharpe Ratio", color_continuous_scale="RdYlGn",
                        title="Sharpe Ratio — Selected Stocks",
                        template="plotly_dark", text="Sharpe Ratio")
    fig_sharpe.update_traces(textposition="outside")
    fig_sharpe.add_hline(y=1, line_dash="dash", line_color="white",
                         annotation_text="Good (>1)", annotation_position="top right")
    fig_sharpe.update_layout(showlegend=False)
    st.plotly_chart(fig_sharpe, use_container_width=True)

# ── Tab 5: Bollinger Bands ────────────────────────────────────────────────────
with tab5:
    st.subheader("Bollinger Bands")
    selected_bb = st.selectbox("Select Stock", selected_tickers,
                               format_func=lambda x: get_ticker_label(x), key="bb")
    if selected_bb in close_df.columns:
        bb_df = compute_bollinger_bands(close_df[selected_bb])
        st.plotly_chart(plot_bollinger_bands(bb_df, selected_bb), use_container_width=True)
    with st.expander("What are Bollinger Bands?"):
        st.write("""
        - **MA20** = 20-day moving average
        - **Upper Band** = MA20 + 2× std → potential **sell** zone
        - **Lower Band** = MA20 − 2× std → potential **buy** zone
        """)

# ── Tab 6: Signals & Correlation ──────────────────────────────────────────────
with tab6:
    st.subheader("MA Crossover Buy/Sell Signals")
    selected_sig = st.selectbox("Select Stock", selected_tickers,
                                format_func=lambda x: get_ticker_label(x), key="sig")
    if selected_sig in close_df.columns:
        signal_df = compute_ma_signals(close_df[selected_sig])
        st.plotly_chart(plot_ma_signals(signal_df, selected_sig), use_container_width=True)
    st.subheader("Correlation Heatmap")
    st.plotly_chart(plot_correlation_heatmap(daily_returns), use_container_width=True)

# ── Tab 7: Compare Stocks ─────────────────────────────────────────────────────
with tab7:
    st.subheader("⚖️ Stock Comparison Mode")
    col_a, col_b = st.columns(2)
    stock_a = col_a.selectbox("Stock A", selected_tickers,
                               format_func=lambda x: get_ticker_label(x),
                               index=0, key="compare_a")
    stock_b = col_b.selectbox("Stock B", selected_tickers,
                               format_func=lambda x: get_ticker_label(x),
                               index=min(1, len(selected_tickers)-1), key="compare_b")

    if stock_a == stock_b:
        st.warning("Please select two different stocks.")
    elif stock_a in close_df.columns and stock_b in close_df.columns:
        norm = close_df[[stock_a, stock_b]].copy()
        norm = (norm / norm.iloc[0]) * 100
        fig_compare = go.Figure()
        fig_compare.add_trace(go.Scatter(x=norm.index, y=norm[stock_a],
                                          name=get_ticker_label(stock_a),
                                          line=dict(color="cyan")))
        fig_compare.add_trace(go.Scatter(x=norm.index, y=norm[stock_b],
                                          name=get_ticker_label(stock_b),
                                          line=dict(color="orange")))
        fig_compare.update_layout(
            title=f"{get_ticker_label(stock_a)} vs {get_ticker_label(stock_b)} (Base=100)",
            xaxis_title="Date", yaxis_title="Normalized Price",
            template="plotly_dark", hovermode="x unified")
        st.plotly_chart(fig_compare, use_container_width=True)

        st.subheader("Head-to-Head Metrics")
        total_returns_full = (close_df.iloc[-1] / close_df.iloc[0] - 1) * 100
        avg_vol_full = volatility_df.mean()
        r_a = total_returns_full.get(stock_a, None)
        r_b = total_returns_full.get(stock_b, None)
        v_a = avg_vol_full.get(stock_a, None)
        v_b = avg_vol_full.get(stock_b, None)
        m1, m2 = st.columns(2)
        m3, m4 = st.columns(2)
        if r_a is not None and r_b is not None:
            m1.metric(f"{get_ticker_label(stock_a)} Return", f"{r_a:.1f}%")
            m2.metric(f"{get_ticker_label(stock_b)} Return", f"{r_b:.1f}%",
                      delta=f"{r_b - r_a:.1f}% vs A")
        if v_a is not None and v_b is not None:
            m3.metric(f"{get_ticker_label(stock_a)} Volatility", f"{v_a:.3f}")
            m4.metric(f"{get_ticker_label(stock_b)} Volatility", f"{v_b:.3f}",
                      delta=f"{v_b - v_a:.3f} vs A", delta_color="inverse")

# ── Tab 8: Investment Simulator ───────────────────────────────────────────────
with tab8:
    st.subheader("💰 Investment Simulator")
    sim_col1, sim_col2, sim_col3 = st.columns(3)
    sim_stock = sim_col1.selectbox("Pick a Stock", selected_tickers,
                                    format_func=lambda x: get_ticker_label(x), key="sim_stock")
    sim_amount = sim_col2.number_input("Investment Amount (₹)", min_value=1000,
                                        max_value=10000000, value=10000, step=1000)
    sim_start = sim_col3.date_input("Start Date", value=pd.to_datetime("2020-01-01"),
                                     key="sim_start")
    if sim_stock in close_df.columns:
        stock_series = close_df[sim_stock].dropna()
        sim_start_ts = pd.Timestamp(sim_start)
        available_dates = stock_series.index[stock_series.index >= sim_start_ts]
        if len(available_dates) == 0:
            st.warning("No data from this start date.")
        else:
            actual_start = available_dates[0]
            start_price = stock_series[actual_start]
            end_price = stock_series.iloc[-1]
            shares = sim_amount / start_price
            final_value = shares * end_price
            profit_loss = final_value - sim_amount
            pct_return = ((final_value - sim_amount) / sim_amount) * 100
            k1, k2, k3, k4 = st.columns(4)
            k1.metric("Amount Invested", f"₹{sim_amount:,.0f}")
            k2.metric("Current Value", f"₹{final_value:,.0f}", f"₹{profit_loss:,.0f}")
            k3.metric("Total Return", f"{pct_return:.1f}%")
            k4.metric("Shares Purchased", f"{shares:.4f}")
            sim_series = stock_series[stock_series.index >= actual_start]
            portfolio_value = (sim_series / start_price) * sim_amount
            fig_sim = go.Figure()
            fig_sim.add_trace(go.Scatter(x=portfolio_value.index, y=portfolio_value.values,
                                          mode="lines", name="Portfolio Value",
                                          line=dict(color="lime", width=2),
                                          fill="tozeroy", fillcolor="rgba(0,255,0,0.05)"))
            fig_sim.add_hline(y=sim_amount, line_dash="dash", line_color="gray",
                              annotation_text="Initial Investment")
            fig_sim.update_layout(title=f"₹{sim_amount:,.0f} in {get_ticker_label(sim_stock)}",
                                   xaxis_title="Date", yaxis_title="Portfolio Value (₹)",
                                   template="plotly_dark", hovermode="x unified")
            st.plotly_chart(fig_sim, use_container_width=True)

            st.subheader("Compare across selected stocks")
            comparison_data = []
            for ticker in selected_tickers:
                if ticker not in close_df.columns:
                    continue
                s = close_df[ticker].dropna()
                avail = s.index[s.index >= sim_start_ts]
                if len(avail) == 0:
                    continue
                fv = (s.iloc[-1] / s[avail[0]]) * sim_amount
                comparison_data.append({
                    "Stock": get_ticker_label(ticker),
                    "Sector": get_sector(ticker),
                    "Final Value (₹)": round(fv, 2),
                    "Return (%)": round(((fv - sim_amount) / sim_amount) * 100, 2)
                })
            comp_df = pd.DataFrame(comparison_data).sort_values("Return (%)", ascending=False)
            fig_comp = px.bar(comp_df, x="Stock", y="Final Value (₹)",
                              color="Return (%)", color_continuous_scale="RdYlGn",
                              title=f"Final Value of ₹{sim_amount:,.0f} across selected stocks",
                              template="plotly_dark", text="Return (%)")
            fig_comp.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
            fig_comp.add_hline(y=sim_amount, line_dash="dash", line_color="gray")
            st.plotly_chart(fig_comp, use_container_width=True)
            st.dataframe(comp_df, use_container_width=True)

# ── Tab 9: Price Race ─────────────────────────────────────────────────────────
with tab9:
    st.subheader("🎬 Stock Price Race")
    speed_option = st.select_slider("Animation Speed",
                                     options=["0.25x", "0.5x", "1x", "2x", "4x"], value="1x")
    speed_map = {"0.25x": 800, "0.5x": 400, "1x": 200, "2x": 100, "4x": 50}
    frame_duration = speed_map[speed_option]

    race_df = close_df.copy().dropna()

    if len(race_df) < 20:
        st.warning("Not enough overlapping data to build the price race — widen your date range or pick fewer/different stocks.")
    else:
        race_df = (race_df / race_df.iloc[0]) * 100
        race_df = race_df.reset_index()
        race_df["Date"] = pd.to_datetime(race_df["Date"]).dt.strftime("%Y-%m-%d")
        race_df = race_df.iloc[::10].reset_index(drop=True)
        race_long = race_df.melt(id_vars="Date", var_name="Stock", value_name="Value")
        race_long["Stock"] = race_long["Stock"].str.replace(".NS", "", regex=False)
        race_long["Value"] = race_long["Value"].round(2)

        fig_race = px.bar(race_long, x="Value", y="Stock", animation_frame="Date",
                          orientation="h", range_x=[0, race_long["Value"].max() * 1.15],
                          color="Stock", text="Value",
                          title="Stock Price Race (Normalized to 100)",
                          template="plotly_dark")
        fig_race.update_traces(texttemplate="%{text:.1f}", textposition="outside")
        fig_race.update_layout(xaxis_title="Normalized Price", yaxis_title="",
                                showlegend=False, height=500,
                                yaxis=dict(categoryorder="total ascending"))

        if fig_race.layout.updatemenus:
            fig_race.layout.updatemenus[0].buttons[0].args[1]["frame"]["duration"] = frame_duration
            fig_race.layout.updatemenus[0].buttons[0].args[1]["transition"]["duration"] = frame_duration // 2

        st.plotly_chart(fig_race, use_container_width=True)
        st.caption("Press ▶ to start the race.")

# ── Tab 10: Backtest ──────────────────────────────────────────────────────────
with tab10:
    st.subheader("🧪 MA Crossover Backtest")
    with st.expander("❓ What is this Backtest doing?"):
        st.write("""
        It simulates two strategies with the same starting money: one where you just buy and hold forever,
        and one where you buy when the 20-day average crosses above the 50-day average, and sell when it
        crosses back below. This shows whether "following the signals" would have actually beaten
        just holding the stock — often it doesn't, which is a real and useful finding.
        """)
    bt_col1, bt_col2 = st.columns(2)
    bt_stock = bt_col1.selectbox("Select Stock", selected_tickers,
                                  format_func=lambda x: get_ticker_label(x), key="bt_stock")
    bt_amount = bt_col2.number_input("Starting Capital (₹)", min_value=1000,
                                      max_value=10000000, value=10000, step=1000, key="bt_amount")
    if bt_stock in close_df.columns:
        prices = close_df[bt_stock].dropna()
        bt_df = pd.DataFrame({"Price": prices})
        bt_df["MA20"] = bt_df["Price"].rolling(20).mean()
        bt_df["MA50"] = bt_df["Price"].rolling(50).mean()
        bt_df.dropna(inplace=True)
        bt_df["Signal"] = 0
        bt_df.loc[bt_df["MA20"] > bt_df["MA50"], "Signal"] = 1
        bt_df["Daily Return"] = bt_df["Price"].pct_change(fill_method=None)
        bt_df["Strategy Return"] = bt_df["Daily Return"] * bt_df["Signal"].shift(1)
        bt_df.dropna(inplace=True)
        bt_df["Hold Value"] = bt_amount * (1 + bt_df["Daily Return"]).cumprod()
        bt_df["Strategy Value"] = bt_amount * (1 + bt_df["Strategy Return"]).cumprod()
        final_hold = bt_df["Hold Value"].iloc[-1]
        final_strategy = bt_df["Strategy Value"].iloc[-1]
        hold_return = ((final_hold - bt_amount) / bt_amount) * 100
        strategy_return = ((final_strategy - bt_amount) / bt_amount) * 100
        trades = bt_df["Signal"].diff().fillna(0)
        num_buys = (trades == 1).sum()
        num_sells = (trades == -1).sum()
        pct_in_market = (bt_df["Signal"].sum() / len(bt_df)) * 100
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Buy & Hold Return", f"{hold_return:.1f}%", f"₹{final_hold:,.0f}")
        k2.metric("Strategy Return", f"{strategy_return:.1f}%", f"₹{final_strategy:,.0f}")
        k3.metric("Total Trades", f"{int(num_buys)} buys / {int(num_sells)} sells")
        k4.metric("Days in Market", f"{pct_in_market:.1f}%")
        if strategy_return > hold_return:
            st.success(f"✅ Strategy BEAT buy & hold by {strategy_return - hold_return:.1f}%")
        else:
            st.warning(f"⚠️ Buy & Hold beat the strategy by {hold_return - strategy_return:.1f}%")
        fig_bt = go.Figure()
        fig_bt.add_trace(go.Scatter(x=bt_df.index, y=bt_df["Hold Value"],
                                     name="Buy & Hold", line=dict(color="cyan", width=2)))
        fig_bt.add_trace(go.Scatter(x=bt_df.index, y=bt_df["Strategy Value"],
                                     name="MA Strategy", line=dict(color="lime", width=2)))
        fig_bt.add_hline(y=bt_amount, line_dash="dash", line_color="gray",
                         annotation_text="Starting Capital")
        fig_bt.update_layout(title=f"Portfolio Growth — {get_ticker_label(bt_stock)}",
                              xaxis_title="Date", yaxis_title="Portfolio Value (₹)",
                              template="plotly_dark", hovermode="x unified")
        st.plotly_chart(fig_bt, use_container_width=True)

# ── Tab 11: SIP Simulator ─────────────────────────────────────────────────────
with tab11:
    st.subheader("📅 SIP Simulator")
    sip_col1, sip_col2, sip_col3 = st.columns(3)
    sip_stock = sip_col1.selectbox("Select Stock", selected_tickers,
                                    format_func=lambda x: get_ticker_label(x), key="sip_stock")
    sip_amount = sip_col2.number_input("Monthly SIP (₹)", min_value=500,
                                        max_value=1000000, value=5000, step=500, key="sip_amount")
    sip_start = sip_col3.date_input("SIP Start Date", value=pd.to_datetime("2020-01-01"),
                                     key="sip_start")
    if sip_stock in close_df.columns:
        prices = close_df[sip_stock].dropna()
        sip_start_ts = pd.Timestamp(sip_start)
        monthly_prices = prices[prices.index >= sip_start_ts].resample("MS").first().dropna()
        if len(monthly_prices) == 0:
            st.warning("No data from this start date.")
        else:
            total_invested = 0
            total_units = 0
            portfolio_history = []
            for date, price in monthly_prices.items():
                units_bought = sip_amount / price
                total_units += units_bought
                total_invested += sip_amount
                current_value = total_units * prices.asof(date)
                portfolio_history.append({
                    "Date": date,
                    "Total Invested (₹)": round(total_invested, 2),
                    "Portfolio Value (₹)": round(current_value, 2)
                })
            sip_df = pd.DataFrame(portfolio_history)
            final_value = total_units * prices.iloc[-1]
            profit = final_value - total_invested
            pct_return = (profit / total_invested) * 100
            years = len(monthly_prices) / 12
            annualized = ((final_value / total_invested) ** (1 / years) - 1) * 100 if years > 0 else 0
            k1, k2, k3, k4 = st.columns(4)
            k1.metric("Total Invested", f"₹{total_invested:,.0f}")
            k2.metric("Current Value", f"₹{final_value:,.0f}", f"₹{profit:,.0f}")
            k3.metric("Total Return", f"{pct_return:.1f}%")
            k4.metric("Annualized Return", f"{annualized:.1f}%")
            fig_sip = go.Figure()
            fig_sip.add_trace(go.Scatter(x=sip_df["Date"], y=sip_df["Portfolio Value (₹)"],
                                          name="Portfolio Value", line=dict(color="lime", width=2),
                                          fill="tozeroy", fillcolor="rgba(0,255,0,0.05)"))
            fig_sip.add_trace(go.Scatter(x=sip_df["Date"], y=sip_df["Total Invested (₹)"],
                                          name="Amount Invested",
                                          line=dict(color="gray", dash="dash")))
            fig_sip.update_layout(
                title=f"SIP Growth — ₹{sip_amount:,.0f}/month in {get_ticker_label(sip_stock)}",
                xaxis_title="Date", yaxis_title="Value (₹)",
                template="plotly_dark", hovermode="x unified")
            st.plotly_chart(fig_sip, use_container_width=True)
            lump_start_price = prices.asof(sip_start_ts)
            lump_value = (total_invested / lump_start_price) * prices.iloc[-1]
            lump_return = ((lump_value - total_invested) / total_invested) * 100
            c1, c2 = st.columns(2)
            c1.metric("SIP Final Value", f"₹{final_value:,.0f}", f"{pct_return:.1f}%")
            c2.metric("Lump Sum Final Value", f"₹{lump_value:,.0f}", f"{lump_return:.1f}%")
            if final_value > lump_value:
                st.success(f"✅ SIP outperformed Lump Sum by ₹{final_value - lump_value:,.0f}")
            else:
                st.info(f"📊 Lump Sum outperformed SIP by ₹{lump_value - final_value:,.0f}")
            with st.expander("📋 Monthly SIP Breakdown"):
                st.dataframe(sip_df, use_container_width=True)

# ── Tab 12: News Feed ─────────────────────────────────────────────────────────
with tab12:
    st.subheader("📰 Latest News")
    news_stock = st.selectbox("Select Stock", selected_tickers,
                               format_func=lambda x: get_ticker_label(x), key="news_stock")

    if st.button("🔄 Refresh News"):
        st.cache_data.clear()

    @st.cache_data(ttl=120, show_spinner="Fetching news...")
    def get_news(ticker):
        return fetch_news(ticker)

    news_items = get_news(news_stock)
    if news_items:
        st.caption(f"Showing {len(news_items)} articles — refreshes every 2 minutes")
        for item in news_items:
            with st.container():
                st.markdown(f"### [{item['title']}]({item['link']})")
                st.markdown(f"**{item['publisher']}** — {item['time']}")
                st.markdown("---")
    else:
        st.info("No news available for this stock right now.")

# ── Tab 13: Portfolio Builder ─────────────────────────────────────────────────
with tab13:
    st.subheader("🧺 Portfolio Builder")
    st.caption("Build a multi-stock portfolio with custom weights and track combined performance over time.")

    with st.expander("❓ What is portfolio weighting?"):
        st.write("""
        Instead of putting all your money into one stock, you split it across several — each gets a
        "weight" (percentage of your total capital). This is how real investors diversify. The chart
        compares your custom-weighted mix against simply splitting money equally across the same stocks.
        """)

    portfolio_stocks = st.multiselect(
        "Pick stocks for your portfolio (2–8 recommended)",
        options=selected_tickers,
        default=selected_tickers[:min(3, len(selected_tickers))],
        format_func=lambda x: get_ticker_label(x),
        key="portfolio_stocks"
    )

    if len(portfolio_stocks) < 2:
        st.info("Select at least 2 stocks to build a portfolio.")
    else:
        total_capital = st.number_input(
            "Total Capital to Invest (₹)",
            min_value=1000, max_value=100000000, value=100000, step=1000,
            key="portfolio_capital"
        )

        st.markdown("#### Set Allocation Weights (%)")
        st.caption("Weights should add up to 100%. Equal split is the default.")

        equal_weight = round(100 / len(portfolio_stocks), 2)
        weights = {}
        weight_cols = st.columns(min(len(portfolio_stocks), 4))

        for i, ticker in enumerate(portfolio_stocks):
            col = weight_cols[i % 4]
            weights[ticker] = col.number_input(
                get_ticker_label(ticker).split(" (")[0],
                min_value=0.0, max_value=100.0,
                value=equal_weight, step=1.0,
                key=f"weight_{ticker}"
            )

        total_weight = sum(weights.values())

        if abs(total_weight - 100) > 0.5:
            st.warning(f"⚠️ Weights sum to {total_weight:.1f}%, not 100%. Adjust before viewing results (they'll be auto-normalized below).")

        norm_weights = {t: w / total_weight for t, w in weights.items()} if total_weight > 0 else {}

        if norm_weights:
            portfolio_prices = close_df[portfolio_stocks].dropna()

            if portfolio_prices.empty:
                st.warning("No overlapping data available for the selected stocks in this date range.")
            else:
                units = {}
                for ticker in portfolio_stocks:
                    allocated_amount = total_capital * norm_weights[ticker]
                    start_price = portfolio_prices[ticker].iloc[0]
                    units[ticker] = allocated_amount / start_price

                portfolio_value_series = sum(
                    portfolio_prices[ticker] * units[ticker] for ticker in portfolio_stocks
                )

                final_value = portfolio_value_series.iloc[-1]
                total_return_pct = ((final_value - total_capital) / total_capital) * 100
                profit = final_value - total_capital

                benchmark_norm = (portfolio_prices / portfolio_prices.iloc[0]).mean(axis=1) * total_capital

                k1, k2, k3, k4 = st.columns(4)
                k1.metric("Capital Invested", f"₹{total_capital:,.0f}")
                k2.metric("Current Value", f"₹{final_value:,.0f}", f"₹{profit:,.0f}")
                k3.metric("Total Return", f"{total_return_pct:.1f}%")
                k4.metric("Stocks in Portfolio", f"{len(portfolio_stocks)}")

                fig_portfolio = go.Figure()
                fig_portfolio.add_trace(go.Scatter(
                    x=portfolio_value_series.index, y=portfolio_value_series.values,
                    name="Your Portfolio (Weighted)",
                    line=dict(color="lime", width=2),
                    fill="tozeroy", fillcolor="rgba(0,255,0,0.05)"
                ))
                fig_portfolio.add_trace(go.Scatter(
                    x=benchmark_norm.index, y=benchmark_norm.values,
                    name="Equal-Weight Benchmark",
                    line=dict(color="gray", width=2, dash="dash")
                ))
                fig_portfolio.add_hline(y=total_capital, line_dash="dot", line_color="white",
                                        annotation_text="Initial Capital")
                fig_portfolio.update_layout(
                    title="Portfolio Growth — Weighted vs Equal-Weight Benchmark",
                    xaxis_title="Date", yaxis_title="Portfolio Value (₹)",
                    template="plotly_dark", hovermode="x unified"
                )
                st.plotly_chart(fig_portfolio, use_container_width=True)

                st.markdown("#### Allocation Breakdown")
                alloc_data = []
                for ticker in portfolio_stocks:
                    allocated_amt = total_capital * norm_weights[ticker]
                    current_val = portfolio_prices[ticker].iloc[-1] * units[ticker]
                    stock_return = ((current_val - allocated_amt) / allocated_amt) * 100
                    alloc_data.append({
                        "Stock": get_ticker_label(ticker),
                        "Weight (%)": round(norm_weights[ticker] * 100, 1),
                        "Allocated (₹)": round(allocated_amt, 2),
                        "Current Value (₹)": round(current_val, 2),
                        "Return (%)": round(stock_return, 2)
                    })
                alloc_df = pd.DataFrame(alloc_data)

                col_pie, col_table = st.columns([1, 1.5])
                with col_pie:
                    fig_pie = px.pie(
                        alloc_df, names="Stock", values="Allocated (₹)",
                        title="Capital Allocation", template="plotly_dark", hole=0.4
                    )
                    st.plotly_chart(fig_pie, use_container_width=True)
                with col_table:
                    st.dataframe(
                        alloc_df.sort_values("Return (%)", ascending=False),
                        use_container_width=True, hide_index=True
                    )

                st.markdown("#### Which stock contributed most to your return?")
                contribution_df = alloc_df.copy()
                contribution_df["Contribution (₹)"] = contribution_df["Current Value (₹)"] - contribution_df["Allocated (₹)"]
                contribution_df = contribution_df.sort_values("Contribution (₹)", ascending=False)
                fig_contrib = px.bar(
                    contribution_df, x="Stock", y="Contribution (₹)",
                    color="Contribution (₹)", color_continuous_scale="RdYlGn",
                    title="Profit/Loss Contribution by Stock",
                    template="plotly_dark", text="Contribution (₹)"
                )
                fig_contrib.update_traces(texttemplate="₹%{text:,.0f}", textposition="outside")
                fig_contrib.update_layout(showlegend=False)
                st.plotly_chart(fig_contrib, use_container_width=True)

                csv_portfolio = alloc_df.to_csv(index=False).encode("utf-8")
                st.download_button("📥 Download Portfolio Breakdown (CSV)", csv_portfolio,
                                    "portfolio_breakdown.csv", "text/csv")