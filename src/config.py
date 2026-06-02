from pathlib import Path

# ── Ruta base del proyecto ──────────────────────────────────────────
# Funciona tanto en scripts .py como en notebooks Jupyter
try:
    BASE_DIR = Path(__file__).resolve().parent.parent
except NameError:
    BASE_DIR = Path().resolve().parent

# ── Carpetas principales ────────────────────────────────────────────
DATA_RAW       = BASE_DIR / "data" / "raw"
DATA_PROCESSED = BASE_DIR / "data" / "processed"
MODELS_DIR     = BASE_DIR / "models"
REPORTS_DIR    = BASE_DIR / "reports"
APP_DIR        = BASE_DIR / "app"

# ── Archivos clave ──────────────────────────────────────────────────
RAW_CSV        = DATA_RAW       / "david_1990_2026_raw.csv"
CLEAN_CSV      = DATA_PROCESSED / "dataset_limpio.csv"
FEATURES_CSV   = DATA_PROCESSED / "dataset_features.csv"
