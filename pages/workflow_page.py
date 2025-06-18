from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import time

def acessar_workflow(driver, wait):
    processos_btn = wait.until(EC.element_to_be_clickable((By.ID, "navbarProcessos")))
    processos_btn.click()
    time.sleep(1)

    workflow_link = wait.until(EC.element_to_be_clickable((By.XPATH, '//a[contains(@href, "Workflow.aspx")]')))
    workflow_link.click()
    time.sleep(1)

def filtrar_criacao_usuario_clicklev(driver, wait):
    tipo_btn = wait.until(EC.element_to_be_clickable((
        By.XPATH, '//button[contains(@class, "multiselect dropdown-toggle")]'
    )))
    tipo_btn.click()
    time.sleep(1)

    opcao_tipo = wait.until(EC.element_to_be_clickable((
        By.XPATH, '//label[contains(text(), "WORKFLOW - CRIACAO DE NOVO USUARIO")]/input'
    )))
    opcao_tipo.click()
    time.sleep(1)

    situacao_btn = wait.until(EC.element_to_be_clickable((
        By.XPATH, '//div[label[contains(text(), "Situação")]]//button'
    )))
    situacao_btn.click()
    time.sleep(1)

    etapa_checkbox = wait.until(EC.element_to_be_clickable((
        By.XPATH, '//label[contains(text(), "ETAPA INTERNA")]/input'
    )))
    etapa_checkbox.click()
    time.sleep(1)

    banco_btn = wait.until(EC.element_to_be_clickable((
        By.XPATH, '//div[label[contains(text(), "Banco")]]//button'
    )))
    banco_btn.click()
    time.sleep(1)

    clicklev_checkbox = wait.until(EC.element_to_be_clickable((
        By.XPATH, '//label[contains(text(), "CLICKLEV")]/input'
    )))
    clicklev_checkbox.click()
    time.sleep(1)

    botao_pesquisar = wait.until(EC.element_to_be_clickable((By.ID, "btPesquisar")))
    driver.execute_script("arguments[0].click();", botao_pesquisar)

    wait.until(EC.presence_of_element_located((By.ID, 'tableWorkFlow')))
    time.sleep(2)

    dropdown_button = wait.until(EC.element_to_be_clickable((
        By.XPATH, '//table[@id="tableWorkFlow"]/tbody/tr[1]//button[contains(@class, "dropdown-toggle")]'
    )))
    dropdown_button.click()
    time.sleep(1)

    atender_opcao = wait.until(EC.element_to_be_clickable((
        By.XPATH, '//table[@id="tableWorkFlow"]/tbody/tr[1]//div[contains(text(), "Atender Solicitação")]'
    )))
    atender_opcao.click()
