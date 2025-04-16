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
SETUP_DB = DATABASE_DIR / "setup.db"
