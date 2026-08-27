import streamlit as st
import json
from dotenv import load_dotenv
import utils.conversor as conv
import utils.leitor_arquivo as lv
#import utils.graficos as gc
import utils.graph as gc
import services.ai as ai


SYSTEM_PROMPT = lv.ler_arquivo("contexto.txt")

def inicializar_mensagens():
    if "tutor_ocupado" not in st.session_state:
        st.session_state.tutor_ocupado = False  # Inicializa o estado do tutor como disponível

    if "historico" not in st.session_state:
        st.session_state.historico = []

        with st.spinner("O tutor está se preparando..."):
            introducao = ai.requisitar_tutor(montar_payload_inicial())
            # Adiciona a mensagem de introdução ao histórico
            # Sem a função de atualizar_mensagens() aqui, pois será chamada no app.py após a inicialização
            st.session_state.historico.append(("assistant", introducao, None, None))  
    
def atualizar_mensagens():
    for autor, texto, grafico, imagem in st.session_state.historico:
        with st.chat_message(autor):
            if grafico:
                fig = gc.processar_grafico(grafico)
                st.plotly_chart(fig, width="stretch")
            if texto:
                st.markdown(conv.formatar_latex(texto))
            if imagem:
                st.image(imagem, caption="Imagem enviada", width=250)

def adcionar_mensagem(tipo : str, conteudo : str):
    if (tipo != "user") and (tipo != "assistant"):
        raise ValueError("O tipo de mensagem deve ser 'user' ou 'assistant'.")

    if conteudo is None or conteudo.strip() == "":
        return  # Não adiciona mensagens vazias
    
    st.session_state.historico.append((tipo, conteudo, None, None))

    with st.chat_message(tipo):
        st.markdown(conv.formatar_latex(conteudo))

'''
def adcionar_imagem(tipo : str, imagem):
    if (tipo != "user"):
        raise ValueError("O tipo de mensagem deve ser 'user'.")

    if imagem is None:
        return  # Não adiciona imagens vazias
    
    st.session_state.historico.append((tipo, None, None, imagem.getvalue()))

    with st.chat_message(tipo):
        pass
        #st.image(imagem, caption="Imagem enviada", width=250)
'''

def adicionar_mensagem_usuario(texto, imagem=None):

    if not texto and imagem is None:
        return

    imagem_bytes = imagem.getvalue() if imagem else None

    st.session_state.historico.append(("user", texto, None, imagem_bytes))

    with st.chat_message("user"):

        if imagem_bytes:
            st.image( imagem_bytes, caption="Imagem enviada", width=250)

        if texto:
            st.markdown(conv.formatar_latex(texto))

'''
def adcionar_grafico(tipo : str, grafico):
    if (tipo != "assistant"):
        raise ValueError("O tipo de mensagem deve ser 'assistant'.")
    
    if grafico is None or not isinstance(grafico, dict) or not grafico:
        return  # Não adiciona gráficos vazios

    st.session_state.historico.append((tipo, None, grafico, None))

    with st.chat_message(tipo):
        fig = gc.processar_pedido(grafico)
        st.plotly_chart(fig, use_container_width=True)
'''

def adicionar_grafico(tipo: str, grafico):
    print(grafico)
    if tipo != "assistant":
        raise ValueError("O tipo de mensagem deve ser 'assistant'.")

    if grafico is None or not isinstance(grafico, str) or not grafico.strip():
        return

    st.session_state.historico.append(
        (tipo, None, grafico, None)
    )

    with st.chat_message(tipo):
        try:
            fig = gc.processar_grafico(grafico)

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        except Exception as e:
            st.error(f"Não foi possível gerar o gráfico: {e}")

def montar_payload(prompt_data) -> list[dict]:
    mensagem_payload = [ # Cria a primeira instrucao
        {
            "role":"system", 
            "content": SYSTEM_PROMPT
        }
    ] 

    for autor, texto, grafico, imagem in st.session_state.historico:
        role = "assistant" if autor == "assistant" else "user"

        mensagem = {
            "role": role
        }

        if texto is not None:
            mensagem["content"] = texto

        if imagem is not None:
            mensagem["images"] = [
                conv.bytes_para_base64(imagem)
            ]

        mensagem_payload.append(mensagem)


    return mensagem_payload

def montar_payload_inicial() -> list[dict]:
    texto_introducao = lv.ler_arquivo("introducao")

    instrucao_state = st.session_state.get("instrucao")
        
    if instrucao_state and instrucao_state.strip():
        topico_nome = instrucao_state.upper()
        prompt_usuario = f"{texto_introducao}\n\nTópico selecionado: {topico_nome}"
    else:
        prompt_usuario = texto_introducao
    
    payload_inicial = [ # Padrao modelo
        {"role": "user", "content": prompt_usuario},
    ]

    return payload_inicial