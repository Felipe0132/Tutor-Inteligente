import streamlit as st
import json
from dotenv import load_dotenv
import conversor as conv
import leitor_arquivo as lv
import requisicao_tutor as tutor
import graficos as gc

load_dotenv()

SYSTEM_PROMPT = lv.ler_arquivo("contexto.txt")

st.write('Tutor Inteligente')
st.write("Tire suas dúvidas de matemática e resolva problemas passo a passo!")

if "historico" not in st.session_state:
    st.session_state.historico = []

    if st.session_state.get("instrucao") and st.session_state.instrucao != " ":
        topico_nome = st.session_state.instrucao.upper()
        INTRODUCAO_PROMPT = lv.ler_arquivo("introducao") + topico_nome
    else:
        INTRODUCAO_PROMPT = lv.ler_arquivo("introducao")

    payload_inicial = [ # Padrao modelo
        {"role": "user", "content": INTRODUCAO_PROMPT},
    ]

    with st.spinner("O tutor está se preparando..."):
        introducao = tutor.requisitar_tutor(payload_inicial)
        st.session_state.historico.append(("assistant", introducao, None))

for autor, texto, grafico in st.session_state.historico:
    with st.chat_message(autor):
        if grafico:
            fig = gc.renderizar_grafico_matematico(grafico)
            st.plotly_chart(fig, use_container_width=True)
        if texto:
            st.markdown(conv.formatar_latex(texto))

prompt_data = st.chat_input("Digite sua duvida ou o exercicio de matematica...", accept_file=True, file_type=["png", "jpg", "jpeg"])

if prompt_data and prompt_data.text: # Se existem mensagem e se tiver texto
    prompt = prompt_data.text
    imagem_carregada = prompt_data.files[0] if prompt_data.files else None

    if imagem_carregada:
        st.image(imagem_carregada, caption="Imagem enviada", width=250)

    st.session_state.historico.append(("user", prompt, None))

    with st.chat_message("user"):
        st.markdown(conv.formatar_latex(prompt))

    mensagem_payload = [{"role":"system", "content": SYSTEM_PROMPT}] # Cria a primeira instrucao

    for autor, texto, grafico in st.session_state.historico:
        role = "assistant" if autor == "assistant" else "user"
        mensagem_payload.append({"role": role, "content": texto})

    
    if imagem_carregada:
        img_b64 = conv.imagem_para_base64(imagem_carregada)# Adiciona a imagem em Base64
        mensagem_payload[-1]["images"] = [img_b64] # Coloca ela como ultima mensagem, falando que eh uma imagem ligado a ultima pergunta
 
    with st.spinner("O tutor está analisando sua pergunta..."):
        resposta_tutor = tutor.requisitar_tutor(mensagem_payload)
        if "<grafico>" in resposta_tutor:
            antes, resto = resposta_tutor.split("<grafico>", 1) # Quebra uma vez em <grafico>

            json_grafico, depois = resto.split("</grafico>")
            texto = (antes.strip() + " " + depois.strip()).strip()

            dados_grafico = json.loads(json_grafico.strip())

        else:
            texto = resposta_tutor.strip()
            dados_grafico = None

    st.session_state.historico.append(("assistant", texto, dados_grafico))


    with st.chat_message("assistant"):
        if dados_grafico:
            fig = gc.renderizar_grafico_matematico(dados_grafico)
            st.plotly_chart(fig, use_container_width=True)
        if texto:
            st.markdown(conv.formatar_latex(texto))