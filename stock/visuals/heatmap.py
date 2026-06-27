import plotly.figure_factory as ff
import plotly.express as px
import pandas as pd

def plot_correlation_heatmap(daily_returns: pd.DataFrame) -> px.imshow:
    corr = daily_returns.corr().round(2)
    clean_cols = [c.replace(".NS", "") for c in corr.columns]

    fig = px.imshow(
        corr,
        text_auto=True,
        x=clean_cols,
        y=clean_cols,
        color_continuous_scale="RdBu",
        title="Stock Return Correlation Heatmap",
        template="plotly_dark"
    )
    fig.update_layout(width=600, height=500)
    return fig