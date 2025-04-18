from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]

UI_DIR = ROOT_DIR / "ui"
CONFIG_DIR = UI_DIR / "config"
UTIL_DIR = UI_DIR / "util"
RESOURCE_DIR = UI_DIR / "resources"
DATABASE_DIR = UI_DIR / "database"

STYLES = CONFIG_DIR / "styles.css"

LOG_FILE = ROOT_DIR / "logs" / "log.log"

ROOT_BACKGROUND = RESOURCE_DIR / "gooddr.png"

DB_ROOT = DATABASE_DIR / "db"
CORE_DB = DB_ROOT / "core.db"
PATIENT_DB = DB_ROOT / "patients.db"
BILLING_DB = DB_ROOT / "billing.db"

LOG_DIR = ROOT_DIR / "logs"

for path in [RESOURCE_DIR, CONFIG_DIR, UTIL_DIR, DATABASE_DIR, DB_ROOT, LOG_DIR]:
    path.mkdir(parents=True, exist_ok=True)
