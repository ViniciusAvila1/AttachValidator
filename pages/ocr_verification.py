from PIL import Image, ImageFile
from pdf2image import convert_from_bytes
import pytesseract
import io
import fitz  # PyMuPDF
import re
from datetime import datetime, timedelta

ImageFile.LOAD_TRUNCATED_IMAGES = True  # mantém o download de arquivos truncados

def extrair_texto_imagem(imagem_bytes):
    """
    Extrai texto de uma imagem em bytes usando OCR (Tesseract).
    """
    try:
        imagem = Image.open(io.BytesIO(imagem_bytes))
        imagem.load()
        texto = pytesseract.image_to_string(imagem, lang='por')
    except Exception as e:
        raise Exception(f"Erro ao abrir imagem: {e}")

    return texto

def extrair_texto_pdf(pdf_bytes):
    """
    Extrai texto de um PDF. Se não encontrar texto selecionável, aplica OCR em cada página.
    """
    texto = ""
    with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
        for page in doc:
            text_page = page.get_text()
            if text_page.strip():
                texto += text_page
            else:
                # Se a página não tiver texto extraível, usa OCR
                pix = page.get_pixmap(dpi=300)
                img_bytes = pix.tobytes("png")
                imagem = Image.open(io.BytesIO(img_bytes))
                texto += pytesseract.image_to_string(imagem, lang='por')
    return texto

def data_esta_nos_ultimos_dias(texto, dias=5):
    """
    Verifica se há alguma data no texto que esteja nos últimos '5' dias.
    Aceita formatos numéricos ou com mês abreviado por extenso.
    """
    hoje = datetime.now()
    limite = hoje - timedelta(days=dias)
    
    datas_encontradas = []

    # Mapeamento de meses em português (abreviado e completo)
    meses_pt = {
        "jan": 1, "fev": 2, "mar": 3, "abr": 4, "mai": 5, "jun": 6,
        "jul": 7, "ago": 8, "set": 9, "out": 10, "nov": 11, "dez": 12
    }

    # 🟢 Lista de padrões para capturar diferentes formatos de data
    padroes = [
        r'\b(\d{1,2})[\/\-](\d{1,2})[\/\-](\d{2,4})\b', # 03/07/2025 ou 03-07-25
        r'\b(\d{1,2})[\/\-]([a-zç]{3,9})[\/\-](\d{2,4})\b', # 03/jul/25 ou 03-julho-2025
        r'\b(\d{1,2})[\s\-]?de[\s\-]?([a-zç]{3,9})[\s\-]?de[\s\-]?(\d{2,4})\b', # 03 de julho de 2025
    ]

    texto = texto.lower()

    for padrao in padroes:
        for match in re.findall(padrao, texto):
            try:
                dia, mes, ano = match

                # Se mês for texto (ex: jul ou julho), converte para número
                if mes.isalpha():
                    mes = meses_pt.get(mes[:3])
                    if not mes:
                        continue
                else:
                    mes = int(mes)

                dia = int(dia)
                ano = int(ano)
                if ano < 100:  # Corrige anos com 2 dígitos (04/07/25 para 04/07/2025)
                    ano += 2000

                data_encontrada = datetime(ano, mes, dia)
                datas_encontradas.append(data_encontrada)

            except Exception:
                continue

    for data in datas_encontradas:
        if limite.date() <= data.date() <= hoje.date():
            return True

    return False


def validar_conteudo_anexo(nome, caminho_arquivo):
    """
    Valida se o conteúdo do arquivo possui um comprovante com:
    - Palavras-chave
    - Valor de R$30,00
    - Nome da empresa ou CNPJ
    - Data dentro dos últimos 5 dias
    """
    try:
        with open(caminho_arquivo, "rb") as f:
            conteudo = f.read()

        # extração do texto do conteúdo (PDF ou imagem)
        if nome.lower().endswith(".pdf"):
            texto = extrair_texto_pdf(conteudo)
        else:
            texto = extrair_texto_imagem(conteudo)

        texto = texto.lower()

        # filtros de validação
        palavras_comprovante = ["comprovante", "pagamento", "transferência", "pix"]
        padrao_valor = re.compile(r"(r\$)?\s*30[,\.]00")
        padrao_cnpj = re.compile(r"13[\.\s]?054[\.\s]?592[\.\s]?\/?0001[\-\s]?76")

        tem_palavra_chave = any(p in texto for p in palavras_comprovante)
        tem_valor = bool(padrao_valor.search(texto))
        tem_cnpj = bool(padrao_cnpj.search(texto))
        tem_nome_empresa = "lev" in texto or "lev negócios" in texto
        tem_data_valida = data_esta_nos_ultimos_dias(texto)

        exibir_resultado_validacao(
            nome,
            tem_palavra_chave,
            tem_valor,
            tem_cnpj,
            tem_nome_empresa,
            tem_data_valida,
            comprovante_valido=tem_palavra_chave and tem_valor and (tem_cnpj or tem_nome_empresa) and tem_data_valida
        )

    except Exception as e:
        print(f"❌ {nome}: erro ao processar OCR: {e}")


def exibir_resultado_validacao(nome, tem_palavra_chave, tem_valor, tem_cnpj, tem_nome_empresa, tem_data_valida, comprovante_valido):
    """
    Exibe o resultado da validação do comprovante de forma padronizada.
    """
    if comprovante_valido:
        print(f"✅ {nome}: COMPROVANTE VÁLIDO ENCONTRADO.")
    else:
        print(f"❌ {nome}: NÃO FOI IDENTIFICADO COMPROVANTE VÁLIDO.")
        print("🔍 Detalhes:")
    print(f"    ✔️ Palavras-chave: {'Sim' if tem_palavra_chave else 'Não'}")
    print(f"    ✔️ Valor R$30,00: {'Sim' if tem_valor else 'Não'}")
    print(f"    ✔️ CNPJ: {'Sim' if tem_cnpj else 'Não'}")
    print(f"    ✔️ Nome da empresa: {'Sim' if tem_nome_empresa else 'Não'}")
    print(f"    ✔️ Data válida (últimos 5 dias): {'Sim' if tem_data_valida else 'Não'}")
