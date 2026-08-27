import streamlit as st

import core.session as sess
import services.ai as ai
import utils.conversor as conv

def obter_input_usuario():
    return st.chat_input(
        "Digite sua dúvida ou o exercício de matemática...", 
        accept_file=True, 
        file_type=["png", "jpg", "jpeg"]
    )
'''
def processar_interacao_ia(prompt_data):
    imagem_carregada = (prompt_data.files[0] if prompt_data.files else None)

    sess.adicionar_mensagem_usuario(prompt_data.text, imagem_carregada)
    
    resposta_tutor = ""

    with st.spinner("O tutor está processando sua mensagem..."):
        resposta_tutor = ai.requisitar_tutor(sess.montar_payload(prompt_data))

    texto = resposta_tutor.strip()

    if ai.verificar_grafico(resposta_tutor):
        grafico, texto = ai.extrair_grafico(resposta_tutor)
        sess.adcionar_grafico("assistant", grafico)
    
    sess.adcionar_mensagem("assistant", texto)
    
    st.rerun()
'''

def processar_interacao_ia(prompt_data):
    imagem_carregada = (
        prompt_data.files[0]
        if prompt_data.files
        else None
    )

    sess.adicionar_mensagem_usuario(
        prompt_data.text,
        imagem_carregada
    )

    with st.spinner("O tutor está processando sua mensagem..."):
        resposta_tutor = ai.requisitar_tutor(
            sess.montar_payload(prompt_data)
        )

    texto = resposta_tutor.strip()

    if ai.verificar_grafico(resposta_tutor):
        grafico, texto = ai.extrair_grafico(
            resposta_tutor
        )

        if grafico:
            sess.adicionar_grafico(
                "assistant",
                grafico
            )

    sess.adcionar_mensagem(
        "assistant",
        texto
    )

    st.rerun()

def renderizar_chat_tela_cheia():
    sess.inicializar_mensagens()
    sess.atualizar_mensagens()

    prompt_data = obter_input_usuario()

    if prompt_data and (prompt_data.text.strip() or prompt_data.files):
        processar_interacao_ia(prompt_data)


def renderizar_chat_expansivo():
    with st.expander("Chat com o tutor", expanded=True):
        caixa_de_texto = st.container()

        with caixa_de_texto:
            sess.inicializar_mensagens()
            sess.atualizar_mensagens()

        prompt_data = obter_input_usuario()

        if prompt_data and (prompt_data.text.strip() or prompt_data.files):
            with caixa_de_texto:
                processar_interacao_ia(prompt_data)

