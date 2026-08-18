def ler_arquivo(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "Você é um tutor de matemática didático e paciente."