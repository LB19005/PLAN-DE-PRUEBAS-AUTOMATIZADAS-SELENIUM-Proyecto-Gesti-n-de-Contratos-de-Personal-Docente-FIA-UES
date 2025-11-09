# ============================================================
# CP_67 - Listar todas las cargas académicas
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
RESULTADOS_FILE = "resultados_CP67.txt"
LOG_FILE = "cp67_log.txt"

USUARIOS = {
    "rrhh": {"email": "rrhh@ues.edu.sv", "password": "password"},
    "admin": {"email": "admin@ues.edu.sv", "password": "password"}
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
        f.write("EJECUCIÓN DE CASO DE PRUEBA CP_67 – LISTAR CARGAS ACADÉMICAS\n")
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
    log(f"Inicio de sesión: {email}")

# ============================================================
# ESCENARIO 1 – RRHH sin permisos
# ============================================================
def escenario_rrhh():
    log("------------------------------------------------------")
    log("ESCENARIO 1: RRHH - Sin permisos (Validar que no liste cargas)")
    log("------------------------------------------------------")

    driver, wait, actions = iniciar_driver()
    try:
        log("1. Iniciando sesión como RRHH...")
        login(driver, wait, USUARIOS["rrhh"]["email"], USUARIOS["rrhh"]["password"])

        log("2. Intentando acceder al submódulo 'Carga académica' (URL directa)...")
        driver.get(URL_BASE + "carga-academica")
        time.sleep(2)

        try:
            driver.find_element(By.XPATH, "//span[contains(text(),'Generar nueva carga académica')]")
            resultado = "FALLIDO (Usuario RRHH puede ver el módulo de Carga Académica)"
        except NoSuchElementException:
            resultado = "ÉXITO (Usuario RRHH no muestra módulo ni listado de cargas)"

    except Exception as e:
        resultado = f"FALLIDO (Error inesperado: {e})"

    registrar_resultado("Escenario 1 - RRHH", resultado)
    log(f"ESCENARIO 1 finalizado: {resultado}\n")
    driver.quit()

# ============================================================
# ESCENARIO 2 – ADMIN autorizado
# ============================================================
def escenario_admin():
    log("------------------------------------------------------")
    log("ESCENARIO 2: ADMIN - Listar cargas académicas (Usuario autorizado)")
    log("------------------------------------------------------")

    driver, wait, actions = iniciar_driver()
    try:
        log("1. Iniciando sesión como Admin...")
        login(driver, wait, USUARIOS["admin"]["email"], USUARIOS["admin"]["password"])

        log("2. Desplegando menú lateral 'Carga académica'...")
        menu_principal = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(),'Carga académica')]")))
        driver.execute_script("arguments[0].click();", menu_principal)
        time.sleep(1)

        log("3. Ingresando al submódulo 'Carga académica'...")
        opcion_carga = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[@href='/carga-academica']")))
        driver.execute_script("arguments[0].click();", opcion_carga)

        log("4. Esperando que la tabla de cargas académicas se muestre...")
        try:
            filas = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "tr.ant-table-row")))
            count = len(filas)
            log(f"   → Se detectaron {count} registros en la tabla.")
            time.sleep(3)  # <<< Delay adicional para observar la tabla
            if count > 0:
                resultado = f"ÉXITO (Listado mostrado con {count} registros)"
            else:
                resultado = "FALLIDO (Tabla cargada pero sin filas detectables)"
        except TimeoutException:
            resultado = "FALLIDO (No se detectó la tabla de cargas académicas)"

    except Exception as e:
        resultado = f"FALLIDO (Error inesperado: {e})"

    registrar_resultado("Escenario 2 - Admin", resultado)
    log(f"ESCENARIO 2 finalizado: {resultado}\n")
    driver.quit()

# ============================================================
# EJECUCIÓN PRINCIPAL
# ============================================================
if __name__ == "__main__":
    print("========== INICIO DE CP_67 ==========\n")
    open(RESULTADOS_FILE, "w", encoding="utf-8").close()
    open(LOG_FILE, "w", encoding="utf-8").close()
    registrar_encabezado()

    escenario_rrhh()
    escenario_admin()

    print("========== FIN DE CP_67 ==========\n")
    log("Ejecución finalizada correctamente.")
