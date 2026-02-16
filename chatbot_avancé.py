import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Chat IA", page_icon="💬", layout="wide")

st.title("💬 Chat IA")

# --- Historique des messages ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Interface du chat ---
for msg in st.session_state.get("messages", []):
    role = msg.get("role", "assistant")

    with st.chat_message(role):

        content = msg.get("content")
        image_url = msg.get("image_url")

        if content:
            st.markdown(content, unsafe_allow_html=True)

        if image_url:
            st.image(image_url, use_column_width=True)


# --- Champ texte et bouton micro ---
col1, col2 = st.columns([8, 1])

with col1:
    user_input = st.chat_input("Écris ton message...")

with col2:
    # Composant HTML pour le micro
    components.html(
        """
        <button id="mic" style="font-size:20px; padding:8px; border-radius:50%; background-color:#0d6efd; color:white; border:none; cursor:pointer;">🎤</button>
        <script>
        const button = document.getElementById("mic");
        button.onclick = () => {
            const recognition = new window.webkitSpeechRecognition() || new window.SpeechRecognition();
            recognition.lang = 'fr-FR';
            recognition.interimResults = false;
            recognition.maxAlternatives = 1;
            recognition.start();
            recognition.onresult = (event) => {
                const text = event.results[0][0].transcript;
                const streamlitInput = window.parent.document.querySelector("input[placeholder='Écris ton message...']");
                streamlitInput.value = text;
                streamlitInput.dispatchEvent(new Event('change'));
            }
        }
        </script>
        """,
        height=50,
    )

# --- Ajouter le message utilisateur ---
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Exemple de réponse IA (ici simple echo, tu peux mettre ton modèle)
    response = f"IA: {user_input}"
    st.session_state.messages.append({"role": "ai", "content": response})
    
    st.rerun()
