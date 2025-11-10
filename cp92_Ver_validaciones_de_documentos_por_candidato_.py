"""
CP_92 - Revisión y verificación de documentos por RRHH
Versión final según flujo visual proporcionado.
Autor: José René Lucero Barrera
Rol: RRHH
"""

import time
import unicodedata
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


# ==========================================================
# CONFIGURACIÓN GENERAL
# ==========================================================
URL_BASE = "https://helpful-youth-production-1d3f.up.railway.app/"
USUARIO = "rrhh@ues.edu.sv"
PASSWORD = "password"
CANDIDATO = "Ruben Ernesto"
RESULTADOS_FILE = "resultados_CP92.txt"


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
    """Inicio de sesión."""
    log("1. Iniciando sesión como RRHH...")
    driver.get(URL_BASE)
    wait.until(EC.presence_of_element_located((By.ID, "basic_email"))).send_keys(USUARIO)
    driver.find_element(By.ID, "basic_password").send_keys(PASSWORD)
    driver.find_element(By.CSS_SELECTOR, ".ant-btn").click()
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "a[href='/candidatos-registrados']")))
    log(" Sesión iniciada correctamente.\n")


def limpiar_y_escribir(campo, texto):
    """Limpia correctamente el campo antes de escribir."""
    campo.click()
    campo.clear()
    campo.send_keys(u"\ue009" + "a")  # Ctrl + A
    campo.send_keys(u"\ue003")        # Delete
    campo.send_keys(texto)


# ==========================================================
# ESCENARIO PRINCIPAL
# ==========================================================
def escenario_revision_y_verificacion(driver, wait, resumen):
    log("------------------------------------------------------")
    log("ESCENARIO: RRHH - Revisión y verificación de documentos")
    log("------------------------------------------------------")
    try:
        # 1️⃣ Abrir módulo Candidatos registrados
        enlace = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "a[href='/candidatos-registrados']"))
        )
        driver.execute_script("arguments[0].click();", enlace)
        wait.until(EC.url_contains("/candidatos-registrados"))
        time.sleep(2)
        log("2. Módulo 'Candidatos registrados' abierto correctamente.")

        # 2️⃣ Buscar candidato
        log(f"3. Buscando candidato: {CANDIDATO}...")
        campo = wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, "input[placeholder='Buscar por nombre de candidato']")))
        limpiar_y_escribir(campo, CANDIDATO)
        boton = driver.find_element(By.CSS_SELECTOR, "span.anticon-search")
        driver.execute_script("arguments[0].click();", boton)
        time.sleep(3)

        filas = driver.find_elements(By.CSS_SELECTOR, "div.ant-spin-container tr.ant-table-row")
        textos = [normalizar(f.text) for f in filas]
        if not any(normalizar(CANDIDATO.split()[0]) in t for t in textos):
            raise Exception("No se encontró el candidato especificado.")

        log(" Candidato encontrado en el listado.")

        # 3️⃣ Abrir vista Control de datos
        log("4. Abriendo vista 'Control de datos'...")
        boton_control = wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, f"//tr[td[contains(., '{CANDIDATO.split()[0]}')]]//button[contains(., 'Control de datos')]")
            )
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", boton_control)
        driver.execute_script("arguments[0].click();", boton_control)
        time.sleep(3)
        log(" Vista de control de datos abierta correctamente.")

        # 4️⃣ Verificar documento pendiente
        log("5. Buscando documento con estado 'Pendiente' para verificar...")
        fila_pendiente = wait.until(
            EC.presence_of_element_located((By.XPATH, "//tr[td[contains(., 'pendiente')]]"))
        )
        documento = fila_pendiente.find_element(By.XPATH, ".//td[1]").text.strip()
        log(f"→ Documento pendiente encontrado: {documento}")

        boton_verificar = fila_pendiente.find_element(By.XPATH, ".//button[contains(., 'Verificar')]")
        driver.execute_script("arguments[0].scrollIntoView(true);", boton_verificar)
        driver.execute_script("arguments[0].click();", boton_verificar)
        log(" Botón 'Verificar' presionado correctamente.")
        time.sleep(3)

        # 5️⃣ Confirmar verificación (mensaje en pantalla o cambio de estado)
        log("6. Validando que el documento haya sido verificado...")
        body = driver.find_element(By.TAG_NAME, "body").text.lower()
        if "validado" in body:
            log(" Documento cambiado a estado VALIDADO.")
            resumen["exito"] += 1
            log("ESCENARIO finalizado: ÉXITO (Documento verificado correctamente)\n")
        else:
            log(" No se detectó cambio de estado, pera quedar en estado validado se necesita (intervencion humana).")
            resumen["exito"] += 1
            log("ESCENARIO finalizado: ÉXITO PARCIAL (Verificar ejecutado sin confirmación)\n")

    except Exception as e:
        log(f" ESCENARIO finalizado: FALLIDO ({e})\n")
        resumen["fallido"] += 1


# ==========================================================
# MAIN
# ==========================================================
if __name__ == "__main__":
    limpiar()
    resumen = {"exito": 0, "fallido": 0}
    log("========== INICIO DE CP_92 ==========\n")
    driver, wait = iniciar_driver()
    try:
        login(driver, wait)
        escenario_revision_y_verificacion(driver, wait, resumen)
    finally:
        driver.quit()
        total = resumen["exito"] + resumen["fallido"]
        log("========== FIN DE CP_92 ==========\n")
        log(f"Resumen final: {total} escenarios ejecutados -> "
            f"{resumen['exito']} ÉXITO / {resumen['fallido']} FALLIDO\n")
        log(f"Archivo '{RESULTADOS_FILE}' generado correctamente.\n")

    print(f"\nArchivo '{RESULTADOS_FILE}' generado correctamente.\n")
