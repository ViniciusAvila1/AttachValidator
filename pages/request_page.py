from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from pages.ocr_verification import validar_conteudo_anexo
import os
import time
import uuid

def baixar_e_validar_anexos(driver, wait, download_path):
    blocos_ids = {
        "A19556AD906D6E9E7902F97288A5B440": "Documento frente",
        "376599C26DE2D5D4E0FAF4F1AC78CCFDF981B89C03ABB1A6CC9D34493EFED945": "Documento verso",
        "2B70879484E4EBCCEB494BBE0AE301E5": "Termo de responsabilidade",
        "66B2DFBF71C3CC8966E2058445361D21A755502137CB598AD9B73BBF45BA926A": "Comprovação de vínculo",
        "8DEDCC02D40669D67BA39063625CD9A1": "Outros documentos"
    }

    for bloco_id, nome_campo in blocos_ids.items():
        try:
            driver.switch_to.window(driver.window_handles[0])

            try:
                wait.until(EC.presence_of_element_located((By.ID, bloco_id)))
            except:
                print(f"⚠️ Bloco '{nome_campo}' (ID: {bloco_id}) não visível no momento. Pulando...")
                continue

            bloco = driver.find_element(By.ID, bloco_id)

            try:
                link_tag = bloco.find_element(By.TAG_NAME, 'a')
                nome_arquivo = link_tag.text.strip()
                print(f"⬇️ Baixando {nome_arquivo}...")

                # Antes de clicar, capturamos os arquivos já existentes
                arquivos_antes = set(os.listdir(download_path))

                link_tag.click()

                # Espera aparecer um novo arquivo na pasta de download
                timeout = 15
                novo_arquivo = None
                for _ in range(timeout):
                    time.sleep(1)
                    arquivos_depois = set(os.listdir(download_path))
                    novos = arquivos_depois - arquivos_antes
                    if novos:
                        novo_arquivo = novos.pop()
                        break

                if not novo_arquivo:
                    print(f"❌ {nome_arquivo}: Download não detectado após {timeout} segundos.")
                    continue

                caminho_arquivo = os.path.join(download_path, novo_arquivo)
                print(f"📄 Arquivo salvo: {novo_arquivo}")
                validar_conteudo_anexo(novo_arquivo, caminho_arquivo)

            except:
                print(f"⚠️ Bloco '{nome_campo}' (ID: {bloco_id}) não possui anexo (sem <a>). Pulando...")

        except Exception as e:
            print(f"⚠️ Erro inesperado no bloco {bloco_id}: {e}")
