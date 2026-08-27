import streamlit as st
import components.chat as chat

st.set_page_config(
    page_title="Tutor Inteligente",
    page_icon="💻",
    layout="wide"
)

import os

if "instrucao" not in st.session_state:
    st.session_state.instrucao = None

if st.session_state.instrucao is None:
    st.markdown("<h2 style='text-align: center; margin-top: -10px; margin-bottom: 0px;'>💻 Tutor Inteligente de Cálculo 1</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #666; margin-bottom: 15px;'>Escolha um tópico para iniciar o atendimento:</p>", unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown("##### 📐 1. Funções")
        st.image("assets/imgs/funcoes.png", width=120)
        if st.button("Funções Reais", key="btn_f_reais", use_container_width=True):
            st.session_state.instrucao = "funcoes_reais.txt"
            st.rerun()
        if st.button("Polinômios & Álgebra", key="btn_f_pol", use_container_width=True):
            st.session_state.instrucao = "funcoes_polinomiais_e_expressoes_algebricas.txt"
            st.rerun()
        if st.button("Funções Modulares", key="btn_f_mod", use_container_width=True):
            st.session_state.instrucao = "funcoes_modulares.txt"
            st.rerun()
        if st.button("Exponenciais & Log", key="btn_f_exp", use_container_width=True):
            st.session_state.instrucao = "funcoes_exponenciais_e_logaritmicas.txt"
            st.rerun()
        if st.button("Trigonométricas", key="btn_f_trig", use_container_width=True):
            st.session_state.instrucao = "funcoes_trigonometricas_e_inversas.txt"
            st.rerun()

    with col2:
        st.markdown("##### 📊 2. Limites")
        st.image("assets/imgs/limite.png", width=120)
        if st.button("Limites e Continuidade", key="btn_limites", use_container_width=True):
            st.session_state.instrucao = "limites_e_continuidade.txt"
            st.rerun()

    with col3:
        st.markdown("##### ⚡ 3. Derivadas")
        st.image("assets/imgs/derivada.png", width=120)
        if st.button("Conceitos e Regras", key="btn_derivadas", use_container_width=True):
            st.session_state.instrucao = "derivadas.txt"
            st.rerun()
        if st.button("Aplicações das Derivadas", key="btn_ap_derivadas", use_container_width=True):
            st.session_state.instrucao = "aplicacoes_das_derivadas.txt"
            st.rerun()

    with col4:
        st.markdown("##### 🔄 4. Integrais")
        if os.path.exists("assets/imgs/integral.png"):
            st.image("assets/imgs/integral.png", width=120)
        if st.button("Primitivas Elementares", key="btn_primitivas", use_container_width=True):
            st.session_state.instrucao = "primitivas_elementares.txt"
            st.rerun()

    st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
    if st.button("Continuar sem tópico específico (Geral)", type="primary", use_container_width=True, key="btn_continuar"):
        st.session_state.instrucao = "Geral"
        st.rerun()

else:
    col_info, col_btn = st.columns([4, 1])
    
    with col_info:
        nome_exibicao = st.session_state.instrucao.replace(".txt", "").replace("_", " ").title() if st.session_state.instrucao.endswith(".txt") else st.session_state.instrucao
        st.info(f"Tópico selecionado: **{nome_exibicao}**")
        
    with col_btn:
        if st.button("Trocar Tópico", use_container_width=True):
            st.session_state.instrucao = None
            if "historico" in st.session_state:
                del st.session_state["historico"]
            st.rerun()

    st.divider()
    chat.renderizar_chat_expansivo()
