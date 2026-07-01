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

# ── Sidebar ──────────────────────────────────────────────────────────────────
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
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9 = st.tabs([
    "📊 Overview",
    "📉 Returns",
    "🌊 Volatility",
    "📐 Bollinger Bands",
    "🔀 Signals & Correlation",
    "⚖️ Compare Stocks",
    "💰 Investment Simulator",
    "🎬 Price Race",
    "🧪 Backtest"
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
            m1.metric(f"{stock_a.replace('.NS','')} Total Return", f"{r_a:.1f}%")
            m2.metric(f"{stock_b.replace('.NS','')} Total Return", f"{r_b:.1f}%",
                      delta=f"{r_b - r_a:.1f}% vs {stock_a.replace('.NS','')}")
        else:
            m1.metric(f"{stock_a.replace('.NS','')} Total Return", "N/A")
            m2.metric(f"{stock_b.replace('.NS','')} Total Return", "N/A")

        if v_a is not None and v_b is not None:
            m3.metric(f"{stock_a.replace('.NS','')} Avg Volatility", f"{v_a:.3f}")
            m4.metric(f"{stock_b.replace('.NS','')} Avg Volatility", f"{v_b:.3f}",
                      delta=f"{v_b - v_a:.3f} vs {stock_a.replace('.NS','')}",
                      delta_color="inverse")
        else:
            m3.metric(f"{stock_a.replace('.NS','')} Avg Volatility", "N/A")
            m4.metric(f"{stock_b.replace('.NS','')} Avg Volatility", "N/A")
# ── Tab 7: Investment Simulator ───────────────────────────────────────────────
with tab7:
    st.subheader("💰 Investment Simulator")
    st.caption("See what your investment would be worth today based on historical data.")

    sim_col1, sim_col2, sim_col3 = st.columns(3)
    sim_stock = sim_col1.selectbox("Pick a Stock", TICKERS,
                                    format_func=lambda x: TICKER_LABELS[x],
                                    key="sim_stock")
    sim_amount = sim_col2.number_input("Investment Amount (₹)", min_value=1000,
                                        max_value=10000000, value=10000, step=1000)
    sim_start = sim_col3.date_input("Investment Start Date",
                                     value=pd.to_datetime("2020-01-01"),
                                     min_value=pd.to_datetime("2020-01-01"),
                                     max_value=pd.to_datetime("2024-12-31"),
                                     key="sim_start")

    if sim_stock and sim_amount:
        stock_series = close_df[sim_stock].dropna()
        sim_start_ts = pd.Timestamp(sim_start)

        # Find nearest available trading date
        available_dates = stock_series.index[stock_series.index >= sim_start_ts]

        if len(available_dates) == 0:
            st.warning("No data available from this start date. Try an earlier date.")
        else:
            actual_start = available_dates[0]
            start_price = stock_series[actual_start]
            end_price = stock_series.iloc[-1]

            shares = sim_amount / start_price
            final_value = shares * end_price
            profit_loss = final_value - sim_amount
            pct_return = ((final_value - sim_amount) / sim_amount) * 100

            # KPI row
            k1, k2, k3, k4 = st.columns(4)
            k1.metric("Amount Invested", f"₹{sim_amount:,.0f}")
            k2.metric("Current Value", f"₹{final_value:,.0f}",
                      delta=f"₹{profit_loss:,.0f}")
            k3.metric("Total Return", f"{pct_return:.1f}%")
            k4.metric("Shares Purchased", f"{shares:.4f}")

            # Growth chart
            sim_series = stock_series[stock_series.index >= actual_start]
            portfolio_value = (sim_series / start_price) * sim_amount

            fig_sim = go.Figure()
            fig_sim.add_trace(go.Scatter(
                x=portfolio_value.index,
                y=portfolio_value.values,
                mode="lines",
                name="Portfolio Value",
                line=dict(color="lime", width=2),
                fill="tozeroy",
                fillcolor="rgba(0,255,0,0.05)"
            ))
            fig_sim.add_hline(y=sim_amount, line_dash="dash",
                              line_color="gray",
                              annotation_text="Initial Investment",
                              annotation_position="top left")
            fig_sim.update_layout(
                title=f"₹{sim_amount:,.0f} invested in {sim_stock.replace('.NS','')} from {actual_start.date()}",
                xaxis_title="Date",
                yaxis_title="Portfolio Value (₹)",
                template="plotly_dark",
                hovermode="x unified"
            )
            st.plotly_chart(fig_sim, use_container_width=True)

            # Compare all stocks with same amount
            st.subheader("How would it compare across all stocks?")
            comparison_data = []
            for ticker in TICKERS:
                s = close_df[ticker].dropna()
                avail = s.index[s.index >= sim_start_ts]
                if len(avail) == 0:
                    continue
                sp = s[avail[0]]
                ep = s.iloc[-1]
                fv = (ep / sp) * sim_amount
                comparison_data.append({
                    "Stock": ticker.replace(".NS", ""),
                    "Final Value (₹)": round(fv, 2),
                    "Return (%)": round(((fv - sim_amount) / sim_amount) * 100, 2)
                })

            comp_df = pd.DataFrame(comparison_data).sort_values("Return (%)", ascending=False)

            fig_comp = px.bar(
                comp_df,
                x="Stock",
                y="Final Value (₹)",
                color="Return (%)",
                color_continuous_scale="RdYlGn",
                title=f"Final Value of ₹{sim_amount:,.0f} across all stocks",
                template="plotly_dark",
                text="Return (%)"
            )
            fig_comp.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
            fig_comp.add_hline(y=sim_amount, line_dash="dash",
                               line_color="gray",
                               annotation_text="Initial Investment")
            st.plotly_chart(fig_comp, use_container_width=True)
            st.dataframe(comp_df, use_container_width=True)

# ── Tab 8: Price Race Animation ───────────────────────────────────────────────
# ── Tab 8: Price Race Animation ───────────────────────────────────────────────
with tab8:
    st.subheader("🎬 Stock Price Race")
    st.caption("Animated bar chart race showing normalized price growth over time (Base = 100)")

    # Speed control
    speed_option = st.select_slider(
        "Animation Speed",
        options=["0.25x", "0.5x", "1x", "2x", "4x"],
        value="1x"
    )

    speed_map = {
        "0.25x": 800,
        "0.5x": 400,
        "1x": 200,
        "2x": 100,
        "4x": 50
    }
    frame_duration = speed_map[speed_option]

    race_df = close_df.copy().dropna()
    race_df = (race_df / race_df.iloc[0]) * 100
    race_df = race_df.reset_index()
    race_df["Date"] = pd.to_datetime(race_df["Date"]).dt.strftime("%Y-%m-%d")

    # Sample every 10 days
    race_df = race_df.iloc[::10].reset_index(drop=True)

    race_long = race_df.melt(id_vars="Date", var_name="Stock", value_name="Value")
    race_long["Stock"] = race_long["Stock"].str.replace(".NS", "", regex=False)
    race_long["Value"] = race_long["Value"].round(2)

    color_map = {
        "TCS": "#636EFA",
        "INFY": "#EF553B",
        "RELIANCE": "#00CC96",
        "HDFCBANK": "#AB63FA",
        "WIPRO": "#FFA15A"
    }

    fig_race = px.bar(
        race_long,
        x="Value",
        y="Stock",
        animation_frame="Date",
        orientation="h",
        range_x=[0, race_long["Value"].max() * 1.15],
        color="Stock",
        color_discrete_map=color_map,
        text="Value",
        title="Stock Price Race — Normalized to 100 (2020–2024)",
        template="plotly_dark"
    )

    fig_race.update_traces(texttemplate="%{text:.1f}", textposition="outside")
    fig_race.update_layout(
        xaxis_title="Normalized Price (Base = 100)",
        yaxis_title="",
        showlegend=False,
        height=450,
        yaxis=dict(categoryorder="total ascending")
    )

    fig_race.layout.updatemenus[0].buttons[0].args[1]["frame"]["duration"] = frame_duration
    fig_race.layout.updatemenus[0].buttons[0].args[1]["transition"]["duration"] = frame_duration // 2

    st.plotly_chart(fig_race, use_container_width=True)
    st.caption("Press ▶ to start. Use the speed slider above to control animation pace. 0.25x is slowest, 4x is fastest.")

# ── Tab 9: MA Crossover Backtest ──────────────────────────────────────────────
with tab9:
    st.subheader("🧪 MA Crossover Backtest Simulator")
    st.caption("Simulates buying and selling based on MA20 vs MA50 crossover signals. Compares strategy returns vs simply holding.")

    bt_col1, bt_col2 = st.columns(2)
    bt_stock = bt_col1.selectbox("Select Stock", TICKERS,
                                  format_func=lambda x: TICKER_LABELS[x],
                                  key="bt_stock")
    bt_amount = bt_col2.number_input("Starting Capital (₹)", min_value=1000,
                                      max_value=10000000, value=10000, step=1000,
                                      key="bt_amount")

    # Build backtest
    prices = close_df[bt_stock].dropna()
    bt_df = pd.DataFrame({"Price": prices})
    bt_df["MA20"] = bt_df["Price"].rolling(20).mean()
    bt_df["MA50"] = bt_df["Price"].rolling(50).mean()
    bt_df.dropna(inplace=True)

    # Signal: 1 = hold/buy, 0 = out of market
    bt_df["Signal"] = 0
    bt_df.loc[bt_df["MA20"] > bt_df["MA50"], "Signal"] = 1

    # Backtest logic
    bt_df["Daily Return"] = bt_df["Price"].pct_change(fill_method=None)
    bt_df["Strategy Return"] = bt_df["Daily Return"] * bt_df["Signal"].shift(1)
    bt_df.dropna(inplace=True)

    # Cumulative portfolio value
    bt_df["Hold Value"] = bt_amount * (1 + bt_df["Daily Return"]).cumprod()
    bt_df["Strategy Value"] = bt_amount * (1 + bt_df["Strategy Return"]).cumprod()

    # Final values
    final_hold = bt_df["Hold Value"].iloc[-1]
    final_strategy = bt_df["Strategy Value"].iloc[-1]
    hold_return = ((final_hold - bt_amount) / bt_amount) * 100
    strategy_return = ((final_strategy - bt_amount) / bt_amount) * 100

    # Signal stats
    trades = bt_df["Signal"].diff().fillna(0)
    num_buys = (trades == 1).sum()
    num_sells = (trades == -1).sum()
    days_in_market = bt_df["Signal"].sum()
    pct_in_market = (days_in_market / len(bt_df)) * 100

    # KPI row
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Buy & Hold Return", f"{hold_return:.1f}%", f"₹{final_hold:,.0f}")
    k2.metric("Strategy Return", f"{strategy_return:.1f}%", f"₹{final_strategy:,.0f}",
              delta_color="normal")
    k3.metric("Total Trades", f"{int(num_buys)} buys / {int(num_sells)} sells")
    k4.metric("Days in Market", f"{pct_in_market:.1f}%")

    # Winner banner
    if strategy_return > hold_return:
        st.success(f"✅ Strategy BEAT buy & hold by {strategy_return - hold_return:.1f}%")
    else:
        st.warning(f"⚠️ Buy & Hold beat the strategy by {hold_return - strategy_return:.1f}% — signals didn't help here")

    # Portfolio growth chart
    fig_bt = go.Figure()
    fig_bt.add_trace(go.Scatter(
        x=bt_df.index,
        y=bt_df["Hold Value"],
        name="Buy & Hold",
        line=dict(color="cyan", width=2)
    ))
    fig_bt.add_trace(go.Scatter(
        x=bt_df.index,
        y=bt_df["Strategy Value"],
        name="MA Crossover Strategy",
        line=dict(color="lime", width=2)
    ))
    fig_bt.add_hline(y=bt_amount, line_dash="dash",
                     line_color="gray",
                     annotation_text="Starting Capital",
                     annotation_position="top left")
    fig_bt.update_layout(
        title=f"Portfolio Growth — {bt_stock.replace('.NS','')} | Starting ₹{bt_amount:,.0f}",
        xaxis_title="Date",
        yaxis_title="Portfolio Value (₹)",
        template="plotly_dark",
        hovermode="x unified"
    )
    st.plotly_chart(fig_bt, use_container_width=True)

    # Buy/sell signal markers on price
    st.subheader("Buy & Sell Points on Price Chart")
    signal_changes = bt_df["Signal"].diff().fillna(0)
    buy_points = bt_df[signal_changes == 1]
    sell_points = bt_df[signal_changes == -1]

    fig_signals = go.Figure()
    fig_signals.add_trace(go.Scatter(
        x=bt_df.index, y=bt_df["Price"],
        name="Price", line=dict(color="white", width=1)
    ))
    fig_signals.add_trace(go.Scatter(
        x=bt_df.index, y=bt_df["MA20"],
        name="MA20", line=dict(color="cyan", dash="dash", width=1)
    ))
    fig_signals.add_trace(go.Scatter(
        x=bt_df.index, y=bt_df["MA50"],
        name="MA50", line=dict(color="orange", dash="dash", width=1)
    ))
    fig_signals.add_trace(go.Scatter(
        x=buy_points.index, y=buy_points["Price"],
        mode="markers", name="Buy",
        marker=dict(color="lime", size=10, symbol="triangle-up")
    ))
    fig_signals.add_trace(go.Scatter(
        x=sell_points.index, y=sell_points["Price"],
        mode="markers", name="Sell",
        marker=dict(color="red", size=10, symbol="triangle-down")
    ))
    fig_signals.update_layout(
        title=f"Trade Signals — {bt_stock.replace('.NS', '')}",
        xaxis_title="Date",
        yaxis_title="Price (INR)",
        template="plotly_dark",
        hovermode="x unified"
    )
    st.plotly_chart(fig_signals, use_container_width=True)

    # Raw trade log
    with st.expander("📋 View Trade Log"):
        trade_log = bt_df[signal_changes != 0][["Price", "Signal"]].copy()
        trade_log["Action"] = trade_log["Signal"].map({1: "BUY", 0: "SELL"})
        trade_log = trade_log[["Price", "Action"]]
        trade_log["Price"] = trade_log["Price"].round(2)
        st.dataframe(trade_log, use_container_width=True)