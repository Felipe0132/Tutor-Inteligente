import streamlit as st
import base64
import requests
import os
from dotenv import load_dotenv

load_dotenv()

colab_url = os.getenv("COLAB_URL", "")

st.write('Tutor Inteligente')
st.write("Tire suas dúvidas de matemática e resolva problemas passo a passo!")

if not colab_url:
    try:
        colab_url = st.secrets.get("COLAB_URL", "")
    except Exception: # Se secrets.toml não existir localmente, ignora o erro
        colab_url = ""

colab_url = colab_url.rstrip("/")

# Função para converter imagem para Base64
def imagem_para_base64(uploaded_file):
    return base64.b64encode(uploaded_file.getvalue()).decode("utf-8")

try:
    with open("contexto.txt", "r", encoding="utf-8") as f:
        SYSTEM_PROMPT = f.read()
except FileNotFoundError:
    SYSTEM_PROMPT = "Você é um tutor de matemática didático e paciente."

if st.session_state.get("instrucao") and st.session_state.instrucao != " ":
    topico_instrucao = st.session_state.instrucao
    SYSTEM_PROMPT += f"\n\nO aluno selecionou o tópico de estudo: {topico_instrucao.upper()}."

def requisitar_tutor(mensagem):
    if not colab_url:
        st.error("⚠️ URL do Colab não configurada! Verifique o arquivo .env no computador ou Secrets no Streamlit Cloud.")
        st.stop()

    endpoint = f"{colab_url}/api/chat" # Modelo como o Ollama
    
    payload = { # JSON exigido pelo Ollama
        "model": "llava",
        "messages": mensagem, 
        "stream": False # Recebe mensagem inteira
    }

    # Cabeçalho para burlar a tela de aviso do Ngrok
    headers = {
        "ngrok-skip-browser-warning": "true",
        "User-Agent": "StreamlitApp",
        "Content-Type": "application/json",
    }

    try:
        resposta = requests.post(endpoint, json=payload, headers=headers, timeout=120)

        if resposta.status_code == 200:
            return resposta.json()["message"]["content"] # Retorna a mensagem da IA
        else:
            st.error(f"Erro no servidor (Código {resposta.status_code}). Verifique o Colab.")
            st.code(f"Headers: {dict(resposta.headers)}\n\nBody: '{resposta.text}'")
            st.stop()
    except requests.exceptions.RequestException as e:
        st.error(f"Erro de conexão com a URL do Ngrok. O notebook do Colab está ativo? Detalhes: {e}")
        st.stop()

if "historico" not in st.session_state:
    st.session_state.historico = []

    if st.session_state.get("instrucao") and st.session_state.instrucao != " ":
        topico_nome = st.session_state.instrucao.upper()
        instrucao_inicial = (
            f"Apresente-se rapidamente como Tutor Inteligente, mencione que"
            f" vamos estudar o tema {topico_nome} e liste 3 opções de tópicos"
            " ou problemas comuns sobre esse assunto para eu escolher."
        )
    else:
        instrucao_inicial = (
            "Apresente-se rapidamente como Tutor Inteligente de Matemática, dê"
            " as boas-vindas e pergunte qual assunto de matemática posso te"
            " ajudar a estudar hoje."
        )

    payload_inicial = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": instrucao_inicial},
    ]

    with st.spinner("O tutor está se preparando..."):
        saudacao_ia = requisitar_tutor(payload_inicial)
        st.session_state.historico.append(("assistant", saudacao_ia))

for autor, texto in st.session_state.historico:
    with st.chat_message(autor):
        st.markdown(texto)

imagem_carregada = st.file_uploader("Envie uma foto do problema (opcional)", type=["png", "jpg", "jpeg"])

if prompt := st.chat_input("Digite sua duvida ou o exercicio de matematica..."): # Testa e retorna prompt
    if imagem_carregada:
        st.image(imagem_carregada, caption="Imagem enviada", width=250)

    st.session_state.historico.append(("user", prompt))

    with st.chat_message("user"):
        st.markdown(prompt)

    mensagem_payload = [{"role":"system", "content": SYSTEM_PROMPT}] # Cria a primeira instrucao

    for autor, texto in st.session_state.historico:
        role = "assistant" if autor == "assistant" else "user"
        # Faz o sistema reconhecer de quem eh a mensagem
        mensagem_payload.append({"role":role, "content":texto})

    # Adiciona a imagem Base64 na ÚLTIMA mensagem do usuário (se anexada)
    if imagem_carregada:
        img_b64 = imagem_para_base64(imagem_carregada)
        mensagem_payload[-1]["images"] = [img_b64]

    with st.spinner("O tutor está analisando sua pergunta..."):
        resposta_tutor = requisitar_tutor(mensagem_payload)

    st.session_state.historico.append(("assistant", resposta_tutor))
    with st.chat_message("assistant"):
        st.markdown(resposta_tutor)