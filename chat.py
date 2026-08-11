import streamlit as st
import base64
import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

colab_url = os.getenv("COLAB_URL", "")

st.write('Tutor Inteligente')
st.write("Tire suas dúvidas de matemática e resolva problemas passo a passo!")

groq_api_key = os.getenv("GROQ_API_KEY", "")
if not groq_api_key:
    try:
        groq_api_key = st.secrets.get("GROQ_API_KEY", "")
    except Exception:
        groq_api_key = ""

if not groq_api_key:
    st.error("Chave 'GROQ_API_KEY' não configurada! Verifique as Secrets no Streamlit Cloud.")
    st.stop()

client = Groq(api_key=groq_api_key)

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
    messages_payload = [{'role': 'system', 'content': SYSTEM_PROMPT}]

    for msg in mensagem:
        role = msg['role']
        content = msg['content']
        img_b64 = msg.get('image_b64')
        if img_b64:
            user_content = [
                {'type': 'text', 'text': content if content else "Analise esta imagem."},
                {'type': 'image_url', 'image_url':{'url': f'data:image/jpeg;base64,{img_b64}'}}
            ] # Padrao das imagens eh ler um texto e depois a url dela, passando que eh uma url e depois a url
            messages_payload.append({"role":role, "content":user_content}) # contente seria tudo
        else:
            messages_payload.append({"role": role, "content": content})

    try:
        # Chamada oficial da API
        response = client.chat.completions.create(
            model="qwen/qwen3.6-27b",
            messages=messages_payload,
            temperature=0.3,
            max_tokens=1024,
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Erro ao se comunicar com a Groq API: {e}")
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

    primeira_msg = [{"role": "user", "content": instrucao_inicial}]

    with st.spinner("O tutor está se preparando..."):
        saudacao_ia = requisitar_tutor(primeira_msg)
        st.session_state.historico.append({"role": "assistant", "content": saudacao_ia})

for msg in st.session_state.historico:  
    with st.chat_message(msg['role']):
        st.markdown(msg['content'])

imagem_carregada = st.file_uploader("Envie uma foto do problema (opcional)", type=["png", "jpg", "jpeg"])

if prompt := st.chat_input("Digite sua duvida ou o exercicio de matematica..."): # Testa e retorna prompt
    if imagem_carregada:
        st.image(imagem_carregada, caption="Imagem enviada", width=250)
        img_b64 = imagem_para_base64(imagem_carregada)
    else:
        img_b64 = None

    with st.chat_message("user"):
        st.markdown(prompt)

    st.session_state.historico.append({
        "role": "user", 
        "content": prompt, 
        "image_b64": img_b64 # Caso tenha
    })

    with st.chat_message("assistant"):
        with st.spinner("O tutor está analisando sua pergunta..."):
            resposta_tutor = requisitar_tutor(st.session_state.historico)
            st.markdown(resposta_tutor)

    st.session_state.historico.append({"role": "assistant", "content": resposta_tutor})