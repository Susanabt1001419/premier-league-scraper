####Hay que instalar en anaconda prompt selenium para que funcione
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import re
from selenium.webdriver.common.by import By
from tqdm import tqdm
#%% Para iniciar el navegador
def iniciar_navegador(ruta_driver, url):
    options = Options()
    options.add_argument("--start-maximized")
    
    service = Service(executable_path=ruta_driver)
    driver = webdriver.Chrome(service=service, options=options)
    
    driver.get(url)
    return driver

# Ruta al ChromeDriver
ruta_driver = "C:/Users/USER/Desktop/Pregrado/Semestre 7/Analitica 1/chromedriver-win64/chromedriver.exe"

# URL de WhoScored Premier League
url_premier = "https://www.whoscored.com/Regions/252/Tournaments/2/England-Premier-League"

# Iniciar navegador
driver = iniciar_navegador(ruta_driver, url_premier)

# Esperar a que cargue la página
time.sleep(5)
# %% Para extraer los datos y colocarlos en un archivo csv (goles a favor, en contra, partidos ganados, perdidos, etc)
import pandas as pd

# Espera adicional por seguridad
time.sleep(5)

# Buscamos las filas de la tabla
filas = driver.find_elements(By.CSS_SELECTOR, "table#standings-23400-grid tbody tr")

# Lista para guardar los datos
datos = []

for fila in filas:
    celdas = fila.find_elements(By.TAG_NAME, "td")
    if len(celdas) >= 10:  # Aseguramos que haya suficientes columnas
        equipo = celdas[0].text
        equipo = re.sub(r"^\d+", "", equipo).strip()##Para quitar los numeros delante del nombre del equipo
        pj = celdas[1].text
        ganados = celdas[2].text
        empatados = celdas[3].text
        perdidos = celdas[4].text
        gf = celdas[5].text
        ga = celdas[6].text
        gd = celdas[7].text
        puntos = celdas[8].text
        datos.append([equipo, pj, ganados, empatados, perdidos, gf, ga, gd, puntos])

# Convertimos a DataFrame
df_tabla = pd.DataFrame(datos, columns=["Equipo", "PJ", "G", "E", "P", "GF", "GA", "GD", "Pts"])

# Mostramos los primeros resultados
print(df_tabla.head())
########## Para el archivo csv
df_tabla.to_csv("C:/Users/USER/Desktop/Pregrado/Semestre 7/Analitica 1/tabla_posiciones_premier.csv", index=False, encoding='utf-8-sig')##Hay que cambiar la url para donde quiera que se guarde en su computador
#%%
# %% Obtener en nombre y las url de cada equipo para entrar a estadisticas más profundas

equipos = []

# Volvemos a buscar las filas de la tabla por si el driver se ha reiniciado
filas = driver.find_elements(By.CSS_SELECTOR, "table#standings-23400-grid tbody tr")

for fila in filas:
    try:
        # Buscamos el enlace dentro del primer <td>
        enlace = fila.find_element(By.CLASS_NAME, "team-link")
        nombre = enlace.text
        url = enlace.get_attribute("href")

        equipos.append([nombre, url])
    except:
        continue

# Mostramos los primeros
for nombre, url in equipos[:5]:
    print(f"{nombre} → {url}")
#%%Entremos solo a un equipo al que queramos 
nombre_equipo, url_equipo = equipos[0]  # O el que quieras visitar
print(f"Entrando a: {nombre_equipo} → {url_equipo}")

# Ir a la página del equipo
driver.get(url_equipo)

# Esperamos a que cargue la página completamente
time.sleep(10)  # Podrías usar WebDriverWait más adelante para mejorar esto
#%% Ahora hagamos lo mismo con todos los equipos para extraer sus estadisticas 
estadisticas = []

for nombre, url in tqdm(equipos, desc= "Extrayendo estadisticas de equipos"):
    driver.get(url)
    time.sleep(10)
    
    try:
        # Buscar la tabla de estadísticas por torneo
        tabla = driver.find_element(By.ID, "top-team-stats-summary-content")
        
        # Seleccionar la primera fila (Premier League)
        fila = tabla.find_elements(By.TAG_NAME, "tr")[0]
        
        # Extraer estadísticas específicas por clase
        shots = fila.find_element(By.CLASS_NAME, "shotsPerGame").text
        posesion_pase = fila.find_element(By.CLASS_NAME, "possession").text
        pases = fila.find_element(By.CLASS_NAME, "passSuccess").text
        aereos = fila.find_element(By.CLASS_NAME, "aerialWonPerGame").text
        
        # Guardamos los datos en la lista estadisticas 
        estadisticas.append([nombre, shots,posesion_pase,pases,aereos])
    
    except Exception as e:
        print(f"❌ Error al procesar {nombre}: {e}")
        estadisticas.append([nombre, None, None, None, None])
        continue
    
# Convertimos a DataFrame
df_estadisticas = pd.DataFrame(estadisticas, columns=["Equipo", "Tiros al arco","Posesión", "Precisión de Pase", "Duelos Aéreos"])

# Mostramos los primeros resultados
print(df_estadisticas.head())
#%% Unir con marge ambos dataframes
df_merged = pd.merge(df_tabla, df_estadisticas, on="Equipo", how="inner")

# Revisar resultado
print(df_merged.head())

# Exportar
df_merged.to_csv("C:/Users/USER/Desktop/Pregrado/Semestre 7/Analitica 1/datos_combinados_premier.csv", index=False, encoding="utf-8-sig")
print("✅ Archivo 'datos_combinados_premier.csv' exportado correctamente.")
