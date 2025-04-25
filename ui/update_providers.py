# update_providers.py

import sqlite3

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFormLayout,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ui.config.paths import PATIENT_DB
from ui.database.write_to_db import write_to_database


class UpdateProvidersWindow(QWidget):
    def __init__(self, parent=None) -> None:  # noqa: ANN001
        super().__init__(parent)
        self.setWindowTitle("Add Provider")
        self.setObjectName("SubWindow")

        main_layout = QVBoxLayout(self)

        container = QWidget(self)
        container_layout = QVBoxLayout(container)
        container_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        form_layout = QFormLayout()

        # ---Provider Name
        self.provider_name_input = QLineEdit(self)
        form_layout.addRow("Provider Name:", self.provider_name_input)

        """# ---User ID
        self.user_id_input = QLineEdit(self)
        form_layout.addRow("User ID:", self.user_id_input)"""

        # ---Provider Rate
        self.provider_rate_input = QLineEdit(self)
        form_layout.addRow("Provider Rate:", self.provider_rate_input)

        # ---Max Visits Per Day
        """self.max_visits_input = QLineEdit(self)
        form_layout.addRow("Max Visits Per Day:", self.max_visits_input)"""

        container_layout.addLayout(form_layout)

        # ---Add Provider button
        self.add_button = QPushButton("Add Provider", self)
        self.add_button.clicked.connect(self.add_provider)
        container_layout.addWidget(self.add_button, alignment=Qt.AlignmentFlag.AlignHCenter)

        main_layout.addWidget(container)

    def _generate_provider_id(self) -> str:
        # ---Count existing providers and return next ID
        try:
            conn = sqlite3.connect(PATIENT_DB)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM Provider;")
            count = cursor.fetchone()[0] or 0
        finally:
            conn.close()
        return str(count + 1)

    def add_provider(self) -> None:
        provider_id = self._generate_provider_id()
        provider_name = self.provider_name_input.text().strip()
        # user_id = self.user_id_input.text().strip()

        # ---Rate and Max Visits validation
        rate_text = self.provider_rate_input.text().strip()
        # max_visits_text = self.max_visits_input.text().strip()
        if not rate_text:
            QMessageBox.warning(self, "Input Error", "Provider Rate is required.")
            return
        """if not max_visits_text:
            QMessageBox.warning(self, "Input Error", "Max Visits Per Day is required.")
            return"""
        try:
            provider_rate = float(rate_text)
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Provider Rate must be a number.")
            return
        """try:
            max_visits = int(max_visits_text)
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Max Visits Per Day must be an integer.")
            return"""

        # ---Validation
        if not provider_name:
            QMessageBox.warning(self, "Input Error", "Provider Name is required.")
            return
        """if not user_id:
            QMessageBox.warning(self, "Input Error", "User ID is required.")
            return"""

        # ---Prepare data for database insertion
        provider_data = {
            "ProviderId": provider_id,
            "ProviderName": provider_name,
            # "UserId": user_id,
            "ProviderRate": provider_rate,
            # "MaxVisitsPerDay": max_visits,
        }

        # ---Insert provider details into the database
        success = write_to_database("patients", "Provider", provider_data)
        if success:
            QMessageBox.information(
                self,
                "Success",
                "Provider added successfully.",
                QMessageBox.StandardButton.Ok,
            )
            # ---Clear input fields
            self._clear_inputs()
        else:
            QMessageBox.critical(self, "Database Error", "Failed to add provider.")

    def _clear_inputs(self) -> None:
        for child in self.findChildren(QLineEdit):
            child.clear()
