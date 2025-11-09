"""
CP_79 - Validar restricción de creación duplicada de empleado (Admin)
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager

# =========================
# CONFIGURACIÓN
# =========================
URL_BASE = "https://helpful-youth-production-1d3f.up.railway.app/"
ADMIN = {"email": "admin@ues.edu.sv", "password": "password"}

DATOS = {
    "name": "José Lucero",
    "email": f"jose.lucero_{int(time.time())}@ues.edu.sv"  # correo único para el primer intento
}

MENSAJES_DUPLICADOS = ["ya existe", "en uso", "duplicado", "único", "anteriormente", "existente"]
MENSAJES_EXITO = ["creado", "éxito", "registrado", "guardado", "usuario creado", "empleado creado"]

# =========================
# FUNCIONES
# =========================
def iniciar_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    service = ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    wait = WebDriverWait(driver, 25)
    actions = ActionChains(driver)
    return driver, wait, actions


def login_admin(driver, wait):
    print("1. Iniciando sesión como admin...")
    driver.get(URL_BASE)
    wait.until(EC.presence_of_element_located((By.ID, "basic_email"))).send_keys(ADMIN["email"])
    driver.find_element(By.ID, "basic_password").send_keys(ADMIN["password"])
    driver.find_element(By.CSS_SELECTOR, ".ant-btn").click()
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    print(f"Inicio de sesión exitoso: {ADMIN['email']}")
    time.sleep(2)


def leer_mensaje_flotante(driver):
    """Busca mensajes de éxito o error sin mostrarlos en consola"""
    try:
        for _ in range(6):
            elementos = driver.find_elements(
                By.CSS_SELECTOR,
                ".ant-message, .ant-message-notice-content, .ant-notification-notice-message, .ant-modal-confirm-content, .ant-modal-body"
            )
            for e in elementos:
                texto = e.text.strip().lower().replace("aceptar", "")
                if texto and len(texto) > 4:
                    return texto
            time.sleep(1)
        return ""
    except:
        return ""


def validar_en_tabla(driver, nombre):
    """Verifica si el nombre aparece en la tabla de usuarios."""
    try:
        time.sleep(2)
        tabla = driver.find_element(By.TAG_NAME, "body").text.lower()
        return nombre.lower() in tabla
    except:
        return False


def crear_empleado(driver, wait, actions, email=None):
    """Crea o intenta crear un empleado."""
    print("→ Abriendo módulo Usuarios...")
    usuarios_link = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Usuarios")))
    actions.move_to_element(usuarios_link).click().perform()
    time.sleep(2)

    print("→ Presionando + Crear...")
    wait.until(EC.element_to_be_clickable(
        (By.XPATH, "//button[contains(., 'Crear') and contains(@class,'ant-btn-lg')]"))
    ).click()
    time.sleep(1)

    correo = email if email else DATOS["email"]

    wait.until(EC.presence_of_element_located((By.ID, "createUser_name"))).send_keys(DATOS["name"])
    driver.find_element(By.ID, "createUser_email").send_keys(correo)

    driver.find_element(By.ID, "createUser_role").click()
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".ant-select-item-option-content"))).click()
    driver.find_element(By.CSS_SELECTOR, "div.ant-select-selector").click()
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".ant-select-item-option-content"))).click()
    time.sleep(1)

    print("→ Guardando registro...")
    guardar_btn = wait.until(EC.element_to_be_clickable(
        (By.CSS_SELECTOR, "button.ant-btn.ant-btn-primary"))
    )
    guardar_btn.click()
    time.sleep(3)

    mensaje = leer_mensaje_flotante(driver)
    texto_total = mensaje.lower()

    for msg in MENSAJES_EXITO:
        if msg in texto_total:
            print(" Registro creado correctamente.")
            return "CREADO"

    for msg in MENSAJES_DUPLICADOS:
        if msg in texto_total:
            print(" Duplicado detectado correctamente.")
            return "DUPLICADO"

    print("→ Verificando si el registro aparece en la tabla...")
    if validar_en_tabla(driver, DATOS["name"]):
        print(" Registro visible en la tabla (creación confirmada).")
        return "CREADO"

    print(" No se detectó registro ni mensaje visible.")
    return "SIN_MENSAJE"


# =========================
# ESCENARIO PRINCIPAL
# =========================
def escenario_duplicado_empleado():
    print("------------------------------------------------------")
    print("ESCENARIO: ADMIN - Restricción de creación duplicada de empleado")
    print("------------------------------------------------------")

    driver, wait, actions = iniciar_driver()
    resultado = "FALLIDO"

    try:
        login_admin(driver, wait)

        print("\n2. Creando empleado...")
        r1 = crear_empleado(driver, wait, actions)
        print(f"   → Resultado primer intento: {r1}")

        print("\nREFRESCANDO MODULO PARA SEGUNDA CREACION...")
        driver.refresh()
        time.sleep(4)

        print("\n3. Intentando crear el mismo empleado nuevamente...")
        r2 = crear_empleado(driver, wait, actions, email=DATOS["email"])
        print(f"   → Resultado segundo intento: {r2}")

        if r1 == "CREADO" and r2 == "DUPLICADO":
            resultado = "ÉXITO (Sistema bloquea duplicado correctamente)"
        elif r1 == "CREADO" and r2 == "CREADO":
            resultado = "FALLIDO (El sistema permitió duplicado)"
        elif r1 == "CREADO" and r2 == "SIN_MENSAJE":
            resultado = "POSIBLE ÉXITO (El sistema bloqueó pero sin mostrar mensaje)"
        else:
            resultado = f"FALLIDO (Resultados inesperados: r1={r1}, r2={r2})"

    except Exception as e:
        print(f" Error inesperado en escenario: {e}")
        resultado = "FALLIDO (Error en ejecución)"
    finally:
        driver.quit()
        print(f"\nESCENARIO finalizado: {resultado}\n")


# =========================
# MAIN
# =========================
if __name__ == "__main__":
    print("========== INICIO DE CP_79 ==========\n")
    escenario_duplicado_empleado()
    print("========== FIN DE CP_79 ==========\n")
