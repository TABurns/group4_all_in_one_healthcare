import simplematch as sm
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QDialogButtonBox, QFormLayout, QInputDialog, QLineEdit, QMessageBox, QVBoxLayout

from ui.config.logger_config import logger
from ui.database.write_to_db import write_to_database
from ui.util.resize_window import size_and_center_window


class SetupPage(QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Initial Setup")
        self.setModal(True)
        self.setObjectName("SetupDialog")
        size_and_center_window(self, 0.40, 0.35)

        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

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

        main_layout.addLayout(form_layout)

        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.setObjectName("SetupBTN")
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        main_layout.addWidget(self.button_box)

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
            company_data = {
                "CompanyName": company_name,
                "CompanyAddress": company_address,
                "CompanyEmail": company_email,
                "CompanyPhone": company_phone,
            }
            success = write_to_database("core", "Company", company_data)
            if not success:
                QMessageBox.critical(self, "Error", "Failed to save company info to database.")
                return
        except Exception as e:
            logger.error(f"Error saving setup configuration to SQLite: {e}")
            return

        super().accept()


class AdminSetupDialog(QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Admin User Setup")
        self.setModal(True)
        self.setSizeGripEnabled(True)
        self.setObjectName("SetupDialog")
        size_and_center_window(self, 0.40, 0.35)

        form_layout = QFormLayout()

        self.username = QLineEdit(self)
        self.username.setObjectName("LineEdit")
        self.email = QLineEdit(self)
        self.email.setObjectName("LineEdit")
        self.password = QLineEdit(self)
        self.password.setObjectName("LineEdit")

        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        form_layout.addRow("Admin Username:", self.username)
        form_layout.addRow("Admin Email:", self.email)
        form_layout.addRow("Admin Password:", self.password)

        main_layout = QVBoxLayout(self)
        main_layout.addLayout(form_layout)

        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.setObjectName("SetupBTN")
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        main_layout.addWidget(self.button_box)

    def get_data(self) -> tuple[str, str, str]:
        username = self.username.text().strip()
        email = self.email.text().strip()
        password = self.password.text().strip()

        if not username:
            QMessageBox.warning(self, "Input Error", "Username is required.")
            return "", "", ""
        if not email:
            QMessageBox.warning(self, "Input Error", "Email is required.")
            return "", "", ""
        if not password:
            QMessageBox.warning(self, "Input Error", "Password is required.")
            return "", "", ""

        admin_data = {
            "UserName": username,
            "UserEmail": email,
            "UserPosition": "Admin",
            "UserPrivilegeLevel": "Admin",
        }
        write_to_database("core", "Users", admin_data)
        return username, email, password


class LoginDialog(QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Login")
        self.setModal(True)
        self.setObjectName("SetupDialog")
        size_and_center_window(self, 0.30, 0.25)

        form_layout = QFormLayout(self)
        self.username = QLineEdit(self)
        self.username.setObjectName("LineEdit")
        self.password = QLineEdit(self)
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        self.password.setObjectName("LineEdit")
        form_layout.addRow("Username:", self.username)
        form_layout.addRow("Password:", self.password)

        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.setObjectName("SetupBTN")
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addLayout(form_layout)
        layout.addWidget(self.button_box)

    def get_credentials(self) -> tuple[str, str]:
        username = self.username.text().strip()
        password = self.password.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "Input Error", "Both username and password are required.")
            return "", ""

        return username, password

    def open_new_user_dialog(self) -> None:
        username, ok1 = QInputDialog.getText(self, "New User", "Enter Username:")
        if not ok1 or not username.strip():
            return
        email, ok2 = QInputDialog.getText(self, "New User", "Enter Email:")
        if not ok2 or not email.strip():
            return
        password, ok3 = QInputDialog.getText(self, "New User", "Enter Password:", QLineEdit.EchoMode.Password)
        if not ok3 or not password.strip():
            return

        user_data = {
            "UserName": username.strip(),
            "UserEmail": email.strip(),
            "UserPosition": "Staff",
            "UserPrivilegeLevel": "User",
        }

        write_to_database("core", "Users", user_data)
