from PIL import Image, ImageFile
from pdf2image import convert_from_bytes
import pytesseract
import io
import fitz  # PyMuPDF
import re

ImageFile.LOAD_TRUNCATED_IMAGES = True

def extrair_texto_imagem(imagem_bytes):
    try:
        imagem = Image.open(io.BytesIO(imagem_bytes))
        imagem.load()
        return pytesseract.image_to_string(imagem, lang='por')
    except Exception as e:
        raise Exception(f"Erro ao abrir imagem: {e}")

def extrair_texto_pdf(pdf_bytes):
    texto = ""
    try:
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
    except Exception as e:
        raise Exception(f"Erro ao extrair texto do PDF: {e}")

def validar_conteudo_anexo(nome, caminho_arquivo):
    try:
        with open(caminho_arquivo, "rb") as f:
            conteudo = f.read()

        if nome.lower().endswith(".pdf"):
            texto = extrair_texto_pdf(conteudo)
        else:
            texto = extrair_texto_imagem(conteudo)

        texto = texto.lower()

        # filtros ocr
        palavras_comprovante = ["comprovante", "pagamento", "transferência", "pix"]
        padrao_valor = re.compile(r"(r\$)?\s*30[,\.]00")
        padrao_cnpj = re.compile(r"13[\.\s]?054[\.\s]?592[\.\s]?\/?0001[\-\s]?76")

        # pelo menos 1 das palavra-chave presente
        palavras_encontradas = [p for p in palavras_comprovante if p in texto]
        tem_palavras = len(palavras_encontradas) >= 1
        tem_valor = bool(padrao_valor.search(texto))
        tem_cnpj = bool(padrao_cnpj.search(texto))
        tem_nome_empresa = "lev" in texto or "lev negocios" in texto

        if tem_palavras and tem_valor and (tem_cnpj or tem_nome_empresa):
            print(f"✅ {nome}: COMPROVANTE DE PAGAMENTO É VÁLIDO.")
            print(f"    ✔️ Palavras-chave: {'Sim' if tem_palavras else 'Não'} ({', '.join(palavras_encontradas) if palavras_encontradas else 'nenhuma'})")
            print(f"    ✔️ Valor R$30,00: {'Sim' if tem_valor else 'Não'}")
            print(f"    ✔️ CNPJ: {'Sim' if tem_cnpj else 'Não'}")
            print(f"    ✔️ Nome da empresa: {'Sim' if tem_nome_empresa else 'Não'}")
        else:
            print(f"❌ {nome}: NÃO FOI IDENTIFICADO COMO COMPROVANTE DE PAGAMENTO VÁLIDO.")
            print("🔍 Detalhes:")
            print(f"    ✔️ Palavras-chave: {'Sim' if tem_palavras else 'Não'} ({', '.join(palavras_encontradas) if palavras_encontradas else 'nenhuma'})")
            print(f"    ✔️ Valor R$30,00: {'Sim' if tem_valor else 'Não'}")
            print(f"    ✔️ CNPJ: {'Sim' if tem_cnpj else 'Não'}")
            print(f"    ✔️ Nome da empresa: {'Sim' if tem_nome_empresa else 'Não'}")

    except Exception as e:
        print(f"❌ {nome}: erro ao processar OCR: {e}")
