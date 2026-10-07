import streamlit as st

import core.session as sess
import services.ai as ai
import utils.conversor as conv
import utils.graph as gc

def obter_input_usuario():
    return st.chat_input(
        "Digite sua dúvida ou o exercício de matemática...", 
        accept_file=True, 
        file_type=["png", "jpg", "jpeg"]
    )

def processar_interacao_ia(prompt_data):
    imagem_carregada = (
        prompt_data.files[0]
        if prompt_data.files
        else None
    )

    # 1. Adiciona e exibe a mensagem do usuário
    sess.adicionar_mensagem_usuario(
        prompt_data.text,
        imagem_carregada
    )

    # 2. Transmite a resposta da IA em tempo real com Streaming
    with st.chat_message("assistant"):
        area_texto = st.empty()

        with st.spinner("O tutor está pensando..."):
            resposta_completa = area_texto.write_stream(
                ai.requisitar_tutor_stream(sess.montar_payload())
            )

        grafico = None
        texto_final = resposta_completa

        # 3. Detecta se a IA incluiu um bloco de gráfico
        if ai.verificar_grafico(resposta_completa):
            grafico, texto_final = ai.extrair_grafico(resposta_completa)
            # Remove o JSON cru da tela e exibe o texto explicativo formatado
            area_texto.markdown(conv.formatar_latex(texto_final))

            if grafico:
                try:
                    fig = gc.processar_grafico(grafico)
                    st.plotly_chart(fig, width="stretch")
                except Exception as e:
                    st.error(f"Não foi possível gerar o gráfico: {e}")
        else:
            area_texto.markdown(conv.formatar_latex(texto_final))

    # 4. Registra no histórico para preservar o contexto nas próximas perguntas
    sess.adicionar_interacao_assistente(texto_final, grafico)
    st.rerun()

def renderizar_chat_tela_cheia():
    recem_inicializado = sess.inicializar_mensagens()
    if not recem_inicializado:
        sess.atualizar_mensagens()

    prompt_data = obter_input_usuario()

    if prompt_data and (prompt_data.text.strip() or prompt_data.files):
        processar_interacao_ia(prompt_data)

def renderizar_chat_expansivo():
    with st.expander("Chat com o tutor", expanded=True):
        caixa_de_texto = st.container()

        with caixa_de_texto:
            recem_inicializado = sess.inicializar_mensagens()
            if not recem_inicializado:
                sess.atualizar_mensagens()

        prompt_data = obter_input_usuario()

        if prompt_data and (prompt_data.text.strip() or prompt_data.files):
            with caixa_de_texto:
                processar_interacao_ia(prompt_data)
