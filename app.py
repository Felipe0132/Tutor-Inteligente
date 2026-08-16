import streamlit as st
import components.chat as chat

st.set_page_config(
    page_title="Tutor Inteligente",
    page_icon="💻",
    layout="wide"
)

chat.renderizar_chat_expansivo()
