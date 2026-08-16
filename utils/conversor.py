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

def bytes_para_base64(imagem_bytes: bytes) -> str:
    return base64.b64encode(imagem_bytes).decode("utf-8")

def detectar_mime_base64(img_b64: str) -> str:
    if img_b64.startswith("iVBORw0KGgo"):
        return "image/png"

    if img_b64.startswith("/9j/"):
        return "image/jpeg"

    raise ValueError("Formato de imagem não suportado.")