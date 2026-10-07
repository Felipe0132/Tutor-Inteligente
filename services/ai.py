import requests
import streamlit as st
import os
import utils.conversor as conv
from dotenv import load_dotenv
import json
from groq import Groq
import re

load_dotenv()

# Puxando variáveis (se existirem)
colab_url = os.getenv("COLAB_URL", "")
groq_api_key = os.getenv("GROQ_API_KEY", "")
ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
ollama_model = os.getenv("OLLAMA_MODEL", "qwen2.5")

# Backend configurável: "local", "groq" ou "colab"
BACKEND = os.getenv("BACKEND", "local")

# Aviso no terminal sem caracteres especiais para evitar erros de encoding no Windows
print(f"[IA] O sistema foi iniciado usando o motor: {BACKEND.upper()} (Modelo: {ollama_model})")

def obter_backend():
    return st.session_state.get("backend_selecionado", os.getenv("BACKEND", "local"))

def requisitar_tutor_stream(mensagem):
    """
    Retorna um gerador que produz chunks de texto em tempo real (Streaming).
    """
    backend = obter_backend()
    if backend == "colab":
        yield from requisitar_tutor_colab_stream(mensagem)
    elif backend == "groq":
        yield from requisitar_tutor_groq_stream(mensagem)
    elif backend == "local":
        yield from requisitar_tutor_local_stream(mensagem)
    else:
        yield "Nenhum backend configurado!"

def requisitar_tutor(mensagem) -> str:
    """
    Consome o gerador de streaming e retorna o texto completo.
    """
    chunks = []
    for chunk in requisitar_tutor_stream(mensagem):
        chunks.append(chunk)
    return "".join(chunks)

def requisitar_tutor_local_stream(mensagem):
    endpoint = f"{ollama_url}/api/chat"
    
    messages_payload = []
    tem_imagem = False
    for msg in mensagem:
        nova_msg = {
            "role": msg["role"],
            "content": msg.get("content", "")
        }
        
        if msg.get("images"):
            tem_imagem = True
            nova_msg["images"] = msg.get("images")
            
        messages_payload.append(nova_msg)

    if tem_imagem and "vl" not in ollama_model.lower():
        st.warning(
            f"O modelo local configurado ('{ollama_model}') é somente texto. "
            "Para analisar imagens de exercícios, configure um modelo de visão (ex: 'qwen2.5-vl') "
            "ou utilize o motor GROQ no arquivo .env."
        )
        
    payload = {
        "model": ollama_model,
        "messages": messages_payload,
        "stream": True,
        "options": {
            "num_thread": 4,
            "num_ctx": 2048,
            "temperature": 0.3
        },
        "keep_alive": "30m"
    }

    try:
        resposta = requests.post(endpoint, json=payload, stream=True, timeout=180)

        if resposta.status_code == 200:
            for line in resposta.iter_lines(decode_unicode=True):
                if line:
                    try:
                        data = json.loads(line)
                        chunk = data.get("message", {}).get("content", "")
                        if chunk:
                            yield chunk
                    except Exception:
                        continue
            return

        yield f"Erro no servidor Ollama ({resposta.status_code}): {resposta.text}"

    except requests.exceptions.RequestException as e:
        yield f"\n\n**Erro de conexão com o Ollama local:** {e}\n\nO Ollama está instalado e em execução?"

def requisitar_tutor_colab_stream(mensagem):
    if not colab_url:
        yield "URL do Colab não configurada!"
        return

    endpoint = f"{colab_url}/api/chat"

    payload = {
        "model": "qwen2.5vl:3b",
        "messages": mensagem,
        "stream": True
    }

    headers = {
        "ngrok-skip-browser-warning": "true",
        "Content-Type": "application/json"
    }

    try:
        resposta = requests.post(endpoint, json=payload, headers=headers, stream=True, timeout=180)

        if resposta.status_code == 200:
            for line in resposta.iter_lines(decode_unicode=True):
                if line:
                    try:
                        data = json.loads(line)
                        chunk = data.get("message", {}).get("content", "")
                        if chunk:
                            yield chunk
                    except Exception:
                        continue
            return

        yield f"Erro no servidor Colab: {resposta.status_code}"

    except requests.exceptions.RequestException as e:
        yield f"\n\n**Erro de conexão com o Colab:** {e}"

def requisitar_tutor_groq_stream(mensagem):
    if not groq_api_key:
        yield "GROQ_API_KEY não configurada no arquivo .env!"
        return

    client = Groq(api_key=groq_api_key)
    messages_payload = []

    for msg in mensagem:
        role = msg["role"]
        content = msg.get("content", "")
        images = msg.get("images")

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
        else:
            messages_payload.append({
                "role": role,
                "content": content
            })

    try:
        model_name = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
        response = client.chat.completions.create(
            model=model_name,
            messages=messages_payload,
            temperature=0.3,
            max_completion_tokens=2048,
            stream=True
        )
        for chunk in response:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    except Exception as e:
        yield f"\n\n**Erro ao se comunicar com a Groq API:** {e}"

def verificar_grafico(resposta: str) -> bool:
    return bool(
        re.search(
            r"<grafico>\s*.*?\s*</grafico>",
            resposta,
            re.DOTALL | re.IGNORECASE
        )
    )

def extrair_grafico(resposta: str) -> tuple[str | None, str]:
    padrao = r"<grafico>\s*(.*?)\s*</grafico>"

    match = re.search(
        padrao,
        resposta,
        re.DOTALL | re.IGNORECASE
    )

    if not match:
        return None, resposta.strip()

    conteudo = match.group(1).strip()

    # Remove markdown acidental:
    conteudo = re.sub(
        r"^```(?:json)?\s*",
        "",
        conteudo,
        flags=re.IGNORECASE
    )

    conteudo = re.sub(
        r"\s*```$",
        "",
        conteudo
    )

    conteudo = conteudo.strip()

    # Reconstrói o bloco para o processador de gráficos
    grafico = f"<grafico>\n{conteudo}\n</grafico>"

    texto = (
        resposta[:match.start()]
        + resposta[match.end():]
    ).strip()

    return grafico, texto