from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import time

def baixar_todos_anexos(driver, wait):
    print("\n📎 Buscando todos os anexos disponíveis...")
    try:
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "SMA-crv")))
        blocos_anexo = driver.find_elements(By.CLASS_NAME, "SMA-crv")

        arquivos_baixados = []

        for bloco in blocos_anexo:
            try:
                link = bloco.find_element(By.TAG_NAME, "a")
                nome_arquivo = link.text.strip()
                link.click()
                print(f"✔️ Anexo baixado: {nome_arquivo}")
                arquivos_baixados.append(nome_arquivo)
                time.sleep(2)
            except:
                continue

        if not arquivos_baixados:
            print("⚠️ Nenhum anexo encontrado.")
        return arquivos_baixados

    except Exception as e:
        print(f"❌ Erro ao buscar anexos: {e}")
        return []
