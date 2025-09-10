from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from datetime import datetime
import time

def acessar_workflow(driver, wait):
    processos_btn = wait.until(EC.element_to_be_clickable((By.ID, "navbarProcessos")))
    processos_btn.click()

    workflow_link = wait.until(EC.element_to_be_clickable((By.XPATH, '//a[contains(@href, "Workflow.aspx")]')))
    workflow_link.click()

def filtrar_criacao_usuario_clicklev(driver, wait):
    tipo_btn = wait.until(EC.element_to_be_clickable((
        By.XPATH, '//button[contains(@class, "multiselect dropdown-toggle")]'
    )))
    tipo_btn.click()
    
    opcao_tipo = wait.until(EC.element_to_be_clickable((
        By.XPATH, '//label[contains(text(), "WORKFLOW - CRIACAO DE NOVO USUARIO")]/input'
    )))
    opcao_tipo.click()

    """
    opcao_tipo = wait.until(EC.element_to_be_clickable((
        By.XPATH, '//label[contains(text(), "WORKFLOW - RESET SENHA")]/input'
    )))
    opcao_tipo.click()
    """
    
    situacao_btn = wait.until(EC.element_to_be_clickable((
        By.XPATH, '//div[label[contains(text(), "Situação")]]//button'
    )))
    situacao_btn.click()
    
    etapa_checkbox = wait.until(EC.element_to_be_clickable((
        By.XPATH, '//label[contains(text(), "ETAPA INTERNA")]/input',
    )))
    etapa_checkbox.click()
    """
    aguarda_checkbox = wait.until(EC.element_to_be_clickable((
        By.XPATH, '//label[contains(text(), "AGUARDANDO")]/input',
    )))
    aguarda_checkbox.click()
    """
    banco_btn = wait.until(EC.element_to_be_clickable((
        By.XPATH, '//div[label[contains(text(), "Banco")]]//button'
    )))
    banco_btn.click()

    clicklev_checkbox = wait.until(EC.element_to_be_clickable((
        By.XPATH, '//label[contains(text(), "CLICKLEV")]/input'
    )))
    clicklev_checkbox.click()
    
    """
    clickpower_checkbox = wait.until(EC.element_to_be_clickable((
        By.XPATH, '//label[contains(text(), "CLICKPOWER")]/input'
    )))
    clickpower_checkbox.click()
    """
        
    # Define as datas: início fixo e fim como data atual
    data_inicial = "01/01/2025"
    data_final = datetime.today().strftime('%d/%m/%Y')

    # Preenche o campo de Data Inicial
    campo_data_inicial = wait.until(EC.element_to_be_clickable((By.ID, 'Processo_txtDataInicial')))
    campo_data_inicial.clear()
    campo_data_inicial.send_keys(data_inicial)
    time.sleep(0.5)

    # Preenche o campo de Data Final
    campo_data_final = wait.until(EC.element_to_be_clickable((By.ID, 'Processo_txtDataFinal')))
    campo_data_final.clear()
    campo_data_final.send_keys(data_final)
    time.sleep(0.5)

    #clique no botão pesquisar
    botao_pesquisar = wait.until(EC.element_to_be_clickable((By.ID, "btPesquisar")))
    driver.execute_script("arguments[0].click();", botao_pesquisar)

    try:
        tabela = wait.until(EC.presence_of_element_located((By.ID, 'tableWorkFlow')))
        linhas = tabela.find_elements(By.XPATH, './/tbody/tr')

        # Filtra apenas linhas que realmente têm botão de ação (ou seja, solicitações reais)
        linhas_validas = [
            linha for linha in linhas
            if linha.find_elements(By.XPATH, './/button[contains(@class, "dropdown-toggle")]')
        ]

        if not linhas_validas:
            print("❌ Nenhuma solicitação encontrada na tabela.")
            time.sleep(4)
            return False
    except Exception as e:
        print(f"❌ Erro ao tentar localizar a tabela ou as linhas: {e}")
        return

    # Se tiver linhas, segue o processo
    dropdown_button = wait.until(EC.element_to_be_clickable((
        By.XPATH, '//table[@id="tableWorkFlow"]/tbody/tr[1]//button[contains(@class, "dropdown-toggle")]'
    )))
    dropdown_button.click()
    time.sleep(1)

    atender_opcao = wait.until(EC.element_to_be_clickable((
        By.XPATH, '//table[@id="tableWorkFlow"]/tbody/tr[1]//div[contains(text(), "Atender Solicitação")]'
    )))
    atender_opcao.click()
    return True