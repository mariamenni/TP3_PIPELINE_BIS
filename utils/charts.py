"""
Module de visualisations interactives avec Plotly.
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd


# ==========================================================
# GRAPHIQUES 
# ==========================================================
def create_bar_chart(df: pd.DataFrame, x: str, y: str, title: str = "") -> go.Figure:
    fig = px.bar(df, x=x, y=y, title=title, template="plotly_dark")
    fig.update_layout(
        xaxis_title=x,
        yaxis_title=y,
        hovermode="x unified"
    )
    return fig


def create_pie_chart(df: pd.DataFrame, names: str, values: str, title: str = "") -> go.Figure:
    fig = px.pie(
        df, names=names, values=values,
        title=title, hole=0.3
    )
    fig.update_traces(textposition="inside", textinfo="percent+label")
    return fig


def create_scatter_plot(
    df: pd.DataFrame,
    x: str,
    y: str,
    color: str | None = None,
    title: str = ""
) -> go.Figure:
    fig = px.scatter(
        df, x=x, y=y, color=color,
        title=title, template="plotly_dark"
    )
    fig.update_traces(marker=dict(size=8, opacity=0.7))
    return fig


def create_histogram(
    df: pd.DataFrame,
    x: str,
    nbins: int = 30,
    title: str = ""
) -> go.Figure:
    return px.histogram(
        df, x=x, nbins=nbins,
        title=title, template="plotly_dark"
    )


def create_line_chart(df: pd.DataFrame, x: str, y: str, title: str = "") -> go.Figure:
    return px.line(
        df, x=x, y=y,
        title=title, template="plotly_dark",
        markers=True
    )


def create_heatmap(df: pd.DataFrame, title: str = "") -> go.Figure:
    numeric_df = df.select_dtypes(include=["number"])
    corr = numeric_df.corr()

    return px.imshow(
        corr,
        title=title or "Matrice de corrélation",
        color_continuous_scale="RdBu_r",
        aspect="auto"
    )


# ==========================================================
# GRAPHIQUES SPÉCIFIQUES GEO 
# ==========================================================
def create_geo_map(df: pd.DataFrame) -> go.Figure:
    """
    Carte interactive des adresses géocodées.
    
    """

    fig = px.scatter_mapbox(
        df,
        lat="latitude",
        lon="longitude",
        color="city",
        hover_name="commune",
        hover_data={
            "population": True,
            "score": ":.2f",
            "latitude": False,
            "longitude": False,
        },
        zoom=4,
        mapbox_style="open-street-map",
        height=650,   
    )

    # Ajuste automatiquement la vue aux points
    fig.update_layout(
        margin=dict(l=0, r=0, t=50, b=0),
        mapbox=dict(
            center=dict(
                lat=df["latitude"].mean(),
                lon=df["longitude"].mean(),
            )
        ),
    )

    return fig


def population_by_city(df: pd.DataFrame) -> go.Figure:
    """
    Population moyenne par ville.
    """
    agg = (
        df.groupby("city", as_index=False)["population"]
        .mean()
        .sort_values("population", ascending=False)
    )

    return create_bar_chart(
        agg,
        x="city",
        y="population",
        title="Population moyenne par ville"
    )
