import streamlit as st
import pyrebase
import requests
import pandas as pd
import pydeck as pdk
from firebase_config import firebase_config

firebase = pyrebase.initialize_app(firebase_config)
auth = firebase.auth()

st.set_page_config(page_title="Système NDVI", layout="centered")
st.title("📡 Système d'Alerte NDVI – Réserve de So’o Lala")

# Si l'utilisateur n'est pas connecté
if 'user' not in st.session_state:

    mode = st.radio("Choisissez une action :", ["🔐 Connexion", "🆕 Créer un compte"])

    if mode == "🆕 Créer un compte":
        st.subheader("Créer un compte utilisateur")
        email_new = st.text_input("Email", key="new_email")
        password_new = st.text_input("Mot de passe", type="password", key="new_password")
        if st.button("Créer mon compte"):
            try:
                user = auth.create_user_with_email_and_password(email_new, password_new)
                st.success("🎉 Compte créé avec succès. Connectez-vous maintenant.")
            except Exception as e:
                st.error(f"❌ Erreur : {e}")

    elif mode == "🔐 Connexion":
        st.subheader("Connexion utilisateur")
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Mot de passe", type="password", key="login_password")
        if st.button("Se connecter"):
            try:
                user = auth.sign_in_with_email_and_password(email, password)
                st.session_state['user'] = user
                st.success("✅ Connexion réussie !")
                st.experimental_rerun()
            except:
                st.error("❌ Email ou mot de passe incorrect.")
else:
    # Interface principale après connexion
    st.success(f"Bienvenue, {st.session_state['user']['email']}")

    if st.button("🚪 Se déconnecter"):
        st.session_state.pop('user')
        st.experimental_rerun()

    st.markdown("---")
    st.subheader("📋 Données d'alerte NDVI")
    api_url = "https://ndvi-api-1.onrender.com/ndvi_alerts.php"

    try:
        response = requests.get(api_url)
        if response.status_code == 200:
            data = response.json()

            # Nettoyage
            for d in data:
                d["NDVI"] = float(d["NDVI"])
                d["latitude"] = float(d["latitude"])
                d["longitude"] = float(d["longitude"])

            df = pd.DataFrame(data)
            st.dataframe(df)

            # Carte
            st.subheader("🗺️ Carte des points NDVI")
            st.pydeck_chart(pdk.Deck(
                map_style="mapbox://styles/mapbox/satellite-streets-v11",
                initial_view_state=pdk.ViewState(
                    latitude=df["latitude"].mean(),
                    longitude=df["longitude"].mean(),
                    zoom=9
                ),
                layers=[
                    pdk.Layer(
                        'ScatterplotLayer',
                        data=df,
                        get_position='[longitude, latitude]',
                        get_color='[255, 0, 0, 160]',
                        get_radius=300
                    )
                ]
            ))

        else:
            st.error("Erreur lors de la récupération des données NDVI.")

    except Exception as e:
        st.error(f"Erreur API : {e}")
