
import streamlit as st
import pandas as pd
import requests
import folium
from streamlit_folium import st_folium

st.set_page_config(layout="wide")
st.title("📡 Système d'Alerte NDVI – Réserve de So’o Lala")

# Connexion à l'API Render
url = "https://ndvi-api-1.onrender.com/ndvi_alerts.php"

try:
    response = requests.get(url)
    data = response.json()
    df = pd.DataFrame(data)
    df["NDVI"] = df["NDVI"].astype(float)
    df["latitude"] = df["latitude"].astype(float)
    df["longitude"] = df["longitude"].astype(float)

    # Marquer les alertes NDVI ≤ 0.3 comme critiques
    df["Alerte"] = df["NDVI"].apply(lambda x: "🔴 Critique" if x <= 0.3 else "🟢 Stable")
    st.success("Connexion API réussie ✅")
except Exception as e:
    st.error(f"Erreur de connexion à l’API : {e}")
    st.stop()

# Affichage tableau
st.subheader("📋 Données d'alerte NDVI")
st.dataframe(df[["date", "NDVI", "latitude", "longitude", "Alerte"]])

# Carte
st.subheader("🗺️ Carte des points NDVI")
m = folium.Map(location=[3.5, 12.2], zoom_start=8)

for _, row in df.iterrows():
    color = "red" if row["Alerte"] == "🔴 Critique" else "green"
    folium.CircleMarker(
        location=[row["latitude"], row["longitude"]],
        radius=7,
        popup=f"Date: {row['date']} | NDVI: {row['NDVI']}",
        color=color,
        fill=True,
        fill_opacity=0.8
    ).add_to(m)

st_folium(m, height=500)
