import streamlit as st

if "instrucao" not in st.session_state:
    st.session_state.instrucao  = " "

def index():
    st.title("Tutor Inteligente", text_alignment="center")

    st.text("Conheca as opcoes de selecao para iniciar caso necessario:")

    funcoes_img, limite_img, derivada_img, integral_img = st.columns(4, border=True)

    funcoes_img.image("assets/imgs/funcoes.png")
    limite_img.image("assets/imgs/limite.png")
    derivada_img.image("assets/imgs/derivada.png")
    integral_img.image("assets/imgs/integral.png")

    funcoes_btn, limite_btn, derivada_btn, integral_btn = st.columns(4)

    clicou_funcoes = funcoes_btn.button("Funcoes", key="funcoes_img", use_container_width=True)
    clicou_limite = limite_btn.button("Limites", key="limite", use_container_width=True)
    clicou_derivada = derivada_btn.button("Derivadas", key="derivada", use_container_width=True)
    clicou_integral = integral_btn.button("Integral", key="integral", use_container_width=True)

    continuar_btn = st.button("Continuar", use_container_width=True)

    if clicou_funcoes:
        st.session_state.instrucao = "funcoes"
        st.rerun()
    if clicou_limite:
        st.session_state.instrucao = "limite"
        st.rerun()
    if clicou_derivada:
        st.session_state.instrucao = "derivada"
        st.rerun()
    if clicou_integral:
        st.session_state.instrucao = "integral"
        st.rerun()
    if continuar_btn:
        st.session_state.instrucao = False
        st.rerun()


index_page = st.Page(index, title="Tutor Inteligente")
chat_page = st.Page("chat.py", title="Chat Tutor Inteligente")

if st.session_state.instrucao == " ":
    pg = st.navigation([index_page])
else:
    pg = st.navigation([chat_page])

pg.run()