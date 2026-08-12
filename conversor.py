import re
import base64

def formatar_latex(texto: str) -> str:
    # Converte \[ ... \] (bloco) para $$ ... $$
    texto = re.sub(r'\\\[(.*?)\\\]', r'$$\1$$', texto, flags=re.DOTALL)
    # Converte \( ... \) (inline) para $ ... $
    texto = re.sub(r'\\\((.*?)\\\)', r'$\1$', texto, flags=re.DOTALL)
    return texto

# Função para converter imagem para Base64
def imagem_para_base64(uploaded_file):
    return base64.b64encode(uploaded_file.getvalue()).decode("utf-8")
