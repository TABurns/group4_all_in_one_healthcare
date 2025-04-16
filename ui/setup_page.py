import sqlite3

import simplematch as sm
from PySide6.QtWidgets import QDialog, QDialogButtonBox, QFormLayout, QLineEdit, QMessageBox, QVBoxLayout

from ui.config.paths import SETUP_DB


class SetupPage(QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Initial Setup")
        self.setModal(True)
        self.setObjectName("SetupDialog")

        self.main_layout = QVBoxLayout(self)

        form_layout = QFormLayout()
        self.company_name_input = QLineEdit(self)
        self.company_name_input.setObjectName("LineEdit")
        form_layout.addRow("Company Name:  ", self.company_name_input)

        self.company_address_input = QLineEdit(self, placeholderText="601 College St, Clarksville, TN 37044")
        self.company_address_input.setObjectName("LineEdit")
        form_layout.addRow("Company Address:  ", self.company_address_input)

        self.company_email_input = QLineEdit(self, placeholderText="company@yahoo.com")
        self.company_email_input.setObjectName("LineEdit")
        form_layout.addRow("Company Email:  ", self.company_email_input)

        self.company_phone_input = QLineEdit(self, placeholderText="(###) ###-####")
        self.company_phone_input.setObjectName("LineEdit")
        form_layout.addRow("Company Phone:  ", self.company_phone_input)

        self.main_layout.addLayout(form_layout)

        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.setObjectName("SetupBTN")
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.main_layout.addWidget(self.button_box)

    def accept(self) -> None:
        company_name = self.company_name_input.text().strip()
        company_email = self.company_email_input.text().strip()
        company_address = self.company_address_input.text().strip()
        company_phone = self.company_phone_input.text().strip()

        if not company_name:
            QMessageBox.warning(self, "Input Error", "Hospital name is required.")
            return

        if not company_address:
            QMessageBox.warning(self, "Input Error", "Company Address is required.")
            return

        company_email = self.company_email_input.text().strip()
        if not company_email:
            QMessageBox.warning(self, "Input Error", "Company email is required.")
            return

        # ---Validate company email, expected pattern: username@domain
        email_pattern = "{username}@{domain}"
        email_result = sm.match(email_pattern, company_email)
        if not email_result:
            QMessageBox.warning(self, "Invalid Input", "Company email must be in the format username@domain.")
            return

        # ---Ensure the domain contains a period (e.g., yahoo.com)
        if "." not in email_result.get("domain", ""):
            QMessageBox.warning(self, "Invalid Input", "Company email domain must contain a period (e.g., yahoo.com).")
            return

        if not company_phone:
            QMessageBox.warning(self, "Input Error", "Company phone is required.")
            return

        # ---Validate company phone format using simplematch with expected pattern: (###) ###-####
        phone_pattern = "({area}) {prefix}-{line}"
        match_result = sm.match(phone_pattern, company_phone)
        if not match_result:
            QMessageBox.warning(self, "Invalid Input", "Company phone must be in the format (###) ###-####.")
            return

        # ---Verify that each input contains the correct number of digits and only digits
        if len(match_result.get("area", "")) != 3 or not match_result["area"].isdigit():
            QMessageBox.warning(self, "Invalid Input", "Area code must be exactly 3 digits.")
            return
        if len(match_result.get("prefix", "")) != 3 or not match_result["prefix"].isdigit():
            QMessageBox.warning(self, "Invalid Input", "Prefix must be exactly 3 digits.")
            return
        if len(match_result.get("line", "")) != 4 or not match_result["line"].isdigit():
            QMessageBox.warning(self, "Invalid Input", "Line number must be exactly 4 digits.")
            return

        try:
            SETUP_DB.parent.mkdir(parents=True, exist_ok=True)
            conn = sqlite3.connect(str(SETUP_DB))
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS settings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_name TEXT,
                    company_address TEXT,
                    company_email TEXT,
                    company_phone TEXT
                );
            """)
            cursor.execute("DELETE FROM settings")
            cursor.execute(
                "INSERT INTO settings (company_name, company_address, company_email, company_phone) VALUES (?, ?, ?, ?)",
                (company_name, company_address, company_email, company_phone),
            )
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error saving setup configuration to SQLite: {e}")
            return

        super().accept()
