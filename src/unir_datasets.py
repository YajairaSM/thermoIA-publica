"""
unir_datasets.py — Une los 26 archivos CSV anuales en un solo dataset
Formato esperado de cada archivo:
    time,temperature,humidity,rain,pressure,wind_speed
    2000-01-01T00:00,22.5,87,0.3,1007.4,5.4

Uso:
    python unir_datasets.py

Coloca todos los CSV anuales en una carpeta llamada 'data_raw' dentro
del mismo directorio que este script, o ajusta la variable RAW_DIR.
"""

import pandas as pd
import glob
import sys
from pathlib import Path

# ── Colores ANSI ──────────────────────────────────────────────────────────────
RESET  = "\033[0m"
BOLD   = "\033[1m"
CYAN   = "\033[96m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
RED    = "\033[91m"
GRAY   = "\033[90m"
WHITE  = "\033[97m"

def linea(car="─", largo=55, color=CYAN):
    print(f"{color}{car * largo}{RESET}")

def ok(texto):
    print(f"  {GREEN}{RESET} {texto}")

def warn(texto):
    print(f"  {YELLOW}{RESET} {texto}")

def error(texto):
    print(f"  {RED}ERROR:{RESET} {texto}")

# ── Configuración ─────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent

RAW_DIR = BASE_DIR.parent / "data" / "raw"

OUTPUT_DIR = BASE_DIR.parent / "data" / "processed"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = OUTPUT_DIR / "dataset_unido_2.csv"

# ── Encabezado ────────────────────────────────────────────────────────────────
print()
linea("═")
print(f"{BOLD}{CYAN}  UNIFICADOR DE DATASETS — Open-Meteo{RESET}")
linea("═")
print()

# ── Verificar carpeta ─────────────────────────────────────────────────────────
if not RAW_DIR.exists():
    error(f"No se encontró la carpeta: {RAW_DIR}")
    print(f"\n  Crea la carpeta {BOLD}data_raw/{RESET} y coloca los archivos CSV dentro.")
    sys.exit(1)

# ── Buscar archivos CSV ───────────────────────────────────────────────────────
archivos = sorted(glob.glob(str(RAW_DIR / "*.csv")))

if not archivos:
    error(f"No se encontraron archivos CSV en: {RAW_DIR}")
    sys.exit(1)

print(f"  {WHITE}Archivos encontrados: {len(archivos)}{RESET}\n")

# ── Leer y unir ───────────────────────────────────────────────────────────────
dfs = []
errores_archivos = []

for archivo in archivos:
    nombre = Path(archivo).name
    try:
        df = pd.read_csv(archivo)

        # Verificar columnas esperadas
        columnas_esperadas = {"time", "temperature", "humidity", "rain", "pressure", "wind_speed"}
        columnas_archivo   = set(df.columns.str.strip().str.lower())

        if not columnas_esperadas.issubset(columnas_archivo):
            faltantes = columnas_esperadas - columnas_archivo
            warn(f"{nombre} — faltan columnas: {faltantes} — OMITIDO")
            errores_archivos.append(nombre)
            continue

        # Estandarizar nombres de columnas
        df.columns = df.columns.str.strip().str.lower()

        # Parsear fecha
        df["time"] = pd.to_datetime(df["time"], errors="coerce")

        # Reportar nulos en fecha
        nulos_fecha = df["time"].isna().sum()
        if nulos_fecha > 0:
            warn(f"{nombre} — {nulos_fecha} fechas inválidas eliminadas")
            df = df.dropna(subset=["time"])

        filas = len(df)
        anio  = df["time"].dt.year.mode()[0]
        ok(f"{nombre} — {filas:,} filas — año {anio}")
        dfs.append(df)

    except Exception as e:
        error(f"{nombre} — {e}")
        errores_archivos.append(nombre)

# ── Validar que hay datos ─────────────────────────────────────────────────────
if not dfs:
    error("No se pudo leer ningún archivo correctamente.")
    sys.exit(1)

# ── Concatenar ────────────────────────────────────────────────────────────────
print()
print(f"  {CYAN}Uniendo {len(dfs)} archivos...{RESET}")

dataset = pd.concat(dfs, ignore_index=True)
dataset = dataset.sort_values("time").reset_index(drop=True)

# Eliminar duplicados exactos
duplicados = dataset.duplicated(subset=["time"]).sum()
if duplicados > 0:
    warn(f"Se eliminaron {duplicados} filas duplicadas por fecha/hora")
    dataset = dataset.drop_duplicates(subset=["time"]).reset_index(drop=True)

# ── Resumen del dataset unido ─────────────────────────────────────────────────
print()
linea()
print(f"{BOLD}{CYAN}  RESUMEN DEL DATASET UNIDO{RESET}")
linea()
print(f"  Total filas        : {len(dataset):,}")
print(f"  Rango de fechas    : {dataset['time'].min()} → {dataset['time'].max()}")
print(f"  Años cubiertos     : {dataset['time'].dt.year.min()} – {dataset['time'].dt.year.max()}")
print()

# Verificar nulos
print(f"  {BOLD}Valores nulos por columna:{RESET}")
nulos = dataset.isnull().sum()
for col, n in nulos.items():
    if n > 0:
        pct = n / len(dataset) * 100
        warn(f"  {col}: {n} nulos ({pct:.1f}%)")
    else:
        ok(f"  {col}: sin nulos")

# ── Estadísticas básicas ──────────────────────────────────────────────────────
print()
print(f"  {BOLD}Estadísticas básicas:{RESET}")
stats = dataset[["temperature","humidity","rain","pressure","wind_speed"]].describe().round(2)
print(stats.loc[["min","mean","max"]].to_string())

# ── Guardar ───────────────────────────────────────────────────────────────────
print()
dataset.to_csv(OUTPUT_FILE, index=False)
ok(f"Dataset guardado en: {OUTPUT_FILE}")
print(f"  {GRAY}Tamaño: {OUTPUT_FILE.stat().st_size / 1024:.1f} KB{RESET}")

# ── Resumen de errores ────────────────────────────────────────────────────────
if errores_archivos:
    print()
    warn(f"Archivos con problemas ({len(errores_archivos)}):")
    for f in errores_archivos:
        print(f"    - {f}")

print()
linea("═")
print(f"{BOLD}{GREEN}  Proceso completado.{RESET}")
linea("═")
print()
