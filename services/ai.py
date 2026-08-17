import requests
import streamlit as st
import os
import utils.conversor as conv
from dotenv import load_dotenv
import json
from groq import Groq

load_dotenv()

colab_url = os.getenv("COLAB_URL", "")
groq_api_key = os.getenv("GROQ_API_KEY", "")

back = "colab"

if not colab_url:
    try:
        colab_url = st.secrets.get("COLAB_URL", "")
    except Exception:
        colab_url = ""
    back = "colab"

if not groq_api_key:
    try:
        groq_api_key = st.secrets.get("GROQ_API_KEY", "")
    except Exception:
        groq_api_key = ""
    back = "groq"

BACKEND = back

def requisitar_tutor(mensagem):
    if BACKEND == "colab":
        return requisitar_tutor_colab(mensagem)

    elif BACKEND == "groq":
        return requisitar_tutor_groq(mensagem)

def requisitar_tutor_colab(mensagem) -> str:

    if not colab_url:
        st.error("URL do Colab não configurada!")
        st.stop()

    endpoint = f"{colab_url}/api/chat"

    payload = {
        "model": "qwen2.5vl:3b",
        "messages": mensagem,
        "stream": False
    }

    headers = {
        "ngrok-skip-browser-warning": "true",
        "Content-Type": "application/json"
    }

    st.session_state.tutor_ocupado = True

    try:
        resposta = requests.post(endpoint, json=payload, headers=headers, timeout=120)

        if resposta.status_code == 200:
            return resposta.json()["message"]["content"]

        st.error(
            f"Erro no servidor: {resposta.status_code}"
        )
        st.code(resposta.text)
        st.stop()

    except requests.exceptions.RequestException as e:
        st.error(f"Erro de conexão: {e}")
        st.stop()

    finally:
        st.session_state.tutor_ocupado = False


def requisitar_tutor_groq(mensagem):

    if not groq_api_key:
        st.error("GROQ_API_KEY não configurada!")
        st.stop()

    client = Groq(api_key=groq_api_key)

    messages_payload = []

    for msg in mensagem:

        role = msg["role"]
        content = msg.get("content")
        images = msg.get("images")

        # Mensagem com imagem
        if images:

            multimodal_content = []

            if content:
                multimodal_content.append({
                    "type": "text",
                    "text": content
                })

            for img in images:

                mime = conv.detectar_mime_base64(img)

                multimodal_content.append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:{mime};base64,{img}"
                    }
                })

            messages_payload.append({
                "role": role,
                "content": multimodal_content
            })

        # Mensagem somente texto
        else:

            messages_payload.append({
                "role": role,
                "content": content
            })

    try:

        response = client.chat.completions.create(
            model="qwen/qwen3.6-27b",
            messages=messages_payload,
            temperature=0.3,
            max_completion_tokens=2048,
            stream=False,
            reasoning_format="hidden"

        )
        
        return response.choices[0].message.content

    except Exception as e:
        st.error(
            f"Erro ao se comunicar com a Groq API: {e}"
        )
        st.stop()

def verificar_grafico(resposta : str) -> bool:
    return "<grafico>" in resposta


def extrair_grafico(resposta : str) -> tuple[dict, str]:
    antes, resto = resposta.split("<grafico>", 1)
    json_grafico, depois = resto.split("</grafico>")
    return json.loads(json_grafico.strip()), (antes.strip() + " " + depois.strip()).strip()