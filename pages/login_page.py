from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

def realizar_login(driver, wait, usuario, senha):
    usuario_input = wait.until(EC.visibility_of_element_located((By.ID, "usuario")))
    usuario_input.send_keys(usuario + Keys.ENTER)

    senha_input = wait.until(EC.visibility_of_element_located((By.ID, "senha")))
    senha_input.send_keys(senha + Keys.ENTER)

def fechar_modal_sessao_ativa(wait):
    try:
        modal_btn = WebDriverWait(wait._driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, '//div[contains(@class, "btn-danger") and contains(text(), "Fechar")]'))
        )
        modal_btn.click()
    except:
        print("Nenhum modal de sessão ativa foi encontrado.")
