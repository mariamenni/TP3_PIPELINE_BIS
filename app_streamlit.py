"""
Application Streamlit - GEO Data Explorer 

"""

import streamlit as st
import pandas as pd
from pathlib import Path

# =============================
# IMPORTS PROJET
# =============================
from utils.data import load_all_parquets
from utils.charts import (
    create_geo_map,
    population_by_city,
    create_histogram,
    create_scatter_plot,
    create_heatmap,
)
from utils.chatbot import DataChatbot

# =============================
# CONFIG PAGE
# =============================
st.set_page_config(
    page_title="GEO Data Explorer",
    page_icon="🌍",
    layout="wide",
)

# =============================
# CHARGEMENT DES DONNÉES
# =============================
@st.cache_data(show_spinner=True)
def load_data():
    data_path = Path("data/processed")
    return load_all_parquets(data_path)

try:
    df = load_data()
except Exception as e:
    st.error(f"❌ Erreur lors du chargement des données : {e}")
    st.stop()

# =============================
# INITIALISATION SESSION STATE
# =============================
if "messages" not in st.session_state:
    st.session_state.messages = []

if "chatbot" not in st.session_state:
    st.session_state.chatbot = DataChatbot(df)


# =============================
# HEADER
# =============================
st.title("🌍 GEO Data Explorer")
st.markdown(
    "*Dashboard interactif basé sur les données géographiques produites *"
)

# =============================
# SIDEBAR — FILTRES
# =============================
st.sidebar.header("🔍 Filtres")

# --- Filtre Ville ---
city_choices = ["Toutes"]
if "city" in df.columns:
    city_choices += sorted(df["city"].dropna().unique())

city = st.sidebar.selectbox("Ville", city_choices)

# --- Filtre Score ---
min_score = st.sidebar.slider(
    "Score minimum de géocodage",
    0.0,
    1.0,
    0.5,
    step=0.05,
)

# =============================
# APPLICATION DES FILTRES
# =============================
df_filtered = df.copy()

if city != "Toutes":
    df_filtered = df_filtered[df_filtered["city"] == city]

df_filtered = df_filtered[df_filtered["score"] >= min_score]

# =============================
# MÉTRIQUES
# =============================
st.header("📊 Vue d’ensemble")

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric("Lignes", f"{len(df_filtered):,}")

with c2:
    st.metric("Colonnes", len(df_filtered.columns))

with c3:
    if "population" in df_filtered.columns:
        st.metric(
            "Population moyenne",
            f"{df_filtered['population'].mean():,.0f}"
        )

with c4:
    st.metric(
        "Villes uniques",
        df_filtered["city"].nunique() if "city" in df_filtered.columns else 0
    )

# =============================
# VISUALISATIONS
# =============================
st.header("📈 Visualisations")

tab1, tab2, tab3 = st.tabs(
    ["🗺️ Carte", "📊 Analyses", "🔗 Corrélations"]
)

# --- CARTE ---
with tab1:
    st.subheader("Carte des adresses géocodées")
    fig = create_geo_map(df_filtered)
    st.plotly_chart(fig, use_container_width=True)

# --- ANALYSES ---
with tab2:
    st.subheader("Analyses dynamiques")

    numeric_cols = df_filtered.select_dtypes(include="number").columns.tolist()

    col1, col2 = st.columns(2)

    with col1:
        x_col = st.selectbox("Colonne X", numeric_cols)
        fig = create_histogram(
            df_filtered,
            x=x_col,
            title=f"Distribution de {x_col}",
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        y_col = st.selectbox("Colonne Y", numeric_cols)
        fig = create_scatter_plot(
            df_filtered,
            x=x_col,
            y=y_col,
            color="city" if "city" in df_filtered.columns else None,
            title=f"{y_col} en fonction de {x_col}",
        )
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Population moyenne par ville")
    fig = population_by_city(df_filtered)
    st.plotly_chart(fig, use_container_width=True)

# --- CORRÉLATIONS ---
with tab3:
    st.subheader("Matrice de corrélation")
    fig = create_heatmap(df_filtered)
    st.plotly_chart(fig, use_container_width=True)

# =============================
# DONNÉES
# =============================
st.header("🗃️ Données")

with st.expander("Afficher les 100 premières lignes"):
    st.dataframe(df_filtered.head(100), use_container_width=True)

# =============================
# CHATBOT
# =============================

SUGGESTIONS = [
    "Quelles sont les villes les plus peuplées ?",
    "La qualité du géocodage est-elle bonne ?",
    "Y a-t-il une corrélation entre population et score ?",
    "Propose des analyses intéressantes sur ce dataset",
]

st.header("🤖 Assistant Data")

# --- Boutons de suggestions ---
st.markdown("**Suggestions de questions :**")
cols = st.columns(len(SUGGESTIONS))

for col, suggestion in zip(cols, SUGGESTIONS):
    if col.button(suggestion, use_container_width=True):
        # Ajouter la question utilisateur
        st.session_state.messages.append(
            {"role": "user", "content": suggestion}
        )

        # Appel LLM
        response = st.session_state.chatbot.chat(suggestion)

        # Ajouter la réponse assistant
        st.session_state.messages.append(
            {"role": "assistant", "content": response}
        )

        st.rerun()  


# --- Affichage de l'historique (UNE SEULE FOIS) ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])


# --- Input utilisateur ---
if prompt := st.chat_input("Posez une question sur les données..."):
    st.session_state.messages.append(
        {"role": "user", "content": prompt}
    )

    response = st.session_state.chatbot.chat(prompt)

    st.session_state.messages.append(
        {"role": "assistant", "content": response}
    )

    st.rerun()


# --- Reset conversation ---
if st.button("🔄 Nouvelle conversation"):
    st.session_state.chatbot.reset()
    st.session_state.messages = []
    st.rerun()