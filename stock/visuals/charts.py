import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

def plot_price_trends(close_df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    for col in close_df.columns:
        fig.add_trace(go.Scatter(
            x=close_df.index,
            y=close_df[col],
            name=col.replace(".NS", ""),
            mode="lines"
        ))
    fig.update_layout(
        title="Stock Price Trends (2020–2024)",
        xaxis_title="Date",
        yaxis_title="Price (INR)",
        hovermode="x unified",
        template="plotly_dark"
    )
    return fig

def plot_cumulative_returns(cum_returns: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    for col in cum_returns.columns:
        fig.add_trace(go.Scatter(
            x=cum_returns.index,
            y=cum_returns[col] * 100,
            name=col.replace(".NS", ""),
            mode="lines"
        ))
    fig.update_layout(
        title="Cumulative Returns (%)",
        xaxis_title="Date",
        yaxis_title="Return (%)",
        hovermode="x unified",
        template="plotly_dark"
    )
    return fig

def plot_daily_returns_distribution(daily_returns: pd.DataFrame, ticker: str) -> go.Figure:
    fig = px.histogram(
        daily_returns[ticker],
        nbins=100,
        title=f"Daily Return Distribution — {ticker.replace('.NS', '')}",
        labels={"value": "Daily Return", "count": "Frequency"},
        template="plotly_dark"
    )
    return fig

def plot_rolling_volatility(volatility_df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    for col in volatility_df.columns:
        fig.add_trace(go.Scatter(
            x=volatility_df.index,
            y=volatility_df[col],
            name=col.replace(".NS", ""),
            mode="lines"
        ))
    fig.update_layout(
        title="Rolling 20-Day Annualized Volatility",
        xaxis_title="Date",
        yaxis_title="Volatility",
        hovermode="x unified",
        template="plotly_dark"
    )
    return fig

def plot_bollinger_bands(bb_df: pd.DataFrame, ticker: str) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=bb_df.index, y=bb_df["Price"],
                             name="Price", line=dict(color="white")))
    fig.add_trace(go.Scatter(x=bb_df.index, y=bb_df["MA20"],
                             name="MA20", line=dict(color="yellow", dash="dash")))
    fig.add_trace(go.Scatter(x=bb_df.index, y=bb_df["Upper Band"],
                             name="Upper Band", line=dict(color="red", dash="dot")))
    fig.add_trace(go.Scatter(x=bb_df.index, y=bb_df["Lower Band"],
                             name="Lower Band", line=dict(color="green", dash="dot"),
                             fill="tonexty", fillcolor="rgba(0,255,0,0.05)"))
    fig.update_layout(
        title=f"Bollinger Bands — {ticker.replace('.NS', '')}",
        xaxis_title="Date",
        yaxis_title="Price (INR)",
        template="plotly_dark"
    )
    return fig

def plot_ma_signals(signal_df: pd.DataFrame, ticker: str) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=signal_df.index, y=signal_df["Price"],
                             name="Price", line=dict(color="white")))
    fig.add_trace(go.Scatter(x=signal_df.index, y=signal_df["MA20"],
                             name="MA20", line=dict(color="cyan", dash="dash")))
    fig.add_trace(go.Scatter(x=signal_df.index, y=signal_df["MA50"],
                             name="MA50", line=dict(color="orange", dash="dash")))

    # Buy signals
    buys = signal_df[signal_df["Position"] == 1]
    fig.add_trace(go.Scatter(x=buys.index, y=buys["Price"],
                             mode="markers", name="Buy Signal",
                             marker=dict(color="lime", size=10, symbol="triangle-up")))

    # Sell signals
    sells = signal_df[signal_df["Position"] == -2]
    fig.add_trace(go.Scatter(x=sells.index, y=sells["Price"],
                             mode="markers", name="Sell Signal",
                             marker=dict(color="red", size=10, symbol="triangle-down")))

    fig.update_layout(
        title=f"MA Crossover Signals — {ticker.replace('.NS', '')}",
        xaxis_title="Date",
        yaxis_title="Price (INR)",
        template="plotly_dark"
    )
    return fig