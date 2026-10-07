import re
import base64

SUPERSCRIPT_MAP = {
    '0': '⁰', '1': '¹', '2': '²', '3': '³', '4': '⁴',
    '5': '⁵', '6': '⁶', '7': '⁷', '8': '⁸', '9': '⁹',
    '+': '⁺', '-': '⁻', '=': '⁼', '(': '⁽', ')': '⁾',
    'n': 'ⁿ', 'i': 'ⁱ', 'x': 'ˣ', 'y': 'ʸ', 't': 'ᵗ', 'k': 'ᵏ', 'm': 'ᵐ'
}

def to_superscript(s: str) -> str:
    return ''.join(SUPERSCRIPT_MAP.get(c, c) for c in s)

def formatar_latex(texto: str) -> str:
    if not texto:
        return ''

    # 1. Converte \[ ... \] (bloco) para $$ ... $$
    texto = re.sub(r'\\\[(.*?)\\\]', lambda m: f"$${m.group(1)}$$", texto, flags=re.DOTALL)
    # Converte \( ... \) (inline) para $ ... $
    texto = re.sub(r'\\\((.*?)\\\)', lambda m: f"${m.group(1)}$", texto, flags=re.DOTALL)

    def repl_match(m):
        base = m.group(1)
        exp_raw = m.group(2)
        exp_clean = exp_raw.strip('()')
        if all(c in SUPERSCRIPT_MAP for c in exp_clean):
            return base + to_superscript(exp_clean)
        return f"{base}^{{{exp_clean}}}"

    # 2. Converte x**2, x**3, (x+1)**2 para sobrescrito x², x³, (x+1)²
    texto = re.sub(r'([a-zA-Z0-9_\)])\*\*(\-?[0-9a-zA-Z]+|\([0-9a-zA-Z\+\-]+\))', repl_match, texto)

    # 3. Converte x"2, x"3 (erro comum de digitação em teclados ABNT para ^), x^2, x^3, (x+1)^2
    texto = re.sub(r'([a-zA-Z0-9_\)])[\"\^](\-?[0-9a-zA-Z]+|\([0-9a-zA-Z\+\-]+\))', repl_match, texto)

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