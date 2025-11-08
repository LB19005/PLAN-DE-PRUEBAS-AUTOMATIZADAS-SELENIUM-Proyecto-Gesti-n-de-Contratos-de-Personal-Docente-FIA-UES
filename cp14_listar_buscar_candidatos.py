"""
CP_14 - Listar y buscar candidatos por nombre
Autor: José René Lucero Barrera
"""

import time
import unicodedata
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


URL_BASE = "https://helpful-youth-production-1d3f.up.railway.app/"
USUARIO = "rrhh@ues.edu.sv"
PASSWORD = "password"
RESULTADOS_FILE = "resultados_CP14.txt"


def normalizar(t):
    """Convierte texto a minúsculas sin acentos."""
    return "".join(c for c in unicodedata.normalize("NFD", t.lower()) if unicodedata.category(c) != "Mn")


def log(t):
    """Registra texto en consola y archivo."""
    print(t)
    with open(RESULTADOS_FILE, "a", encoding="utf-8") as f:
        f.write(t + "\n")


def limpiar():
    """Limpia el archivo de resultados al iniciar."""
    open(RESULTADOS_FILE, "w", encoding="utf-8").close()


def iniciar_driver():
    """Inicia el navegador Chrome."""
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-notifications")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    service = ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    wait = WebDriverWait(driver, 45)
    return driver, wait


def login(driver, wait):
    """Realiza el inicio de sesión."""
    log("1. Iniciando sesión como RRHH...")
    driver.get(URL_BASE)
    wait.until(EC.presence_of_element_located((By.ID, "basic_email"))).send_keys(USUARIO)
    driver.find_element(By.ID, "basic_password").send_keys(PASSWORD)
    driver.find_element(By.CSS_SELECTOR, ".ant-btn").click()
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "a[href='/candidatos-registrados']")))
    log("✅ Sesión iniciada correctamente.\n")


def limpiar_y_escribir(campo, texto):
    """Limpia correctamente el campo antes de escribir."""
    campo.click()
    campo.clear()
    campo.send_keys(u"\ue009" + "a")  # Ctrl + A
    campo.send_keys(u"\ue003")        # Delete
    campo.send_keys(texto)


# -----------------------------------------------------------
# ESCENARIO 1: LISTAR CANDIDATOS
# -----------------------------------------------------------

def escenario_1(driver, wait, resumen):
    log("------------------------------------------------------")
    log("ESCENARIO 1: RRHH - Listar candidatos registrados")
    log("------------------------------------------------------")
    try:
        # Clic forzado en el enlace interno del menú (evita bloqueo del pseudo-elemento ::before)
        enlace = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "a[href='/candidatos-registrados']"))
        )
        driver.execute_script("arguments[0].click();", enlace)

        # Esperar que la URL cambie y el listado aparezca
        wait.until(EC.url_contains("/candidatos-registrados"))
        time.sleep(2)

        # Esperar que se cargue el contenedor principal
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.ant-spin-container")))

        # Intentar detectar filas de la tabla (Ant Design Table)
        filas = driver.find_elements(By.CSS_SELECTOR, "div.ant-spin-container tr.ant-table-row")

        # Si no hay filas aún, reintentar varias veces
        intentos = 0
        while not filas and intentos < 5:
            time.sleep(1)
            filas = driver.find_elements(By.CSS_SELECTOR, "div.ant-spin-container tr.ant-table-row")
            intentos += 1

        # Validar resultado
        if filas:
            total = len(filas)
            primeros = [f.text.split("\n")[0] for f in filas[:5] if f.text]
            log("2. Consultando listado de candidatos registrados...")
            log(f"→ Se encontraron {total} candidatos en el sistema.")
            if primeros:
                log("   Ejemplos: " + ", ".join(primeros))
            log("ESCENARIO 1 finalizado: ÉXITO (Listado mostrado correctamente)\n")
            resumen["exito"] += 1
        else:
            contenedor = driver.find_element(By.CSS_SELECTOR, "div.ant-spin-container")
            texto = contenedor.text.strip()
            if texto:
                log("→ Se muestra texto en el listado (tabla visible).")
                log("ESCENARIO 1 finalizado: ÉXITO (Listado visible correctamente)\n")
                resumen["exito"] += 1
            else:
                driver.save_screenshot("fallo_cp14_escenario1.png")
                raise Exception("No se detectaron filas ni texto en la tabla (ver captura).")

    except Exception as e:
        log(f"ESCENARIO 1 finalizado: FALLIDO (Error al listar candidatos: {e})\n")
        resumen["fallido"] += 1


# -----------------------------------------------------------
# ESCENARIO 2: BUSCAR CANDIDATA "maria"
# -----------------------------------------------------------

def escenario_2(driver, wait, resumen):
    log("------------------------------------------------------")
    log("ESCENARIO 2: RRHH - Buscar candidata específica (maria)")
    log("------------------------------------------------------")
    try:
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href='/candidatos-registrados']"))).click()
        wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, "input[placeholder='Buscar por nombre de candidato']")))
        time.sleep(2)

        campo = driver.find_element(By.CSS_SELECTOR, "input[placeholder='Buscar por nombre de candidato']")
        limpiar_y_escribir(campo, "maria")

        boton = driver.find_element(By.CSS_SELECTOR, "span.anticon-search")
        driver.execute_script("arguments[0].click();", boton)
        time.sleep(3)

        filas = driver.find_elements(By.CSS_SELECTOR, "div.ant-spin-container tr.ant-table-row")
        textos = [normalizar(f.text) for f in filas]
        log("1. Realizando búsqueda con el texto: maria...")

        if any("maria" in t for t in textos):
            log("→ Se encontró al menos una candidata con nombre 'maria'.")
            log("ESCENARIO 2 finalizado: ÉXITO (Resultados correctos para 'maria')\n")
            resumen["exito"] += 1
        else:
            log("→ No se encontró ningún registro con el nombre 'maria'.")
            log("ESCENARIO 2 finalizado: FALLIDO (No se encontró resultado esperado)\n")
            resumen["fallido"] += 1

    except Exception as e:
        log(f"ESCENARIO 2 finalizado: FALLIDO ({e})\n")
        resumen["fallido"] += 1


# -----------------------------------------------------------
# ESCENARIO 3: BUSCAR CANDIDATOS INEXISTENTES
# -----------------------------------------------------------

def escenario_3(driver, wait, resumen):
    log("------------------------------------------------------")
    log("ESCENARIO 3: RRHH - Buscar candidatos inexistentes")
    log("------------------------------------------------------")
    try:
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href='/candidatos-registrados']"))).click()
        wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, "input[placeholder='Buscar por nombre de candidato']")))
        time.sleep(2)

        campo = driver.find_element(By.CSS_SELECTOR, "input[placeholder='Buscar por nombre de candidato']")
        limpiar_y_escribir(campo, "xyz123")

        boton = driver.find_element(By.CSS_SELECTOR, "span.anticon-search")
        driver.execute_script("arguments[0].click();", boton)
        time.sleep(3)

        contenedor = driver.find_element(By.CSS_SELECTOR, "div.ant-spin-container")
        texto = contenedor.text.lower()
        log("1. Buscando candidatos con texto inexistente: 'xyz123'...")

        if "no hay datos" in texto or "no data" in texto:
            log("→ No se encontraron resultados (correcto).")
            log("ESCENARIO 3 finalizado: ÉXITO (No se muestran resultados inexistentes)\n")
            resumen["exito"] += 1
        else:
            filas = driver.find_elements(By.CSS_SELECTOR, "tr.ant-table-row")
            if len(filas) == 0:
                log("→ No se encontraron resultados (correcto).")
                log("ESCENARIO 3 finalizado: ÉXITO (No se muestran resultados inexistentes)\n")
                resumen["exito"] += 1
            else:
                log(f"→ Se encontraron {len(filas)} registros inesperados.")
                log("ESCENARIO 3 finalizado: FALLIDO (El filtro no funcionó correctamente)\n")
                resumen["fallido"] += 1

    except Exception as e:
        log(f"ESCENARIO 3 finalizado: FALLIDO ({e})\n")
        resumen["fallido"] += 1


# -----------------------------------------------------------
# EJECUCIÓN PRINCIPAL
# -----------------------------------------------------------
if __name__ == "__main__":
    limpiar()
    resumen = {"exito": 0, "fallido": 0}
    log("========== INICIO DE CP_14 ==========\n")
    driver, wait = iniciar_driver()
    try:
        login(driver, wait)
        escenario_1(driver, wait, resumen)
        escenario_2(driver, wait, resumen)
        escenario_3(driver, wait, resumen)
    finally:
        driver.quit()
        total = resumen["exito"] + resumen["fallido"]
        log("========== FIN DE CP_14 ==========\n")
        log(f"Resumen final: {total} escenarios ejecutados -> "
            f"{resumen['exito']} ÉXITO / {resumen['fallido']} FALLIDO\n")
        log(f"Archivo '{RESULTADOS_FILE}' generado correctamente.\n")

    print(f"\nArchivo '{RESULTADOS_FILE}' generado correctamente.\n")
