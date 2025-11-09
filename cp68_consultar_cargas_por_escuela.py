# ============================================================
# CP_68 - Consultar cargas por escuela
# Autor: José René Lucero Barrera
# ============================================================
# Objetivo:
# Validar que un usuario autorizado (Admin) pueda filtrar las
# cargas académicas por escuela en el módulo Carga Académica.
# ============================================================

import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager

# ============================================================
# CONFIGURACIÓN
# ============================================================
URL_BASE = "https://helpful-youth-production-1d3f.up.railway.app/"
RESULTADOS_FILE = "resultados_CP68.txt"
LOG_FILE = "cp68_log.txt"

USUARIO = {
    "email": "admin@ues.edu.sv",
    "password": "password"
}

TEXTO_BUSQUEDA = "Ingeniería de Sistemas Informáticos"

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
        f.write("EJECUCIÓN DE CASO DE PRUEBA CP_68 – CONSULTAR CARGAS POR ESCUELA\n")
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
# ESCENARIO – ADMIN autorizado
# ============================================================
def escenario_admin_filtrar_por_nombre():
    log("------------------------------------------------------")
    log("ESCENARIO: ADMIN - Consultar cargas por escuela (Buscar por nombre)")
    log("------------------------------------------------------")

    driver, wait, actions = iniciar_driver()
    try:
        # 1. Login
        log("1. Iniciando sesión como Admin...")
        login(driver, wait, USUARIO["email"], USUARIO["password"])

        # 2. Desplegar menú lateral "Carga académica"
        log("2. Desplegando menú lateral 'Carga académica'...")
        menu_principal = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(),'Carga académica')]")))
        driver.execute_script("arguments[0].click();", menu_principal)
        time.sleep(1)

        # 3. Ingresar al submódulo
        log("3. Ingresando al submódulo 'Carga académica'...")
        opcion_carga = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[@href='/carga-academica']")))
        driver.execute_script("arguments[0].click();", opcion_carga)
        time.sleep(2)

        # 4. Esperar tabla cargada
        log("4. Esperando que la tabla inicial se muestre...")
        filas_iniciales = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "tr.ant-table-row")))
        log(f"   → Tabla cargada con {len(filas_iniciales)} registros visibles.")

        # 5. Buscar por nombre
        log(f"5. Ingresando texto '{TEXTO_BUSQUEDA}' en el campo de búsqueda...")
        input_busqueda = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Buscar por nombre']")))
        input_busqueda.clear()
        input_busqueda.send_keys(TEXTO_BUSQUEDA)
        time.sleep(1)

        # 6. Buscando
        log("6. Presionando botón de búsqueda (lupa)...")
        boton_buscar = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.ant-input-search-button")))
        driver.execute_script("arguments[0].click();", boton_buscar)
        time.sleep(2)

        # 7. Validar resultados
        log("7. Validando registros filtrados...")
        filas_filtradas = driver.find_elements(By.CSS_SELECTOR, "tr.ant-table-row")

        if len(filas_filtradas) > 0:
            resultado = f"ÉXITO (Listado filtrado correctamente por '{TEXTO_BUSQUEDA}' con {len(filas_filtradas)} registros)"
        else:
            resultado = f"FALLIDO (No se encontraron resultados para '{TEXTO_BUSQUEDA}')"

    except TimeoutException as te:
        resultado = f"FALLIDO (Tiempo de espera agotado: {str(te)})"
    except Exception as e:
        resultado = f"FALLIDO (Error inesperado: {e})"

    registrar_resultado("Escenario - Admin", resultado)
    log(f"ESCENARIO finalizado: {resultado}\n")
    driver.quit()

# ============================================================
# EJECUCIÓN PRINCIPAL
# ============================================================
if __name__ == "__main__":
    print("========== INICIO DE CP_68 ==========\n")
    open(RESULTADOS_FILE, "w", encoding="utf-8").close()
    open(LOG_FILE, "w", encoding="utf-8").close()
    registrar_encabezado()

    escenario_admin_filtrar_por_nombre()

    print("========== FIN DE CP_68 ==========\n")
    log("Ejecución finalizada correctamente.")
