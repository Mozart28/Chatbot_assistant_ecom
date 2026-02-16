import streamlit as st
from core.agent import CommercialAgent
from core.state_manager import ConversationState
from config.settings import APP_NAME
from streamlit_option_menu import option_menu
import streamlit.components.v1 as components
from tools.contact import request_contact
from tools.cart import add_product_to_cart
import sqlite3
from datetime import datetime

# --- Page config ---
st.set_page_config(
    page_title=APP_NAME,
    page_icon="🛒",
    layout="wide",
)

def save_rating(rating, message_index):
    conn = sqlite3.connect("feedback.db")
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message_index INTEGER,
            rating INTEGER,
            created_at TEXT
        )
    """)

    c.execute("""
        INSERT INTO feedback (message_index, rating, created_at)
        VALUES (?, ?, ?)
    """, (message_index, rating, datetime.now().isoformat()))

    conn.commit()
    conn.close()


# ======================================================
# SIDEBAR
# ======================================================
with st.sidebar:
    st.logo(
         "data:image/jpeg;base64,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",
            size="large",
    )

    st.caption("Assistant commercial intelligent")
    st.divider()
    st.markdown("### 👤 Espace client")

    if st.button("Nouvelle commande", use_container_width=True):
        st.session_state.messages = []
        st.session_state.cart = []
        st.session_state.conversation_state = ConversationState()
        st.session_state.agent = CommercialAgent(state=st.session_state.conversation_state)
        st.rerun()

    if st.button("🛒 Mon panier", use_container_width=True):
        if st.session_state.cart:
            st.success(f"{len(st.session_state.cart)} produit(s) dans le panier")
        else:
            st.info("Panier vide")
    
    st.divider()

    with st.expander("🔐 Espace administrateur"):
        st.text_input("Email")
        st.text_input("Mot de passe", type="password")
        st.button("Connexion")

    st.write("Mozart Solutions")

# ======================================================
# HEADER
# ======================================================
st.markdown("""
<style>
    .main-header {
        padding: 2rem 0;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="main-header">
    <h1>🛒 Smart Shop</h1>
    <p>Trouvez, comparez et achetez vos produits avec l'aide de l'IA</p>
</div>
""", unsafe_allow_html=True)


# ======================================================
# INIT SESSION STATE
# ======================================================
if "conversation_state" not in st.session_state:
    st.session_state.conversation_state = ConversationState()

if "agent" not in st.session_state:
    st.session_state.agent = CommercialAgent(state=st.session_state.conversation_state)

if "messages" not in st.session_state:
    st.session_state.messages = []

if "cart" not in st.session_state:
    st.session_state.cart = []

if "photo_mode" not in st.session_state:
    st.session_state.photo_mode = False

if "agent_mode" not in st.session_state:
    st.session_state.agent_mode = False

# Welcome message
if not st.session_state.messages:
    st.session_state.messages.append({
        "role": "assistant",
        "content": "👋 Bonjour ! Je suis votre assistant SmartShop. Que recherchez-vous aujourd'hui ?",
    })


# ======================================================
# UTILITY FUNCTIONS
# ======================================================
def handle_pending_choice(user_input):
    """Handle user response when a choice is pending"""
    state = st.session_state.conversation_state
    
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    text = user_input.lower().strip()
    
    # Vague response → force clarification
    if text in ["oui", "ok", "d'accord"]:
        assistant_msg = (
            "Parfait 🙂 Que souhaitez-vous faire ?\n"
            "1️⃣ Ajouter le produit au panier\n"
            "2️⃣ Voir d'autres produits similaires"
        )
        with st.chat_message("assistant"):
            st.markdown(assistant_msg)
        
        st.session_state.messages.append({
            "role": "assistant",
            "content": assistant_msg
        })
        st.stop()
    
    # Choice 1: Add to cart
    elif text in ["1", "ajouter", "ajouter au panier"]:
        # Get product from agent's current_product
        product = st.session_state.agent.current_product
        
        if not product:
            with st.chat_message("assistant"):
                st.markdown("❌ Produit introuvable.")
            state.clear()
            return
        
        msg = add_product_to_cart(product)
        state.clear()
        
        with st.chat_message("assistant"):
            st.success("✅ Produit ajouté au panier.")
            st.markdown("Souhaitez-vous compléter avec un accessoire ?")
        
        st.session_state.messages.append({
            "role": "assistant",
            "content": msg + "\n\nSouhaitez-vous compléter avec un accessoire ?"
        })
        st.stop()
    
    # Choice 2: See similar products
    elif text in ["2", "voir", "autres", "similaires"]:
        state.clear()
        response = st.session_state.agent.run("produits similaires")
        
        with st.chat_message("assistant"):
            st.markdown(response.get("message", "Voici d'autres produits similaires."))
        
        st.session_state.messages.append({
            "role": "assistant",
            "content": response.get("message", "Voici d'autres produits similaires.")
        })
        st.stop()


# ======================================================
# ACTIONS FOOTER
# ======================================================
st.markdown("---")
col1, col2 = st.columns(2)

with col1:
    if st.button("📷 Importer une photo", disabled=st.session_state.photo_mode):
        st.session_state.photo_mode = True
        st.session_state.agent_mode = False

with col2:
    if st.button("💬 Parler à un agent commercial"):
        st.session_state.photo_mode = False
        st.session_state.agent_mode = True
        st.session_state.trigger_agent_message = True


# ======================================================
# MODE PHOTO
# ======================================================
if st.session_state.photo_mode:
    if st.button("❌ Annuler la photo"):
        st.session_state.photo_mode = False

    st.markdown("### 📷 Envoyez une photo du produit")
    
    image_file = st.file_uploader("Importer depuis la galerie", type=["png", "jpg", "jpeg"])
    
    if image_file:
        st.image(image_file, caption="Image reçue", use_container_width=True)
        st.session_state.messages.append({"role": "user", "content": "📷 Image envoyée"})
        st.success("Image reçue ! Analyse en cours…")


# ======================================================
# MODE AGENT COMMERCIAL
# ======================================================
if st.session_state.get("trigger_agent_message", False):
    contact_msg = request_contact()
    
    agent_message = (
        "💬 Un agent commercial va prendre le relais.\n\n"
        "📞 Contactez-nous via WhatsApp ou laissez un message sur notre boite mail.\n\n"
        f"{contact_msg}"
    )
    
    st.session_state.messages.append({
        "role": "assistant",
        "content": agent_message,
        "type": "CONTACT_AGENT",
        "rated": False
    })
    
    st.session_state.trigger_agent_message = False


# ======================================================
# CHAT HISTORY + RATING
# ======================================================
for i, msg in enumerate(st.session_state.get("messages", [])):
    role = msg.get("role", "assistant")
    
    with st.chat_message(role):
        if msg.get("content"):
            st.markdown(msg["content"], unsafe_allow_html=True)
        
        if msg.get("image_url"):
            st.image(msg["image_url"], use_column_width=True)
        
        # ⭐ Rating only for contact agent
        if msg.get("type") == "CONTACT_AGENT" and not msg.get("rated"):
            rating = st.slider(
                "⭐ Notez cette mise en relation",
                1, 5, 3,
                key=f"rating_{i}"
            )
            
            if st.button("Envoyer", key=f"send_rating_{i}"):
                save_rating(rating, i)
                st.session_state.messages[i]["rated"] = True
                st.toast("Merci pour votre retour 🙏")


# ======================================================
# USER INPUT
# ======================================================
user_input = st.chat_input("Ex : chaussures homme cuir, chemises, polo..")

if user_input:
    # Check if pending choice exists
    state = st.session_state.conversation_state
    
    if state.pending_choice:
        handle_pending_choice(user_input)
    else:
        # Normal flow
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        with st.chat_message("user"):
            st.markdown(user_input)
        
        if not st.session_state.photo_mode and not st.session_state.agent_mode:
            with st.chat_message("assistant"):
                with st.spinner("Réponse en cours..."):
                    response = st.session_state.agent.run(user_input)
                
                if isinstance(response, dict):
                    # Handle product image display
                    if response.get("type") == "product_image":
                        product = response["product"]
                        st.subheader(product["name"])
                        st.image(product["image_url"], use_column_width=True)
                        
                        if product.get("price"):
                            st.markdown(f"💰 **Prix :** {product['price']} FCFA")
                        
                        if product.get("in_stock"):
                            st.success("✅ Immédiatement disponible")
                        else:
                            st.warning("❌ Cet article est en rupture de stock")
                        
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": f"🖼️ {product['name']} — {product['price']} FCFA"
                        })
                    
                    # Handle contact request
                    elif response.get("type") == "request_contact":
                        contact_msg = request_contact()
                        st.markdown(contact_msg)
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": contact_msg,
                            "type": "CONTACT_AGENT",
                            "rated": False
                        })
                    
                    # Handle add to cart - FIXED VERSION WITH STATE CLEARING
                    elif response.get("type") == "add_to_cart":
                        product = response.get("product")
                        
                        if product:
                            msg = add_product_to_cart(product)
                            st.success("✅ Produit ajouté au panier.")
                            
                            # CRITICAL: Clear the conversation state to prevent repetition
                            st.session_state.conversation_state.clear()
                            
                            # Add follow-up message
                            follow_up = "Souhaitez-vous ajouter autre chose ?"
                            st.markdown(follow_up)
                            
                            # Add to message history
                            st.session_state.messages.append({
                                "role": "assistant",
                                "content": msg
                            })
                            
                            st.session_state.messages.append({
                                "role": "assistant",
                                "content": follow_up
                            })
                        else:
                            st.error("❌ Produit introuvable")
                            st.session_state.messages.append({
                                "role": "assistant",
                                "content": "❌ Produit introuvable"
                            })
                    
                    # Handle text response
                    elif response.get("type") == "text":
                        st.markdown(response["message"])
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": response["message"]
                        })
                
                else:
                    st.markdown(response)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response
                    })


# ======================================================
# CART SIDEBAR
# ======================================================
if st.session_state.cart:
    with st.sidebar:
        st.markdown("---")
        st.markdown("### 🛒 Panier")
        
        total = sum(int(item["price"]) for item in st.session_state.cart)
        
        for item in st.session_state.cart:
            st.markdown(f"- {item['name']} — {item['price']} FCFA")
        
        st.markdown(f"**Total : {total} FCFA**")
        
        if st.button("✅ Commander", use_container_width=True):
            st.success("Commande envoyée !")
            st.balloons()
