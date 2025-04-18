import sqlite3

from ui.config.logger_config import logger
from ui.config.paths import BILLING_DB, CORE_DB, PATIENT_DB

DB_MAP = {
    "core": CORE_DB,
    "patients": PATIENT_DB,
    "billing": BILLING_DB,
}

def write_to_database(db_key: str, table: str, data: dict) -> bool:
    db_path = DB_MAP.get(db_key)
    if not db_path or not data:
        return False

    try:
        with sqlite3.connect(str(db_path)) as conn:
            cursor = conn.cursor()
            columns = ", ".join(data.keys())
            placeholders = ", ".join(["?"] * len(data))
            values = tuple(data.values())
            cursor.execute(f"INSERT INTO {table} ({columns}) VALUES ({placeholders})", values)  # noqa: S608
            conn.commit()
        return True
    except Exception as e:
        logger.error(f"Error writing to {table} in {db_key} db: {e}")
        return False
