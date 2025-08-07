import os
import re
import pandas as pd

# Lista para armazenar os comprovantes válidos que serão exportados
comprovantes_validos = []

def extrair_codigo_parceiro(usuario_raw: str) -> str:
    """
    Extrai somente os números iniciais do campo 'Usuário', ignorando sufixos como 'master', '@LEV', etc.
    Ex: '013414master' → '013414'
    """
    match = re.match(r"(\d+)", usuario_raw)
    return match.group(1) if match else ""

def adicionar_comprovante_para_planilha(data_pix: str, valor: str, detalhes: str, codigo: str):
    """
    Adiciona os dados de um comprovante válido à lista para exportação.
    """
    comprovantes_validos.append({
        "data": data_pix,
        "valor": valor,
        "detalhes": detalhes,
        "codigo": codigo
    })

def salvar_planilha_excel(nome_arquivo="comprovantes_validos.xlsx"):
    """
    Salva os dados dos comprovantes válidos em uma planilha Excel.
    """
    if not comprovantes_validos:
        print("⚠️ Nenhum comprovante válido para exportar.")
        return

    df = pd.DataFrame(comprovantes_validos, columns=["data", "valor", "detalhes", "codigo"])
    caminho = os.path.join(os.getcwd(), nome_arquivo)
    df.to_excel(caminho, index=False)
    print(f"📊 Planilha salva com sucesso em: {caminho}")
