import sqlite3
import uuid
from datetime import datetime, timedelta

from PySide6.QtCore import QDate, Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDateEdit,
    QGridLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)
from tzlocal import get_localzone

from ui.config.paths import PATIENT_DB
from ui.database.write_to_db import write_to_database


class VisitDetailsWindow(QWidget):

    TZ = get_localzone()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Visit Details")
        self.setObjectName("SubWindow")

        main_layout = QVBoxLayout(self)
        form_layout = QGridLayout()
        form_layout.setHorizontalSpacing(20)
        form_layout.setVerticalSpacing(15)

        self.patient_combo = QComboBox(self)
        form_layout.addWidget(QLabel("Patient:"), 0, 0)
        form_layout.addWidget(self.patient_combo, 0, 1)

        self.provider_combo = QComboBox(self)
        form_layout.addWidget(QLabel("Provider:"), 1, 0)
        form_layout.addWidget(self.provider_combo, 1, 1)

        self.visit_date_edit = QDateEdit(self)
        self.visit_date_edit.setCalendarPopup(True)
        self.visit_date_edit.setDate(QDate.currentDate())
        form_layout.addWidget(QLabel("Visit Date:"), 2, 0)
        form_layout.addWidget(self.visit_date_edit, 2, 1)

        self.visit_notes_edit = QTextEdit(self)
        form_layout.addWidget(QLabel("Visit Notes:"), 3, 0)
        form_layout.addWidget(self.visit_notes_edit, 3, 1)

        self.follow_up_edit = QTextEdit(self)
        form_layout.addWidget(QLabel("Follow‑up / Prescription Details:"), 4, 0)
        form_layout.addWidget(self.follow_up_edit, 4, 1)

        self.send_bill_checkbox = QCheckBox("Send Bill", self)
        form_layout.addWidget(self.send_bill_checkbox, 5, 1)

        self.add_button = QPushButton("Add Visit Details", self)
        self.add_button.clicked.connect(self._add_visit_details)
        form_layout.addWidget(self.add_button, 6, 0, 1, 2, alignment=Qt.AlignmentFlag.AlignCenter)

        main_layout.addLayout(form_layout)

        self._load_patients_and_providers()

    def _load_patients_and_providers(self) -> None:
        try:
            with sqlite3.connect(PATIENT_DB) as conn:
                cur = conn.cursor()

                self.patient_combo.addItem("Select a patient")
                cur.execute("SELECT PatientId, PatientName FROM Patients")
                for pid, name in cur.fetchall():
                    self.patient_combo.addItem(name, pid)

                self.provider_combo.addItem("Select a provider")
                cur.execute("SELECT ProviderId, ProviderName FROM Provider")
                for pid, name in cur.fetchall():
                    self.provider_combo.addItem(name, pid)

        except Exception as e:  # pragma: no cover – UI feedback
            QMessageBox.critical(self, "Database Error", f"Failed to load data: {e}")

    def _add_visit_details(self) -> None:
        patient_id = self.patient_combo.currentData()
        provider_id = self.provider_combo.currentData()
        if patient_id is None:
            QMessageBox.warning(self, "Input Error", "Please select a patient.")
            return
        if provider_id is None:
            QMessageBox.warning(self, "Input Error", "Please select a provider.")
            return

        visit_date = self.visit_date_edit.date().toString("yyyy-MM-dd")
        visit_notes = self.visit_notes_edit.toPlainText().strip()
        follow_up = self.follow_up_edit.toPlainText().strip()
        send_bill = self.send_bill_checkbox.isChecked()

        bill_id = str(uuid.uuid4())
        visit_data = {
            "PatientId": patient_id,
            "ProviderId": provider_id,
            "VisitDate": visit_date,
            "VisitNotes": visit_notes,
            "FollowUpDetails": follow_up,
            "BillId": bill_id if send_bill else None,
        }

        if not write_to_database("patients", "VisitDetails", visit_data):
            QMessageBox.critical(self, "Database Error", "Failed to add visit details.")
            return

        if send_bill:
            if self._create_bill_and_notification(bill_id, patient_id, provider_id):
                QMessageBox.information(self, "Success", "Visit details and billing created successfully.")
            else:
                QMessageBox.warning(
                    self,
                    "Partial Success",
                    "Visit saved, but billing/notification failed.",
                )
        else:
            QMessageBox.information(self, "Success", "Visit details added successfully.")

        self._clear_form()

    def _provider_rate(self, provider_id: str) -> float | None:
        with sqlite3.connect(PATIENT_DB) as conn:
            cur = conn.execute("SELECT ProviderRate FROM Provider WHERE ProviderId = ?", (provider_id,))
            row = cur.fetchone()
            return row[0] if row else None

    def _create_bill_and_notification(self, bill_id: str, patient_id: str, provider_id: str) -> bool:
        amount = self._provider_rate(provider_id) or 0.0
        due_date = (datetime.now(tz=self.TZ).date() + timedelta(days=30)).isoformat()

        bill_ok = write_to_database(
            "billing",
            "Billing",
            {
                "BillId": bill_id,
                "BillAmount": amount,
                "VisitId": bill_id,
                "DueDate": due_date,
                "Paid": 0,
            },
        )

        notif_ok = write_to_database(
            "patients",
            "Notification",
            {
                "NotificationId": str(uuid.uuid4()),
                "PatientId": patient_id,
                "BillId": bill_id,
                "NotificationDate": datetime.now(tz=self.TZ).isoformat(),
                "MessageId": "BILL_GENERATED",
            },
        )

        return bill_ok and notif_ok

    def _clear_form(self) -> None:
        self.patient_combo.setCurrentIndex(0)
        self.provider_combo.setCurrentIndex(0)
        self.visit_date_edit.setDate(QDate.currentDate())
        self.visit_notes_edit.clear()
        self.follow_up_edit.clear()
        self.send_bill_checkbox.setChecked(False)
