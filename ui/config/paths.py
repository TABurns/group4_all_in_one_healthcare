from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]

UI_DIR = ROOT_DIR / "ui"
CONFIG_DIR = UI_DIR / "config"
UTIL_DIR = UI_DIR / "util"


STYLES = CONFIG_DIR / "styles.css"

LOG_FILE = ROOT_DIR / "logs" / "log.log"
