import sqlite3

from PySide6.QtCore import QDate, Qt
from PySide6.QtWidgets import QCheckBox, QComboBox, QDateEdit, QGridLayout, QLabel, QMessageBox, QPushButton, QTextEdit, QVBoxLayout, QWidget

from ui.config.paths import PATIENT_DB
from ui.database.write_to_db import write_to_database


class VisitDetailsWindow(QWidget):
    def __init__(self, parent=None) -> None:  # noqa: ANN001
        super().__init__(parent)
        self.setWindowTitle("Add Visit Details")
        self.setObjectName("SubWindow")

        main_layout = QVBoxLayout(self)

        form_layout = QGridLayout()
        form_layout.setHorizontalSpacing(20)
        form_layout.setVerticalSpacing(15)

        # ---Patient selection
        self.patient_combo = QComboBox(self)
        form_layout.addWidget(QLabel("Patient:"), 0, 0)
        form_layout.addWidget(self.patient_combo, 0, 1)

        # ---Provider selection
        self.provider_combo = QComboBox(self)
        form_layout.addWidget(QLabel("Provider:"), 1, 0)
        form_layout.addWidget(self.provider_combo, 1, 1)

        # ---Visit date
        self.visit_date_edit = QDateEdit(self)
        self.visit_date_edit.setCalendarPopup(True)
        self.visit_date_edit.setDate(QDate.currentDate())
        form_layout.addWidget(QLabel("Visit Date:"), 2, 0)
        form_layout.addWidget(self.visit_date_edit, 2, 1)

        # ---Visit notes
        self.visit_notes_edit = QTextEdit(self)
        form_layout.addWidget(QLabel("Visit Notes:"), 3, 0)
        form_layout.addWidget(self.visit_notes_edit, 3, 1)

        # ---Follow-up / Prescription details
        self.follow_up_edit = QTextEdit(self)
        form_layout.addWidget(QLabel("Follow-up / Prescription Details:"), 4, 0)
        form_layout.addWidget(self.follow_up_edit, 4, 1)

        # ---Send bill checkbox
        self.send_bill_checkbox = QCheckBox("Send Bill", self)
        form_layout.addWidget(self.send_bill_checkbox, 5, 1)

        # ---Add Visit Details button
        self.add_button = QPushButton("Add Visit Details", self)
        self.add_button.clicked.connect(self.add_visit_details)
        form_layout.addWidget(self.add_button, 6, 0, 1, 2, alignment=Qt.AlignmentFlag.AlignCenter)

        main_layout.addLayout(form_layout)

        # ---Load patients and providers into combo boxes
        self.load_patients_and_providers()

    def load_patients_and_providers(self) -> None:
        try:
            with sqlite3.connect(PATIENT_DB) as conn:
                cursor = conn.cursor()

                # ---Load patients
                cursor.execute("SELECT PatientName FROM Patient")
                patients = cursor.fetchall()
                self.patient_combo.addItem("Select a patient")
                for patient in patients:
                    self.patient_combo.addItem(patient[0])

                # ---Load providers
                cursor.execute("SELECT ProviderName FROM Provider")
                providers = cursor.fetchall()
                self.provider_combo.addItem("Select a provider")
                for provider in providers:
                    self.provider_combo.addItem(provider[0])

        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Failed to load data: {e}")

    def add_visit_details(self) -> None:
        # Retrieve data from the form
        patient_name = self.patient_combo.currentText()
        provider_name = self.provider_combo.currentText()
        visit_date = self.visit_date_edit.date().toString("yyyy-MM-dd")
        visit_notes = self.visit_notes_edit.toPlainText().strip()
        follow_up = self.follow_up_edit.toPlainText().strip()
        send_bill = self.send_bill_checkbox.isChecked()

        # Basic validation
        if patient_name == "Select a patient":
            QMessageBox.warning(self, "Input Error", "Please select a patient.")
            return
        if provider_name == "Select a provider":
            QMessageBox.warning(self, "Input Error", "Please select a provider.")
            return

        # Prepare data for database insertion
        visit_data = {
            "PatientName": patient_name,
            "ProviderName": provider_name,
            "VisitDate": visit_date,
            "VisitNotes": visit_notes,
            "FollowUp": follow_up,
            "SendBill": int(send_bill),
        }

        # Insert visit details into the database
        success = write_to_database("patients", "VisitDetails", visit_data)
        if success:
            QMessageBox.information(self, "Success", "Visit details added successfully.", QMessageBox.StandardButton.Ok)
            self._clear_form()
        else:
            QMessageBox.critical(self, "Database Error", "Failed to add visit details.")

    def _clear_form(self) -> None:
        self.patient_combo.setCurrentIndex(0)
        self.provider_combo.setCurrentIndex(0)
        self.visit_date_edit.setDate(QDate.currentDate())
        self.visit_notes_edit.clear()
        self.follow_up_edit.clear()
        self.send_bill_checkbox.setChecked(False)
