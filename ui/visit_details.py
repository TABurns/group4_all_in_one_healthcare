import sqlite3
from datetime import timedelta

from PySide6.QtCore import QDate, Qt
from PySide6.QtWidgets import QComboBox, QDateEdit, QGridLayout, QLabel, QMessageBox, QPushButton, QTextEdit, QVBoxLayout, QWidget
from tzlocal import get_localzone

from ui.config.paths import BILLING_DB, CORE_DB, PATIENT_DB
from ui.database.write_to_db import write_to_database


class VisitDetailsWindow(QWidget):
    TZ = get_localzone()

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
                cursor.execute("SELECT PatientName FROM Patients")
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
        # ---Retrieve data from the form
        patient_name = self.patient_combo.currentText()
        provider_name = self.provider_combo.currentText()
        visit_date = self.visit_date_edit.date().toString("yyyy-MM-dd")
        visit_notes = self.visit_notes_edit.toPlainText().strip()
        follow_up = self.follow_up_edit.toPlainText().strip()

        # ---Basic validation
        if patient_name == "Select a patient":
            QMessageBox.warning(self, "Input Error", "Please select a patient.")
            return
        if provider_name == "Select a provider":
            QMessageBox.warning(self, "Input Error", "Please select a provider.")
            return

        # --- Lookup patient and provider IDs
        conn = sqlite3.connect(PATIENT_DB)
        cursor = conn.cursor()
        cursor.execute("SELECT PatientId FROM Patients WHERE PatientName = ?", (patient_name,))
        patient_row = cursor.fetchone()
        cursor.execute("SELECT ProviderId FROM Provider WHERE ProviderName = ?", (provider_name,))
        provider_row = cursor.fetchone()
        conn.close()

        patient_id = patient_row[0] if patient_row else ""
        provider_id = provider_row[0] if provider_row else ""

        # --- Generate BillId
        conn_bill = sqlite3.connect(BILLING_DB)
        cur_bill = conn_bill.cursor()
        cur_bill.execute("SELECT COUNT(*) FROM Billing;")
        bill_count = cur_bill.fetchone()[0] or 0
        bill_id = str(bill_count + 1)
        conn_bill.close()

        # ---Prepare data for database insertion
        visit_data = {
            "PatientId": patient_id,
            "ProviderId": provider_id,
            "VisitDate": visit_date,
            "VisitNotes": visit_notes,
            "FollowUpDetails": follow_up,
            "BillId": bill_id,
        }

        success = write_to_database("patients", "VisitDetails", visit_data)
        # --- Only generate billing if none exists for this visit
        conn_check = sqlite3.connect(BILLING_DB)
        cur_check = conn_check.cursor()
        cur_check.execute("SELECT 1 FROM Billing WHERE VisitId = ? LIMIT 1", (bill_id,))
        if cur_check.fetchone():
            conn_check.close()
            return
        conn_check.close()

        if success:
            import datetime
            import uuid

            # ---Fetch provider rate
            conn_b = sqlite3.connect(PATIENT_DB)
            cur_b = conn_b.cursor()
            cur_b.execute(
                "SELECT ProviderRate FROM Provider WHERE ProviderId = ?",
                (provider_id,),
            )
            rate_row = cur_b.fetchone()
            amount_due = rate_row[0] if rate_row else 0

            due_date = (datetime.datetime.now(tz=self.TZ).date() + timedelta(days=30)).isoformat()

            conn_b = sqlite3.connect(BILLING_DB)
            cur_b = conn_b.cursor()

            cur_b.execute(
                "INSERT INTO Billing (BillId, VisitId, BillAmount, DueDate, Paid) VALUES (?, ?, ?, ?, 0)",
                (bill_id, bill_id, amount_due, due_date),
            )
            conn_b.commit()
            conn_b.close()


            # ---Read company name from core DB
            conn_core = sqlite3.connect(CORE_DB)
            cur_core = conn_core.cursor()
            cur_core.execute(
                "SELECT CompanyName FROM Company LIMIT 1;",
            )
            row = cur_core.fetchone()
            company_name = row[0] if row else ""
            conn_core.close()

            # --- Generate notification entry
            notification_id = str(uuid.uuid4())
            notification_date = datetime.datetime.now(tz=self.TZ).isoformat()
            message = f"Your bill for services provided by {company_name} on {visit_date} is due on {due_date}.\nPlease pay {amount_due} at you're earliest convenience.\nThank You!"
            conn_n = sqlite3.connect(PATIENT_DB)
            cur_n = conn_n.cursor()
            cur_n.execute(
                "INSERT INTO Notification (NotificationId, PatientId, BillId, NotificationDate, Message) VALUES (?, ?, ?, ?, ?)",
                (notification_id, patient_id, bill_id, notification_date, message),
            )
            conn_n.commit()
            conn_n.close()
            QMessageBox.information(self, "Success", "Visit details added and Bill generated successfully.", QMessageBox.StandardButton.Ok)
            self._clear_form()
        else:
            QMessageBox.critical(self, "Database Error", "Failed to add visit details.")

    def _clear_form(self) -> None:
        self.patient_combo.setCurrentIndex(0)
        self.provider_combo.setCurrentIndex(0)
        self.visit_date_edit.setDate(QDate.currentDate())
        self.visit_notes_edit.clear()
        self.follow_up_edit.clear()
