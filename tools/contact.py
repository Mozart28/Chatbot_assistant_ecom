
import streamlit as st



@st.cache_data
def request_contact():
    return (
    
        "👤 Nom : Service Commercial\n\n"
        "📧 Email : commercial@smartshop.com\n\n"
        "📱 Téléphone : +221 77 123 45 67\n\n"
        "💬 WhatsApp : [📲 Cliquer pour WhatsApp](https://wa.me/221771234567)"
    )

