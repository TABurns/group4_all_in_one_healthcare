import sqlite3
import sys
from pathlib import Path

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication, QDialog, QMessageBox

from ui.config.logger_config import logger
from ui.config.paths import CORE_DB, STYLES
from ui.database.init_db_tables import init_databases
from ui.main_window import MainWindow
from ui.setup_page import AdminSetupDialog, LoginDialog, SetupPage
from ui.util.resize_window import size_and_center_window
from ui.working_area import WorkingArea


class RootApp(QApplication):
    def __init__(self) -> None:
        super().__init__([])
        self.working_area = None

    def check_setup(self) -> str:
        if not CORE_DB.exists():
            return "company"
        try:
            conn = sqlite3.connect(str(CORE_DB))
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

    def run_setup(self) -> bool:
        setup_dialog = SetupPage()
        return setup_dialog.exec() == QDialog.DialogCode.Accepted

    def run_admin_setup(self) -> bool:
        admin_dialog = AdminSetupDialog()
        return admin_dialog.exec() == QDialog.DialogCode.Accepted

    def run_login(self) -> tuple[bool, str, str]:
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

        setup_status = self.check_setup()

        if setup_status == "company":
            QMessageBox.information(self.activeWindow(), "Setup", "Starting Software Configuration", QMessageBox.StandardButton.Ok)  # type: ignore
            if not self.run_setup():
                sys.exit(0)
            setup_status = self.check_setup()

        if setup_status == "admin":
            if not self.run_admin_setup():
                sys.exit(0)
            setup_status = self.check_setup()

        if setup_status == "login":
            success, username, password = self.run_login()
            if not success:
                sys.exit(0)
            conn = sqlite3.connect(str(CORE_DB))
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Users WHERE UserName=? AND UserPassword=?", (username, password))
            if not cursor.fetchone():
                QMessageBox.warning(self.activeWindow(), "Login Failed", "Invalid UserName or Password.")  # type: ignore
                sys.exit(0)

            # Fetch company name for title
            cursor.execute("SELECT CompanyName FROM Company LIMIT 1")
            company_row = cursor.fetchone()
            company_name = company_row[0] if company_row and company_row[0] else "Healthcare App"

        self.working_area = WorkingArea()
        main_window = MainWindow(self, company_name, username)
        QTimer.singleShot(10, main_window.show)
        size_and_center_window(main_window, 0.85, 0.75)
        self.processEvents()
        sys.exit(self.exec())


if __name__ == "__main__":
    app = RootApp()
    app._boot_app()
