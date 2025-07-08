from PIL import Image, ImageFile
from pdf2image import convert_from_bytes
import pytesseract
import io
import fitz  # PyMuPDF
import re
from datetime import datetime
import unicodedata
import locale

# Configura locale para datas em português
locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
ImageFile.LOAD_TRUNCATED_IMAGES = True

def normalizar_texto(texto):
    """
    Remove acentuação e converte para minúsculas.
    """
    return unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('utf-8').lower()

def extrair_texto_imagem(imagem_bytes):
    imagem = Image.open(io.BytesIO(imagem_bytes))
    imagem.load()
    return pytesseract.image_to_string(imagem, lang='por')

def extrair_texto_pdf(pdf_bytes):
    texto = ""
    with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
        for page in doc:
            text_page = page.get_text()
            if text_page.strip():
                texto += text_page
            else:
                pix = page.get_pixmap(dpi=300)
                img_bytes = pix.tobytes("png")
                imagem = Image.open(io.BytesIO(img_bytes))
                texto += pytesseract.image_to_string(imagem, lang='por')
    return texto

def corrigir_texto_para_valor(texto):
    """
    Corrige possíveis falhas do OCR que afetam a leitura do valor.
    """
    return (
        texto.replace("⁰", "0")
             .replace("₀", "0")
             .replace("º", "0")
             .replace("O", "0")
             #.replace("o", "0")  # comentar caso mude no restante do texto
    )
    
def imprimir_detalhes_comprovante(nome, tem_palavras, tem_valor, tem_cnpj, tem_nome_empresa, data_valida, contem_proibidas, comprovante_valido):
            if comprovante_valido:
                print(f"✅ {nome}: COMPROVANTE VÁLIDO ENCONTRADO.")
            else:
                print(f"❌ {nome}: NÃO FOI IDENTIFICADO COMPROVANTE VÁLIDO.")

            print("🔍 Detalhes:")
            print(f"    ✔️ Palavras-chave: {'Sim' if tem_palavras else 'Não'}")
            print(f"    ✔️ Valor R$30,00: {'Sim' if tem_valor else 'Não'}")
            print(f"    ✔️ CNPJ: {'Sim' if tem_cnpj else 'Não'}")
            print(f"    ✔️ Nome da empresa: {'Sim' if tem_nome_empresa else 'Não'}")
            print(f"    ✔️ Data válida (últimos 5 dias): {'Sim' if data_valida else 'Não'}")
            print(f"    ⚠️ Termos proibidos detectados: {'Sim' if contem_proibidas else 'Não'}")

def validar_conteudo_anexo(nome, caminho_arquivo):
    try:
        # lê o conteúdo do arquivo
        with open(caminho_arquivo, "rb") as f:
            conteudo = f.read()

        # extrai o texto via OCR
        if nome.lower().endswith(".pdf"):
            texto = extrair_texto_pdf(conteudo)
        else:
            texto = extrair_texto_imagem(conteudo)

        print("🧾 Trecho do texto OCR extraído:\n", texto[:500], "...\n[Texto truncado]")

        # normaliza texto para facilitar buscas (sem acentos, minúsculas)
        texto_normalizado = normalizar_texto(texto)

        # corrige para capturar o valor mesmo com erros comuns do OCR
        texto_para_valor = corrigir_texto_para_valor(texto_normalizado)
        print("📃 Texto corrigido para valor:", texto_para_valor)

        # palavras-chave obrigatórias (basta 1)
        palavras_chave = ["comprovante", "pagamento", "transferencia", "pix"]
        tem_palavras = any(p in texto_normalizado for p in palavras_chave)

        # verificação do valor (R$ 30,00)
        padrao_valor = re.compile(r"(r\$)?\s*-?\s*3[0oº]{1}[\.,]?[0oº]{2}", re.IGNORECASE)
        match_valor = padrao_valor.search(texto_para_valor)
        tem_valor = bool(match_valor)
        if match_valor:
            print("💰 Valor encontrado (match):", match_valor.group())

        # CNPJ da empresa
        padrao_cnpj = re.compile(r"13[\.\s]?\s*054[\.\s]?\s*592[\.\s\/-]*0001[\-]?\s*76")
        tem_cnpj = bool(padrao_cnpj.search(texto_normalizado))

        # nome da empresa (Lev)
        tem_nome_empresa = "lev" in texto_normalizado

        # data válida (últimos 5 dias)
        texto_sem_virgulas = texto_normalizado.replace(",", "")
        padroes_data = [
            r"\d{2}[\/\-]\d{2}[\/\-]\d{2,4}", # dd/mm/yyyy, dd-mm-yy
            r"\d{1,2}\s*de\s*[a-zç]{3,9}(?:\s*de\s*\d{2,4})?", # dia de mês de ano
            r"\d{1,2}[\/\-][a-zç]{3,9}[\/\-]\d{2,4}", # d/mm/yyyy
            r"\d{1,2}\s+[a-zç]{3,9}\s+\d{2,4}", # d mes yyyy
        ]
        formatos = [
            "%d/%m/%Y", "%d/%m/%y", "%d-%m-%Y", "%d-%m-%y",
            "%d de %B de %Y", "%d de %B", "%d/%b/%Y", "%d/%b/%y",
            "%d-%b-%Y", "%d-%b-%y", "%d %B %Y", "%d %b %Y"
        ]

        data_valida = False
        hoje = datetime.now()

        for padrao in padroes_data:
            datas_encontradas = re.findall(padrao, texto_sem_virgulas)
            for data_txt in datas_encontradas:
                for fmt in formatos:
                    try:
                        data_extraida = datetime.strptime(data_txt.strip(), fmt)

                        # assume o ano atual se não veio no OCR
                        if data_extraida.year == 1900:
                            data_extraida = data_extraida.replace(year=hoje.year)

                        diferenca = (hoje - data_extraida).days
                        if 0 <= diferenca <= 5:
                            data_valida = True
                            break
                    except:
                        continue
                if data_valida:
                    break
            if data_valida:
                break

        # prevenção de falsos positivos (evita contratos)
        texto_limpo = texto_normalizado.replace("\n", " ").strip()
        proibidas = ["contrato", "vinculo", "clicksign", "assinatura", "termo"]
        contem_proibidas = any(p in texto_limpo for p in proibidas)

        # condição final
        comprovante_valido = (
            tem_palavras and tem_valor and data_valida and
            (tem_cnpj or tem_nome_empresa) and not contem_proibidas
        )

        # exibição final
        imprimir_detalhes_comprovante(nome, tem_palavras, tem_valor, tem_cnpj, tem_nome_empresa, data_valida, contem_proibidas, comprovante_valido)

    except Exception as e:
        print(f"❌ {nome}: erro ao processar OCR: {e}")
