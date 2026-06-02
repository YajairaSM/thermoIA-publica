import os
import time
import requests
import pandas as pd

# ============================================
# CONFIGURACION
# ============================================

LATITUDE = 8.4273
LONGITUDE = -82.4309

START_YEAR = 1990
END_YEAR = 1999

OUTPUT_FOLDER = "data-api"

# Variables climáticas
HOURLY_VARIABLES = [
    "temperature_2m",
    "relative_humidity_2m",
    "precipitation",
    "surface_pressure",
    "wind_speed_10m"
]

# ============================================
# CREAR CARPETA
# ============================================

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# ============================================
# DESCARGA POR AÑO
# ============================================

for year in range(START_YEAR, END_YEAR + 1):

    print(f"\nDescargando datos del año {year}...")

    url = "https://archive-api.open-meteo.com/v1/archive"

    params = {
        "latitude": LATITUDE,
        "longitude": LONGITUDE,

        "start_date": f"{year}-01-01",
        "end_date": f"{year}-12-31",

        "hourly": HOURLY_VARIABLES,

        "timezone": "America/Panama"
    }

    try:

        response = requests.get(url, params=params, timeout=120)

        # Verificar status
        response.raise_for_status()

        data = response.json()

        # Verificar existencia de datos
        if "hourly" not in data:
            print(f"No hay datos para {year}")
            continue

        hourly = data["hourly"]

        # Crear DataFrame
        df = pd.DataFrame({
            "time": hourly["time"],
            "temperature": hourly["temperature_2m"],
            "humidity": hourly["relative_humidity_2m"],
            "rain": hourly["precipitation"],
            "pressure": hourly["surface_pressure"],
            "wind_speed": hourly["wind_speed_10m"]
        })

        # Nombre archivo
        filename = os.path.join(
            OUTPUT_FOLDER,
            f"weather_{year}.csv"
        )

        # Guardar CSV
        df.to_csv(filename, index=False)

        print(f"Guardado: {filename}")
        print(f"Filas: {len(df)}")

    except Exception as e:

        print(f"ERROR en {year}")
        print(e)

    # Espera para evitar spam API
    time.sleep(1)

print("\nProceso terminado.") 

"""
import os
import requests
import pandas as pd

# ============================================
# CONFIG
# ============================================

LATITUDE = 8.4273
LONGITUDE = -82.4309

OUTPUT_FOLDER = "data-api"

HOURLY_VARIABLES = [
    "temperature_2m",
    "relative_humidity_2m",
    "precipitation",
    "surface_pressure",
    "wind_speed_10m"
]

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# ============================================
# API
# ============================================

url = "https://archive-api.open-meteo.com/v1/archive"

params = {
    "latitude": LATITUDE,
    "longitude": LONGITUDE,

    "start_date": "2026-01-01",
    "end_date": "2026-05-22",

    "hourly": ",".join(HOURLY_VARIABLES),

    "timezone": "America/Panama"
}

try:

    response = requests.get(
        url,
        params=params,
        timeout=(30, 300)
    )

    response.raise_for_status()

    data = response.json()

    if "hourly" not in data:
        print("No hay datos disponibles")
        exit()

    hourly = data["hourly"]

    df = pd.DataFrame({
        "time": hourly.get("time", []),
        "temperature": hourly.get("temperature_2m", []),
        "humidity": hourly.get("relative_humidity_2m", []),
        "rain": hourly.get("precipitation", []),
        "pressure": hourly.get("surface_pressure", []),
        "wind_speed": hourly.get("wind_speed_10m", [])
    })

    filename = os.path.join(
        OUTPUT_FOLDER,
        "weather_2026_jan_may.csv"
    )

    df.to_csv(filename, index=False)

    print(f"Archivo guardado: {filename}")
    print(f"Total filas: {len(df)}")

except Exception as e:

    print("ERROR")
    print(e)
""" 