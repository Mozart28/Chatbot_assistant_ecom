
import streamlit as st
from core.agent import CommercialAgent
from config.settings import APP_NAME

# --- Page config ---
st.set_page_config(
    page_title=APP_NAME,
    page_icon="🛒",
    layout="centered"
)

# --- Title ---
st.title("🛒 Assistant Commercial IA")
st.caption("Je vous propose uniquement des produits disponibles dans notre catalogue.")

# --- Init agent (une seule fois) ---
if "agent" not in st.session_state:
    st.session_state.agent = CommercialAgent()

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Display chat history ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- User input ---
user_input = st.chat_input("Que cherchez-vous ? (ex: chaussures homme cuir)")

if user_input:
    # Affiche message utilisateur
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    with st.chat_message("user"):
        st.markdown(user_input)

    # Agent response
    with st.chat_message("assistant"):
        with st.spinner("Recherche de produits disponibles..."):
            response = st.session_state.agent.run(user_input)
            st.markdown(response)

    st.session_state.messages.append({
        "role": "assistant",
        "content": response
    })
