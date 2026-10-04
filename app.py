import os
import streamlit as st
import components.chat as chat

st.set_page_config(
    page_title="Tutor Inteligente de Cálculo 1",
    page_icon="🎓",
    layout="wide"
)

# Custom CSS para elevar o visual, igualar altura dos cards e aumentar os botões
st.markdown(
    """
    <style>
    .main-title {
        text-align: center;
        font-size: 2.3rem;
        font-weight: 800;
        background: linear-gradient(135deg, #1E88E5 0%, #42A5F5 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-top: -15px;
        margin-bottom: 5px;
    }
    .sub-title {
        text-align: center;
        font-size: 1.05rem;
        color: #555;
        margin-bottom: 25px;
    }
    .category-header {
        font-size: 1.15rem;
        font-weight: 700;
        color: #1565C0;
        margin-bottom: 12px;
        text-align: center;
    }
    /* Igualar a altura mínima dos 4 cards para alinhamento perfeito */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        min-height: 450px !important;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    /* Aumentar o tamanho e área de clique dos botões */
    div.stButton > button {
        border-radius: 9px;
        font-weight: 600;
        font-size: 0.98rem;
        padding: 0.65rem 0.6rem;
        min-height: 46px;
        margin-top: 4px;
        margin-bottom: 4px;
        transition: all 0.2s ease-in-out;
    }
    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 14px rgba(0,0,0,0.18);
    }
    </style>
    """,
    unsafe_allow_html=True
)

if "instrucao" not in st.session_state:
    st.session_state.instrucao = None

if st.session_state.instrucao is None:
    st.markdown('<div class="main-title">🎓 Tutor Inteligente de Cálculo 1</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Selecione um tópico do programa de estudos para iniciar seu atendimento socrático:</div>', unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        with st.container(border=True):
            st.markdown('<div class="category-header">📐 1. Funções</div>', unsafe_allow_html=True)
            if os.path.exists("assets/imgs/funcoes.png"):
                st.image("assets/imgs/funcoes.png", use_container_width=True)
            st.markdown("<div style='margin-bottom: 4px;'></div>", unsafe_allow_html=True)
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
        with st.container(border=True):
            st.markdown('<div class="category-header">📊 2. Limites</div>', unsafe_allow_html=True)
            if os.path.exists("assets/imgs/limite.png"):
                st.image("assets/imgs/limite.png", use_container_width=True)
            st.markdown("<div style='margin-bottom: 4px;'></div>", unsafe_allow_html=True)
            if st.button("Limites e Continuidade", key="btn_limites", use_container_width=True):
                st.session_state.instrucao = "limites_e_continuidade.txt"
                st.rerun()
            # Espaçadores para alinhamento vertical harmônico dos botões
            st.markdown("<div style='height: 160px;'></div>", unsafe_allow_html=True)

    with col3:
        with st.container(border=True):
            st.markdown('<div class="category-header">⚡ 3. Derivadas</div>', unsafe_allow_html=True)
            if os.path.exists("assets/imgs/derivada.png"):
                st.image("assets/imgs/derivada.png", use_container_width=True)
            st.markdown("<div style='margin-bottom: 4px;'></div>", unsafe_allow_html=True)
            if st.button("Conceitos e Regras", key="btn_derivadas", use_container_width=True):
                st.session_state.instrucao = "derivadas.txt"
                st.rerun()
            if st.button("Aplicações das Derivadas", key="btn_ap_derivadas", use_container_width=True):
                st.session_state.instrucao = "aplicacoes_das_derivadas.txt"
                st.rerun()
            # Espaçador para alinhamento vertical harmônico dos botões
            st.markdown("<div style='height: 105px;'></div>", unsafe_allow_html=True)

    with col4:
        with st.container(border=True):
            st.markdown('<div class="category-header">🔄 4. Integrais</div>', unsafe_allow_html=True)
            if os.path.exists("assets/imgs/integral.png"):
                st.image("assets/imgs/integral.png", use_container_width=True)
            st.markdown("<div style='margin-bottom: 4px;'></div>", unsafe_allow_html=True)
            if st.button("Primitivas Elementares", key="btn_primitivas", use_container_width=True):
                st.session_state.instrucao = "primitivas_elementares.txt"
                st.rerun()
            # Espaçadores para alinhamento vertical harmônico dos botões
            st.markdown("<div style='height: 160px;'></div>", unsafe_allow_html=True)

    st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
    if st.button("🚀 Continuar sem tópico específico (Atendimento Geral)", type="primary", use_container_width=True, key="btn_continuar"):
        st.session_state.instrucao = "Geral"
        st.rerun()

else:
    col_info, col_btn = st.columns([4, 1])
    
    with col_info:
        nome_exibicao = st.session_state.instrucao.replace(".txt", "").replace("_", " ").title() if st.session_state.instrucao.endswith(".txt") else st.session_state.instrucao
        st.info(f"🎯 **Tópico em Estudo:** {nome_exibicao}")
        
    with col_btn:
        if st.button("🔄 Trocar Tópico", use_container_width=True):
            st.session_state.instrucao = None
            if "historico" in st.session_state:
                del st.session_state["historico"]
            st.rerun()

    st.divider()
    chat.renderizar_chat_expansivo()
