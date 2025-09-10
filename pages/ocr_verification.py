from PIL import Image, ImageFile
from pdf2image import convert_from_bytes
import pytesseract
import io
import fitz  # PyMuPDF
import re
from datetime import datetime
import unicodedata
import locale

from utils.export_excel import adicionar_comprovante_para_planilha, extrair_codigo_parceiro

# Configura locale para datas em português
try:
    locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
except locale.Error:
    locale.setlocale(locale.LC_TIME, 'pt_BR')
ImageFile.LOAD_TRUNCATED_IMAGES = True

def normalizar_texto(texto):
    """
    Remove acentuação e converte para minúsculas.
    """
    return unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('utf-8').lower()

def extrair_texto_imagem(imagem_bytes):
    imagem = Image.open(io.BytesIO(imagem_bytes))
    imagem.load()
    return pytesseract.image_to_string(imagem, lang='por') # Ajuste para português

def extrair_texto_pdf(pdf_bytes): # extrai texto de PDF, usando OCR se necessário
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

def extrair_nome_pagador(texto: str) -> str: # extrai o nome do titular do pagamento a partir do texto OCR
    padroes_possiveis = [
        r"Nome do pagador\s*[:\-]?\s*(.+)",
        r"Origem.*?Nome\s*[:\-]?\s*(.+)",
        r"(?<=Pagador\s)([A-ZÀ-ÿa-z\s]{5,})",
        r"(?<=Solicitante\s)([A-ZÀ-ÿa-z\s]{5,})",
        r"(?<=Nome\s)([A-ZÀ-ÿa-z\s]{5,})",
        r"(?<=Dados do pagador\s)([A-ZÀ-ÿa-z\s]{5,})",
    ]
    
    for marcador in ["dados de quem pagou", "origem"]:
        if marcador in texto.lower():
            trecho = texto.lower().split(marcador, 1)[1]  # pega tudo após o marcador
            match_nome = re.search(r"nome\s*[:\-]?\s*(.+)", trecho, re.IGNORECASE)
            if match_nome:
                return limpar_nome(match_nome.group(1))
    
    #padrão caixa, buscando "Dados do pagador" ao invés de somente "Nome"
    inicio_pagador = re.search(r"dados do pagador", texto, re.IGNORECASE)
    if not inicio_pagador:
        return "NOME NÃO ENCONTRADO"
    
    trecho_pagador = texto[inicio_pagador.end():] #pegando a partir de dados do pagador
    
    match_nome = re.search(r"nome\s*[:\-]?\s*(.+)", trecho_pagador, re.IGNORECASE)
    
    if match_nome:
        nome_extraido = match_nome.group(1).strip()
        nome_extraido = re.sub(r"[^a-zà-ú\s]", "", nome_extraido, flags=re.IGNORECASE) # remove caracteres especiais
        nome_extraido = re.sub(r"\s{2,}", " ", nome_extraido).strip() # remove espaços múltiplos
        return nome_extraido.upper() # Se não encontrar, retorna um padrão

    # demais padrões
    for padrao in padroes_possiveis:
        match = re.search(padrao, texto, re.IGNORECASE | re.DOTALL)
        if match:
            return limpar_nome(match.group(1))

    #heurística em python: procurar após "De" e ignorar linhas vazias
    # padrão pagbank
    linhas = texto.splitlines()
    for i, linha in enumerate(linhas):
        if re.match(r"^\s*(De|/Pagador)\s*$", linha, re.IGNORECASE):
            # Procura próxima linha não vazia
            for j in range(i+1, len(linhas)):
                prox = linhas[j].strip()
                if prox and not re.match(r"^(cpf|cnpj)", prox, re.IGNORECASE):
                    prox = re.sub(r"\bC*CPF\b", "", prox, flags=re.IGNORECASE)
                    # remove caracteres especiais
                    nome = re.sub(r"[^\w\sÀ-ÿ]", "", prox)
                    # remove numeros
                    nome = re.sub(r"\d+", "", nome)
                    # remove espaços múltiplos
                    nome = re.sub(r"\s+", " ", nome).strip()
                    
                    # se o nome começa com "De" e tem mais de 2 palavras, remove "De"
                    if nome.upper().startswith("DE ") and len(nome.split()) > 2:
                        nome = nome[3:].strip()
                    
                    if 2 <= len(nome.split()) <= 6:
                        return nome.upper()
                    break
def limpar_nome(nome: str) -> str:
    nome = re.sub(r"\bC*CPF\b", "", nome, flags=re.IGNORECASE)
    nome = re.sub(r"[^\w\sÀ-ÿ]", "", nome)
    nome = re.sub(r"\d+", "", nome)
    nome = re.sub(r"\s+", " ", nome).strip()
    if nome.upper().startswith("DE ") and len(nome.split()) > 2:
        nome = nome[3:].strip()
    if 2 <= len(nome.split()) <= 6:
        return nome.upper()
    return "NOME NÃO ENCONTRADO"

def extrair_usuario_de_nome_arquivo(nome_arquivo: str) -> str:
    """
    Extrai o campo 'Usuário' do nome do arquivo, que normalmente aparece após o timestamp.
    Exemplo: '24072025102147#28592@LEV#ARQUIVO_OUTROS#...' → retorna '28592@LEV'
    """
    partes = nome_arquivo.split("#")
    if len(partes) > 1:
        return partes[1]
    return ""

def extrair_data_e_hora_pix(texto: str) -> str:
    """
    Extrai a data e hora no formato dd/mm hh:mm a partir do texto OCR.
    Suporta datas por extenso como '30 de julho de 2025, 21:01'
    """
    import re
    from datetime import datetime

    meses = {
        "janeiro": "01", "fevereiro": "02", "março": "03", "abril": "04", "maio": "05", "junho": "06",
        "julho": "07", "agosto": "08", "setembro": "09", "outubro": "10", "novembro": "11", "dezembro": "12"
    }

    meses_abrev_min = {
        "jan": "01", "fev": "02", "mar": "03", "abr": "04", "mai": "05", "jun": "06",
        "jul": "07", "ago": "08", "set": "09", "out": "10", "nov": "11", "dez": "12"
    }

    padrao_picpay = r"(\d{2})/([a-z]{3})/(\d{4})\s*[-–]\s*(\d{2}:\d{2}:\d{2})"
    match = re.search(padrao_picpay, texto, re.IGNORECASE)
    if match:
        dia, mes_abrev, ano, hora = match.groups()
        mes = meses_abrev_min.get(mes_abrev.lower())
        if mes:
            data_formatada = f"{int(dia):02d}/{mes}"
            hora_curta = hora[:5]  # pega só HH:MM
            return f"{data_formatada} {hora_curta}"

    padrao_mercadopago = r"\b(\d{1,2})\s+de\s+(janeiro|fevereiro|março|abril|maio|junho|julho|agosto|setembro|outubro|novembro|dezembro)\s+de\s+(\d{4}),\s+às\s+(\d{2}:\d{2})"
    match = re.search(padrao_mercadopago, texto, re.IGNORECASE)
    if match:
        dia, mes_ext, ano, hora = match.groups()
        mes = meses.get(mes_ext.lower())
        if mes:
            data_formatada = f"{int(dia):02d}/{mes}"
            return f"{data_formatada} {hora}"

    # Padrão abreviado com mês (ex: 30 JUL 2025 21:01)
    meses_abrev = {
        "JAN": "01", "FEV": "02", "MAR": "03", "ABR": "04", "MAI": "05", "JUN": "06",
        "JUL": "07", "AGO": "08", "SET": "09", "OUT": "10", "NOV": "11", "DEZ": "12"
    }
    padrao_abrev = r"(\d{1,2})\s*(JAN|FEV|MAR|ABR|MAI|JUN|JUL|AGO|SET|OUT|NOV|DEZ)\s*(\d{4})\s*[-/]?\s*(\d{2}:\d{2})"
    match = re.search(padrao_abrev, texto, re.IGNORECASE)
    if match:
        dia, mes_abrev, ano, hora = match.groups()
        mes = meses_abrev.get(mes_abrev.upper())
        if mes:
            data_formatada = f"{int(dia):02d}/{mes}"
            return f"{data_formatada} {hora}"

    # Outros formatos comuns
    padroes = [
        r"(\d{2}/\d{2}/\d{4})[^\d]*(\d{2}:\d{2})",   # 30/07/2025 21:01
        r"(\d{2}/\d{2})[^\d]*(\d{2}:\d{2})",         # 30/07 21:01
        r"(\d{2}-\d{2}-\d{4})[^\d]*(\d{2}:\d{2})"     # 30-07-2025 21:01
    ]
    for padrao in padroes:
        match = re.search(padrao, texto)
        if match:
            data = match.group(1).replace("-", "/")
            hora = match.group(2)[:5]
            try:
                data_formatada = datetime.strptime(data, "%d/%m/%Y").strftime("%d/%m")
            except:
                try:
                    data_formatada = datetime.strptime(data, "%d/%m").strftime("%d/%m")
                except:
                    continue
            return f"{data_formatada} {hora}"

    return "DATA/HORA NÃO ENCONTRADA"

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
        padrao_valor = re.compile(r"(r\$)?\s*-?\s*3[0oº]{1}([\.,]?[0oº]{2})?\b", re.IGNORECASE)
        match_valor = padrao_valor.search(texto_para_valor)
        tem_valor = bool(match_valor)
        if match_valor:
            print("💰 Valor encontrado: ", match_valor.group())

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
            r"\d{2}/[a-zç]{3}/\d{4}" # dd/mes/yyyy
        ]
        formatos = [
            "%d/%m/%Y", "%d/%m/%y", "%d-%m-%Y", "%d-%m-%y",
            "%d de %B de %Y", "%d de %B", "%d/%b/%Y", "%d/%b/%y",
            "%d-%b-%Y", "%d-%b-%y", "%d %B %Y", "%d %b %Y", "%d/%b/%y"
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

        if comprovante_valido:
            # Coletar informações extras para exportação
            nome_pagador = extrair_nome_pagador(texto)
            data_completa = extrair_data_e_hora_pix(texto)

            if "DATA/HORA" not in data_completa:
                detalhes = f"{data_completa} {nome_pagador}"
                data_pix = data_completa.split()[0]
            else:
                detalhes = f"DATA/HORA NÃO ENCONTRADA {nome_pagador}"
                data_pix = "DATA/HORA"

            if nome_pagador in ["NOME NÃO ENCONTRADO", "", None]:
                nome_pagador = "PAGADOR NÃO IDENTIFICADO"

            valor_formatado = "R$ 30,00"
            usuario_raw = extrair_usuario_de_nome_arquivo(nome)
            codigo_parceiro = extrair_codigo_parceiro(usuario_raw)

            # Adiciona à planilha
            adicionar_comprovante_para_planilha(
                data_pix=data_pix,
                valor=valor_formatado,
                detalhes=detalhes,
                codigo=codigo_parceiro
            )

        # exibição final
        imprimir_detalhes_comprovante(nome, tem_palavras, tem_valor, tem_cnpj, tem_nome_empresa, data_valida, contem_proibidas, comprovante_valido)

    except Exception as e:
        print(f"❌ {nome}: erro ao processar OCR: {e}")
