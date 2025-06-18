from config import settings
from drivers.browser import iniciar_driver
from pages.login_page import realizar_login, fechar_modal_sessao_ativa
from pages.workflow_page import acessar_workflow, filtrar_criacao_usuario_clicklev
from pages.request_page import baixar_todos_anexos

if __name__ == "__main__":
    driver, wait = iniciar_driver()
    realizar_login(driver, wait, settings.USUARIO, settings.SENHA)
    fechar_modal_sessao_ativa(wait)
    acessar_workflow(driver, wait)
    filtrar_criacao_usuario_clicklev(driver, wait)
    baixar_todos_anexos(driver, wait)
