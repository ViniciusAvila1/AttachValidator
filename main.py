from config import settings
from drivers.browser import iniciar_driver
from pages.login_page import realizar_login, fechar_modal_sessao_ativa
from pages.workflow_page import acessar_workflow, filtrar_criacao_usuario_clicklev
from pages.request_page import baixar_e_validar_anexos

if __name__ == "__main__":
    driver, wait, download_path = iniciar_driver(com_download=True)
    realizar_login(driver, wait, settings.USUARIO, settings.SENHA)
    fechar_modal_sessao_ativa(wait)
    acessar_workflow(driver, wait)
    
    tem_solicitacao = filtrar_criacao_usuario_clicklev(driver, wait)
    if not tem_solicitacao:
        driver.quit()
        exit()
        
    baixar_e_validar_anexos(driver, wait, download_path)