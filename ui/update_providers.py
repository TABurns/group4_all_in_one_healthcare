# update_providers.py

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFormLayout,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

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

        # ---Provider ID
        self.provider_id_input = QLineEdit(self)
        form_layout.addRow("Provider ID:", self.provider_id_input)

        # ---Provider Name
        self.provider_name_input = QLineEdit(self)
        form_layout.addRow("Provider Name:", self.provider_name_input)

        # ---User ID
        self.user_id_input = QLineEdit(self)
        form_layout.addRow("User ID:", self.user_id_input)

        container_layout.addLayout(form_layout)

        # ---Add Provider button
        self.add_button = QPushButton("Add Provider", self)
        self.add_button.clicked.connect(self.add_provider)
        container_layout.addWidget(self.add_button)

        main_layout.addWidget(container)

    def add_provider(self) -> None:
        provider_id = self.provider_id_input.text().strip()
        provider_name = self.provider_name_input.text().strip()
        user_id = self.user_id_input.text().strip()

        # ---Validation
        if not provider_id:
            QMessageBox.warning(self, "Input Error", "Provider ID is required.")
            return
        if not provider_name:
            QMessageBox.warning(self, "Input Error", "Provider Name is required.")
            return
        if not user_id:
            QMessageBox.warning(self, "Input Error", "User ID is required.")
            return

        # ---Prepare data for database insertion
        provider_data = {
            "ProviderId": provider_id,
            "ProviderName": provider_name,
            "UserId": user_id,
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
            self._clear_inputs()
        else:
            QMessageBox.critical(self, "Database Error", "Failed to add provider.")

    def _clear_inputs(self) -> None:
        for child in self.findChildren(QLineEdit):
            child.clear()
