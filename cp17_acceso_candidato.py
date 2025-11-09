# ============================================================
# CP_17 – Acceso por rol Candidato (Seguridad)
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

# ============================================================
# CONFIGURACIÓN
# ============================================================
URL_BASE = "https://helpful-youth-production-1d3f.up.railway.app/"
RESULTADOS_FILE = "resultados_CP17.txt"

USUARIOS = {
    "financiero": {"email": "financiero@ues.edu.sv", "password": "password"},
    "admin": {"email": "admin@ues.edu.sv", "password": "password"}
}

# ============================================================
# FUNCIONES BASE
# ============================================================
def iniciar_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-notifications")
    service = ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    wait = WebDriverWait(driver, 60)
    actions = ActionChains(driver)
    return driver, wait, actions

def registrar_resultado(escenario, resultado):
    with open(RESULTADOS_FILE, "a", encoding="utf-8") as f:
        f.write(f"{datetime.now().strftime('%H:%M:%S')} | {escenario}: {resultado}\n")

def login(driver, wait, email, password):
    driver.get(URL_BASE)
    wait.until(EC.presence_of_element_located((By.ID, "basic_email"))).send_keys(email)
    driver.find_element(By.ID, "basic_password").send_keys(password)
    driver.find_element(By.CSS_SELECTOR, ".ant-btn").click()
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    time.sleep(3)
    print(f"Inicio de sesión exitoso: {email}")

# ============================================================
# CREAR Y VALIDAR PERSONA “Jose Lucero”
# ============================================================
def crear_y_validar_persona(driver, wait, actions):
    print("2. Abriendo módulo Usuarios...")
    usuarios_link = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Usuarios")))
    actions.move_to_element(usuarios_link).click().perform()
    time.sleep(3)

    print("3. Presionando + Crear...")
    wait.until(EC.element_to_be_clickable(
        (By.XPATH, "//button[contains(., 'Crear') and contains(@class,'ant-btn-lg')]"))
    ).click()
    time.sleep(1)

    print("4. Llenando formulario con nombre fijo 'Jose Lucero'...")
    datos = {
        "name": "Jose Lucero",
        "email": f"jose{int(time.time())}@gmail.com"
    }

    wait.until(EC.presence_of_element_located((By.ID, "createUser_name"))).send_keys(datos["name"])
    driver.find_element(By.ID, "createUser_email").send_keys(datos["email"])

    print("5. Seleccionando rol y escuela...")
    try:
        driver.find_element(By.ID, "createUser_role").click()
        wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, ".ant-select-item-option-content"))).click()
        driver.find_elements(By.CSS_SELECTOR, "div.ant-select-selector")[1].click()
        wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, ".ant-select-item-option-content"))).click()
    except:
        print("   → Guardando...")

    print("6. Guardando registro...")
    guardar_btn = wait.until(EC.element_to_be_clickable(
        (By.CSS_SELECTOR, "button.ant-btn.ant-btn-primary")))
    guardar_btn.click()
    wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, "ant-modal-wrap")))
    time.sleep(2)

    print("7. Buscando registro 'Jose Lucero' mediante buscador...")
    try:
        search_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".ant-input")))
        search_input.clear()
        search_input.send_keys("Jose Lucero")

        search_button = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".ant-input-search-button")))
        driver.execute_script("arguments[0].scrollIntoView(true);", search_button)
        driver.execute_script("arguments[0].click();", search_button)
        time.sleep(3)

        for _ in range(10):
            if "Jose Lucero" in driver.find_element(By.TAG_NAME, "body").text:
                print("   → Registro encontrado en la tabla.")
                driver.save_screenshot("evidencias_cp17_usuario_creado.png")
                return "ÉXITO (Usuario creado y visible: Jose Lucero)"
            time.sleep(2)
        return "FALLIDO (No se encontró 'Jose Lucero' en la tabla tras búsqueda)"
    except Exception as e:
        return f"FALLIDO (Error al buscar: {e})"

# ============================================================
# ACTUALIZAR PERSONA (cambiar nombre a “Jose Lucero Barrera”)
# ============================================================
def actualizar_persona(driver, wait):
    print("8. Intentando editar el registro 'Jose Lucero'...")
    try:
        filas = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "tr.ant-table-row")))
        objetivo = None
        for fila in filas:
            if "Jose Lucero" in fila.text:
                objetivo = fila
                break

        if not objetivo:
            return "FALLIDO (No se encontró 'Jose Lucero' en la tabla)"

        print("   → Seleccionando fila y presionando Editar...")
        driver.execute_script("arguments[0].scrollIntoView(true);", objetivo)
        time.sleep(1)
        driver.execute_script("arguments[0].click();", objetivo)

        boton_editar = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(., 'Editar')]")))
        driver.execute_script("arguments[0].click();", boton_editar)

        print("9. Esperando que el formulario de edición aparezca...")
        for _ in range(15):
            visible = driver.execute_script("""
                const modal = document.querySelector('.ant-modal-content');
                return modal && modal.offsetParent !== null;
            """)
            if visible:
                break
            time.sleep(0.5)

        posibles_selectores = [
            "#updateUser_name",
            "#editUser_name",
            "#personal-info_first_name",
            "input[placeholder='Nombre']",
            "input[aria-label='Nombre']"
        ]
        campo = None
        for _ in range(10):
            for selector in posibles_selectores:
                try:
                    campo = driver.find_element(By.CSS_SELECTOR, selector)
                    if campo.is_displayed():
                        break
                except:
                    pass
            if campo:
                break
            time.sleep(0.5)

        if not campo:
            return "FALLIDO (No se cargó el formulario de edición)"

        print("10. Editando nombre a 'Jose Lucero Barrera'...")
        campo.clear()
        campo.send_keys("Jose Lucero Barrera")

        print("11. Guardando cambios...")
        guardar_btn = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(., 'Guardar') or contains(., 'Actualizar')]")))
        driver.execute_script("arguments[0].click();", guardar_btn)

        try:
            boton_si = wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//button[span[text()='Si']]")))
            driver.execute_script("arguments[0].click();", boton_si)
            print("   → Se confirmó el guardado.")
        except:
            print("   → Continuando...")

        time.sleep(3)
        print("12. Validando actualización...")
        driver.refresh()
        wait.until(EC.presence_of_element_located((By.LINK_TEXT, "Usuarios"))).click()
        time.sleep(3)

        search_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".ant-input")))
        search_input.clear()
        search_input.send_keys("Jose Lucero Barrera")

        search_button = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".ant-input-search-button")))
        driver.execute_script("arguments[0].click();", search_button)
        time.sleep(4)

        if "Jose Lucero Barrera" in driver.find_element(By.TAG_NAME, "body").text:
            print("   → Nombre actualizado correctamente.")
            driver.save_screenshot("evidencias_cp17_despues_edicion.png")
            return "ÉXITO (Actualización confirmada: Jose Lucero Barrera)"
        else:
            return "FALLIDO (El registro no se muestra tras recargar la tabla)"
    except Exception as e:
        return f"FALLIDO (Error al actualizar: {e})"

# ============================================================
# ESCENARIO 1 – FINANCIERO (sin permisos)
# ============================================================
def escenario_financiero():
    print("------------------------------------------------------")
    print("ESCENARIO 1: FINANCIERO - Sin permisos")
    print("------------------------------------------------------")
    driver, wait, actions = iniciar_driver()
    try:
        print("1. Iniciando sesión como financiero...")
        login(driver, wait, USUARIOS["financiero"]["email"], USUARIOS["financiero"]["password"])
        try:
            driver.find_element(By.LINK_TEXT, "Usuarios").click()
            time.sleep(2)
            resultado = "FALLIDO (El usuario sin permiso accedió al módulo)"
        except:
            resultado = "ÉXITO (No puede acceder al módulo Usuarios)"
    except Exception as e:
        resultado = f"FALLIDO (Error inesperado: {e})"
    finally:
        registrar_resultado("Escenario 1 - Financiero", resultado)
        driver.quit()
        print(f"ESCENARIO 1 finalizado: {resultado}\n")

# ============================================================
# ESCENARIO 2 – ADMIN (crear y actualizar persona)
# ============================================================
def escenario_admin():
    print("------------------------------------------------------")
    print("ESCENARIO 2: ADMIN - Crear y actualizar persona")
    print("------------------------------------------------------")
    driver, wait, actions = iniciar_driver()
    try:
        print("1. Iniciando sesión como admin...")
        login(driver, wait, USUARIOS["admin"]["email"], USUARIOS["admin"]["password"])

        resultado_crear = crear_y_validar_persona(driver, wait, actions)
        print(resultado_crear)

        resultado_actualizar = actualizar_persona(driver, wait)
        print(resultado_actualizar)

        resultado_final = f"{resultado_crear} | {resultado_actualizar}"
    except Exception as e:
        resultado_final = f"FALLIDO (Error general: {e})"
    finally:
        registrar_resultado("Escenario 2 - Admin", resultado_final)
        driver.quit()
        print(f"ESCENARIO 2 finalizado: {resultado_final}\n")

# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    print("========== INICIO DE CP_17 ==========\n")
    open(RESULTADOS_FILE, "w", encoding="utf-8").close()
    escenario_financiero()
    escenario_admin()
    print("========== FIN DE CP_17 ==========")
