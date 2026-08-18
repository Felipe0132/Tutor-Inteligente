import streamlit as st
import components.chat as chat

st.set_page_config(
    page_title="Tutor Inteligente",
    page_icon="💻",
    layout="wide"
)

if "instrucao" not in st.session_state:
    st.session_state.instrucao = None

st.title("Bem-Vindo ao Tutor Inteligente de Calculo 1!")
st.markdown(
    """
    Esta é uma aplicação demonstrativa desenvolvida para facilitar a navegação. 
    Escolha uma das opções abaixo para continuar.
    """
)

st.divider()

# --- Seção de Botões ---
st.subheader("Escolha uma opção que deseja aprofundar")

# Criando colunas para organizar os 3 botões de imagem lado a lado
col1, col2, col3 = st.columns(3)

# Botão de Imagem 1
with col1:
    st.image("assets/imgs/funcoes.png", use_container_width=True)
    if st.button("Funções", key="btn_funcoes", use_container_width=True):
        st.session_state.instrucao = "Funcoes"

# Botão de Imagem 2
with col2:
    st.image("assets/imgs/limite.png", use_container_width=True)
    if st.button("Limites", key="btn_limites", use_container_width=True):
        st.session_state.instrucao = "Limites"

# Botão de Imagem 3
with col3:
    st.image("assets/imgs/derivada.png", use_container_width=True)
    if st.button("Derivadas", key="btn_derivadas", use_container_width=True):
        st.session_state.instrucao = "Derivadas"

st.markdown("<br>", unsafe_allow_html=True)

# --- Botão Default ---
if st.button("Continuar sem tópico específico", type="primary", use_container_width=True, key="btn_continuar"):
    st.session_state.instrucao = "Geral"

if st.session_state.instrucao:
    st.divider()
    st.info(f"Tópico selecionado: **{st.session_state.instrucao}**")
    chat.renderizar_chat_expansivo()
