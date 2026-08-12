import requests
import streamlit as st
import os

colab_url = os.getenv("COLAB_URL", "")

if not colab_url:
    try:
        colab_url = st.secrets.get("COLAB_URL", "")
    except Exception: # Se secrets.toml não existir localmente, ignora o erro
        colab_url = ""

colab_url = colab_url.rstrip("/")

def requisitar_tutor(mensagem):
    if not colab_url:
        st.error("⚠️ URL do Colab não configurada! Verifique o arquivo .env no computador ou Secrets no Streamlit Cloud.")
        st.stop()

    endpoint = f"{colab_url}/api/chat" # Modelo como o Ollama
    
    payload = { # JSON exigido pelo Ollama
        "model": "qwen2.5vl:3b",
        "messages": mensagem, 
        "stream": False # Recebe mensagem inteira
    }

    # Cabeçalho para burlar a tela de aviso do Ngrok
    headers = {
        "ngrok-skip-browser-warning": "true",
        "Content-Type": "application/json"
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
