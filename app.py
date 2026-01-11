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

# --- Init agent ---
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

    # Appel agent
    with st.chat_message("assistant"):
        with st.spinner("Recherche en cours..."):
            response = st.session_state.agent.run(user_input)

            # 🔹 CAS STRUCTURÉ (dict)
            if isinstance(response, dict):

                # 🖼 IMAGE PRODUIT
                if response["type"] == "product_image":
                    product = response["product"]

                    st.subheader(product["name"])
                    st.image(product["image_url"], use_container_width=True)

                    if product.get("price"):
                        st.markdown(f"💰 **Prix :** {product['price']} FCFA")

                    if product.get("in_stock"):
                        st.success("✅ En stock")
                    else:
                        st.warning("❌ Rupture de stock")

                    # Sauvegarde texte pour l’historique
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": f"🖼️ {product['name']} — {product['price']} FCFA"
                    })

                # 💬 TEXTE
                elif response["type"] == "text":
                    st.markdown(response["message"])
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response["message"]
                    })

            # 🔹 CAS TEXTE SIMPLE
            else:
                st.markdown(response)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response
                })
