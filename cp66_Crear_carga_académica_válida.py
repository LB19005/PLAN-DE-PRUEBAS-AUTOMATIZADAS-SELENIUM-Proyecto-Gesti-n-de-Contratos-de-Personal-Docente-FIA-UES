# ============================================================
# CP_66 - Crear carga académica válida
# Autor: José René Lucero Barrera
# ============================================================

import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# ============================================================
# CONFIGURACIÓN
# ============================================================
URL_BASE = "https://helpful-youth-production-1d3f.up.railway.app/"
RESULTADOS_FILE = "resultados_CP66.txt"
LOG_FILE = "cp66_log.txt"

USUARIOS = {
    "rrhh": {"email": "rrhh@ues.edu.sv", "password": "password"},
    "director": {"email": "fatimavelasquez@gmail.com", "password": "Hola1234"}
}

# ============================================================
# FUNCIONES AUXILIARES
# ============================================================
def log(msg):
    print(msg)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{datetime.now().strftime('%H:%M:%S')} | {msg}\n")

def registrar_encabezado():
    with open(RESULTADOS_FILE, "a", encoding="utf-8") as f:
        f.write("============================================================\n")
        f.write("EJECUCIÓN DE CASO DE PRUEBA CP_66 – CREAR CARGA ACADÉMICA VÁLIDA\n")
        f.write("Sistema: Gestión de Contratos FIA – Universidad de El Salvador\n")
        f.write(f"Fecha y hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
        f.write("============================================================\n\n")

def registrar_resultado(escenario, resultado):
    with open(RESULTADOS_FILE, "a", encoding="utf-8") as f:
        f.write(f"{datetime.now().strftime('%H:%M:%S')} | {escenario}: {resultado}\n")

def iniciar_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-popup-blocking")
    service = ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    wait = WebDriverWait(driver, 25)
    actions = ActionChains(driver)
    return driver, wait, actions

def login(driver, wait, email, password):
    driver.get(URL_BASE)
    wait.until(EC.presence_of_element_located((By.ID, "basic_email"))).send_keys(email)
    driver.find_element(By.ID, "basic_password").send_keys(password)
    driver.find_element(By.CSS_SELECTOR, ".ant-btn").click()
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    time.sleep(2)
    log(f"Inicio de sesión exitoso: {email}")

# ============================================================
# ESCENARIO 1 – RRHH (sin permisos)
# ============================================================
def escenario_rrhh():
    log("------------------------------------------------------")
    log("ESCENARIO 1: RRHH - Sin permisos")
    log("------------------------------------------------------")

    driver, wait, actions = iniciar_driver()
    try:
        log("1. Iniciando sesión como RRHH...")
        login(driver, wait, USUARIOS["rrhh"]["email"], USUARIOS["rrhh"]["password"])

        log("2. Intentando ingresar a módulo 'Carga académica'...")
        driver.get(URL_BASE + "carga-academica")
        time.sleep(2)

        try:
            driver.find_element(By.XPATH, "//span[contains(text(),'Generar nueva carga académica')]")
            resultado = "FALLIDO (El usuario RRHH accedió al módulo restringido)"
        except NoSuchElementException:
            resultado = "ÉXITO (Bloqueo correcto de acceso al módulo para usuario sin permisos)"

    except Exception as e:
        resultado = f"FALLIDO (Error inesperado: {e})"

    registrar_resultado("Escenario 1 - RRHH", resultado)
    log(f"ESCENARIO 1 finalizado: {resultado}\n")
    driver.quit()

# ============================================================
# ESCENARIO 2 – DIRECTOR ESCUELA (crear carga académica válida)
# ============================================================
def escenario_director():
    log("------------------------------------------------------")
    log("ESCENARIO 2: DIRECTOR ESCUELA - Crear carga académica válida")
    log("------------------------------------------------------")

    driver, wait, actions = iniciar_driver()
    try:
        log("1. Iniciando sesión como director...")
        login(driver, wait, USUARIOS["director"]["email"], USUARIOS["director"]["password"])

        log("2. Desplegando menú lateral 'Carga académica'...")
        # Clic en el título del menú para expandirlo
        menu_principal = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(),'Carga académica')]")))
        driver.execute_script("arguments[0].click();", menu_principal)
        time.sleep(1)

        # Clic en el subenlace interno
        opcion_carga = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[@href='/carga-academica']")))
        driver.execute_script("arguments[0].click();", opcion_carga)
        log("3. Accediendo al submódulo 'Carga académica'...")
        time.sleep(2)

        log("4. Presionando 'Generar nueva carga académica'...")
        btn_generar = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[text()='Generar nueva carga académica']")))
        btn_generar.click()
        time.sleep(1)

        log("5. Confirmando con botón 'Aceptar'...")
        btn_aceptar = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[span[text()='Aceptar']]")))
        driver.execute_script("arguments[0].click();", btn_aceptar)
        time.sleep(2)

        log("6. Verificando mensaje de éxito...")
        try:
            wait.until(EC.visibility_of_element_located((By.XPATH, "//*[contains(text(),'Carga académica generada con éxito')]")))
            resultado = "ÉXITO (Mensaje: 'Carga académica generada con éxito')"
        except TimeoutException:
            resultado = "FALLIDO (No apareció mensaje de éxito tras confirmar)"

        log("7. Validando que el nuevo registro aparezca en la tabla...")
        try:
            wait.until(EC.presence_of_element_located((By.XPATH, "//td[contains(text(),'Ciclo')]")))
            resultado += " | ÉXITO (Nuevo registro visible en tabla)"
        except TimeoutException:
            resultado += " | No se pudo crear la carga academica porque Director ya tiene carga asignada intentar con nuevo usuario o eliminar carga"

    except Exception as e:
        resultado = f"FALLIDO (Error inesperado: {e})"

    registrar_resultado("Escenario 2 - Director Escuela", resultado)
    log(f"ESCENARIO 2 finalizado: {resultado}\n")
    driver.quit()

# ============================================================
# EJECUCIÓN PRINCIPAL
# ============================================================
if __name__ == "__main__":
    print("========== INICIO DE CP_66 ==========\n")
    open(RESULTADOS_FILE, "w", encoding="utf-8").close()
    open(LOG_FILE, "w", encoding="utf-8").close()
    registrar_encabezado()

    escenario_rrhh()
    escenario_director()

    print("========== FIN DE CP_66 ==========\n")
    log("Ejecución finalizada correctamente.")
