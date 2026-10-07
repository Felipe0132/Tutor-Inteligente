import streamlit as st
import json
from dotenv import load_dotenv
import utils.conversor as conv
import utils.leitor_arquivo as lv
import utils.graph as gc
import services.ai as ai

def obter_system_prompt():
    return lv.ler_arquivo("contexto.txt")

def inicializar_mensagens():
    if "tutor_ocupado" not in st.session_state:
        st.session_state.tutor_ocupado = False

    if "historico" not in st.session_state:
        st.session_state.historico = []

        with st.chat_message("assistant"):
            area = st.empty()
            with st.spinner("O tutor está se preparando..."):
                intro = area.write_stream(ai.requisitar_tutor_stream(montar_payload_inicial()))
            area.markdown(conv.formatar_latex(intro))

        st.session_state.historico.append(("assistant", intro, None, None))

def atualizar_mensagens():
    for autor, texto, grafico, imagem in st.session_state.historico:
        with st.chat_message(autor):
            if imagem:
                st.image(imagem, caption="Imagem enviada", width=250)
            if texto:
                st.markdown(conv.formatar_latex(texto))
            if grafico:
                try:
                    fig = gc.processar_grafico(grafico)
                    st.plotly_chart(fig, width="stretch")
                except Exception as e:
                    st.error(f"Erro ao renderizar gráfico: {e}")

def adicionar_mensagem(tipo: str, conteudo: str):
    if tipo not in ("user", "assistant"):
        raise ValueError("O tipo de mensagem deve ser 'user' ou 'assistant'.")

    if not conteudo or not conteudo.strip():
        return

    st.session_state.historico.append((tipo, conteudo, None, None))

# Alias de compatibilidade com o código anterior
adcionar_mensagem = adicionar_mensagem

def adicionar_mensagem_usuario(texto, imagem=None):
    if not texto and imagem is None:
        return

    imagem_bytes = imagem.getvalue() if imagem else None
    st.session_state.historico.append(("user", texto, None, imagem_bytes))

    with st.chat_message("user"):
        if imagem_bytes:
            st.image(imagem_bytes, caption="Imagem enviada", width=250)
        if texto:
            st.markdown(conv.formatar_latex(texto))

def adicionar_interacao_assistente(texto: str, grafico: str | None = None):
    """
    Adiciona a resposta do assistente (texto e gráfico opcional) ao histórico.
    """
    if (not texto or not texto.strip()) and not grafico:
        return

    st.session_state.historico.append(("assistant", texto, grafico, None))

def adicionar_grafico(tipo: str, grafico: str):
    if tipo != "assistant":
        raise ValueError("O tipo de mensagem deve ser 'assistant'.")

    if not grafico or not isinstance(grafico, str) or not grafico.strip():
        return

    st.session_state.historico.append((tipo, None, grafico, None))

    with st.chat_message(tipo):
        try:
            fig = gc.processar_grafico(grafico)
            st.plotly_chart(fig, width="stretch")
        except Exception as e:
            st.error(f"Não foi possível gerar o gráfico: {e}")

# Alias de compatibilidade
adcionar_grafico = adicionar_grafico

def montar_payload(prompt_data=None) -> list[dict]:
    mensagem_payload = [
        {
            "role": "system",
            "content": obter_system_prompt()
        }
    ]

    for autor, texto, grafico, imagem in st.session_state.historico:
        role = "assistant" if autor == "assistant" else "user"

        conteudo_partes = []
        if texto:
            conteudo_partes.append(texto)
        if grafico:
            conteudo_partes.append(grafico)

        mensagem = {
            "role": role,
            "content": "\n\n".join(conteudo_partes)
        }

        if imagem is not None:
            mensagem["images"] = [
                conv.bytes_para_base64(imagem)
            ]

        mensagem_payload.append(mensagem)

    return mensagem_payload

def montar_payload_inicial() -> list[dict]:
    texto_introducao = lv.ler_arquivo("introducao.txt")

    instrucao_state = st.session_state.get("instrucao")
    if instrucao_state and instrucao_state.strip():
        if instrucao_state.endswith(".txt"):
            caminho_topico = f"topicos/{instrucao_state}"
            conteudo_topico = lv.ler_arquivo(caminho_topico)
            nome_limpo = instrucao_state.replace(".txt", "").replace("_", " ").title()
            prompt_usuario = texto_introducao.replace("{topico_nome}", nome_limpo)
            if conteudo_topico and "Você é um tutor" not in conteudo_topico:
                prompt_usuario += f"\n\n--- DETALHES DO TÓPICO E CONTEÚDO DA EMENTA ---\n{conteudo_topico}"
        else:
            prompt_usuario = texto_introducao.replace("{topico_nome}", instrucao_state.strip())
    else:
        prompt_usuario = texto_introducao.replace("{topico_nome}", "Geral")

    payload_inicial = [
        {"role": "system", "content": obter_system_prompt()},
        {"role": "user", "content": prompt_usuario},
    ]

    return payload_inicial