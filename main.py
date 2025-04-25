import sqlite3
import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication, QDialog, QMessageBox

from ui.config.logger_config import logger
from ui.config.paths import CORE_DB, STYLES
from ui.database.init_db_tables import init_databases
from ui.main_window import MainWindow
from ui.setup_page import AdminSetupDialog, LoginDialog, SetupPage
from ui.util.resize_window import size_and_center_window


class RootApp(QApplication):
    def __init__(self) -> None:
        super().__init__([])

    def _check_setup(self) -> str:
        if not CORE_DB.exists():
            return "company"
        try:
            conn = sqlite3.connect(CORE_DB)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM Company")
            if cursor.fetchone()[0] == 0:
                return "company"
            cursor.execute("SELECT COUNT(*) FROM Users WHERE UserPrivilegeLevel = 'Admin'")
            if cursor.fetchone()[0] == 0:
                return "admin"
            return "login"
        except Exception as e:
            logger.error(f"Error checking setup: {e}")
            return "company"

    def _run_setup(self) -> bool:
        setup_dialog = SetupPage()
        return setup_dialog.exec() == QDialog.DialogCode.Accepted

    def _run_admin_setup(self) -> bool:
        admin_dialog = AdminSetupDialog()
        return admin_dialog.exec() == QDialog.DialogCode.Accepted

    def _run_login(self) -> tuple[bool, str, str]:
        login_dialog = LoginDialog()
        if login_dialog.exec() == QDialog.DialogCode.Accepted:
            return True, *login_dialog.get_credentials()
        return False, "", ""

    def _load_stylesheet(self, path: Path) -> str:
        try:
            return path.read_text(encoding="utf-8")
        except Exception as err:
            logger.error(f"Failed to load stylesheet from {path}: {err}")
            return ""

    def _boot_app(self) -> None:
        init_databases()
        self.setStyleSheet(self._load_stylesheet(STYLES))

        setup_status = self._check_setup()

        if setup_status == "company":
            QMessageBox.information(None, "Setup", "Starting Software Configuration", QMessageBox.StandardButton.Ok)  # type: ignore
            if not self._run_setup():
                sys.exit(0)
            setup_status = self._check_setup()

        if setup_status == "admin":
            if not self._run_admin_setup():
                sys.exit(0)
            setup_status = self._check_setup()

        if setup_status == "login":
            success, username, password = self._run_login()
            if not success:
                logger.error("login unsuccessful, exiting.")
                sys.exit(0)
            conn = sqlite3.connect(CORE_DB)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Users WHERE UserName=? AND UserPassword=?", (username, password))
            if not cursor.fetchone():
                QMessageBox.warning(None, "Login Failed", "Invalid UserName or Password.")  # type: ignore
                sys.exit(0)

            # ---Fetch company name for title
            cursor.execute("SELECT CompanyName FROM Company LIMIT 1")
            company_row = cursor.fetchone()
            company_name = company_row[0] if company_row and company_row[0] else "Smart Healthcare Systems"
            self.processEvents()

        self.main_window = MainWindow(self, company_name, username)
        size_and_center_window(self.main_window, 0.85, 0.75)
        self.main_window.show()

        self.processEvents()
        sys.exit(self.exec())


if __name__ == "__main__":
    app = RootApp()
    app._boot_app()
