# new_patients.py

import sqlite3

import simplematch as sm
from PySide6.QtWidgets import (
    QDialogButtonBox,
    QFormLayout,
    QLineEdit,
    QMessageBox,
    QVBoxLayout,
    QWidget,
)

from ui.config.logger_config import logger
from ui.config.paths import PATIENT_DB
from ui.database.write_to_db import write_to_database


class NewPatientWindow(QWidget):
    def __init__(self, root: QWidget, parent=None) -> None:
        super().__init__(parent)

        self.root = root
        self.setWindowTitle("New Patient Portal")
        self.setObjectName('NewPatient')

        main_layout = QVBoxLayout(self)

        form_layout = QFormLayout()

        self.patient_name_input = QLineEdit(self)
        self.patient_name_input.setObjectName("LineEdit")
        form_layout.addRow("Patient Name:  ",self.patient_name_input)

        self.patient_dob_input = QLineEdit(self)
        self.patient_dob_input.setObjectName("LineEdit")
        form_layout.addRow("DOB:  ",self.patient_dob_input)

        self.patient_phone_number = QLineEdit(self)
        self.patient_phone_number.setObjectName("LineEdit")
        form_layout.addRow("Phone Number:  ", self.patient_phone_number)

        self.patient_email = QLineEdit(self)
        self.patient_email.setObjectName("LineEdit")
        form_layout.addRow("Email:  ", self.patient_email)

        main_layout.addLayout(form_layout)

        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.setObjectName("NewPatientSetupBTN")
        self.button_box.accepted.connect(self.accept)
        #self.button_box.rejected.connect(self.reject)
        main_layout.addWidget(self.button_box)

    def accept(self) -> None:
        name = self.patient_name_input.text().strip()
        dob = self.patient_dob_input.text().strip()
        phone = self.patient_phone_number.text().strip()
        email = self.patient_email.text().strip()

        if not name:
            QMessageBox.warning(self, "Input Error", "Name is required.")
            return

        if not dob:
            QMessageBox.warning(self, "Input Error", "Address is required.")
            return

        if not email:
            QMessageBox.warning(self, "Input Error", "Email is required.")
            return

        # ---Validate Email, expected pattern: username@domain
        email_pattern = "{username}@{domain}"
        email_result = sm.match(email_pattern, email)
        if not email_result:
            QMessageBox.warning(self, "Invalid Input", "Email must be in the format username@domain.")
            return

        # ---Ensure the domain contains a period (e.g., yahoo.com)
        if "." not in email_result.get("domain", ""):
            QMessageBox.warning(self, "Invalid Input", "Email domain must contain a period (e.g., yahoo.com).")
            return

        if not phone:
            QMessageBox.warning(self, "Input Error", "Phone is required.")
            return

        # ---Validate company phone format using simplematch with expected pattern: (###) ###-####
        phone_pattern = "({area}) {prefix}-{line}"
        match_result = sm.match(phone_pattern, phone)
        if not match_result:
            QMessageBox.warning(self, "Invalid Input", "Phone must be in the format (###) ###-####.")
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
            with sqlite3.connect(PATIENT_DB) as conn:
                cursor = conn.cursor()
            patient_count = cursor.execute("SELECT COUNT(*) FROM Patient").fetchone()[0]

            patient_id = patient_count + 1

            patient_data = {
                "PatientId": patient_id,
                "PatientName": name,
                "DOB": dob,
                "PatientEmail": email,
            }

            success = write_to_database("patients", "Patient", patient_data)
            if not success:
                QMessageBox.critical(self, "Error", "Failed to save company info to database.")
                return
        except Exception as e:
            logger.error(f"Error saving setup configuration to SQLite: {e}")
            return
