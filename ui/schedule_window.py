import sqlite3
import uuid
from datetime import time

from PySide6.QtCore import QDate, Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QFormLayout,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ui.config.paths import PATIENT_DB
from ui.database.write_to_db import write_to_database


class Schedule(QWidget):

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("SubWindow")
        self.setWindowTitle("Schedule Office Visit")

        container = QWidget(self)
        container_layout = QVBoxLayout(container)
        container_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        form_layout = QFormLayout()

        self.provider_combo = QComboBox(self)
        form_layout.addRow("Provider:", self.provider_combo)

        self.patient_combo = QComboBox(self)
        form_layout.addRow("Patient:", self.patient_combo)

        self.date_edit = QDateEdit(self)
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())
        form_layout.addRow("Date:", self.date_edit)

        self.slot_combo = QComboBox(self)
        self._populate_time_blocks()  # <- fills the combo box
        form_layout.addRow("Time Block:", self.slot_combo)

        container_layout.addLayout(form_layout)

        self.schedule_btn = QPushButton("Schedule", self)
        self.schedule_btn.clicked.connect(self._schedule_visit)
        container_layout.addWidget(self.schedule_btn, alignment=Qt.AlignmentFlag.AlignHCenter)

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(container)

        self._load_providers()
        self._load_patients()

    def _populate_time_blocks(self) -> None:
        start_hour = 9
        end_hour = 17
        for h in range(start_hour, end_hour):
            start = time(hour=h).strftime("%I:%M %p")
            end = time(hour=h + 1).strftime("%I:%M %p")
            label = f"{start} - {end}"
            self.slot_combo.addItem(label, label)

    def _load_providers(self) -> None:
        conn = sqlite3.connect(PATIENT_DB)
        cursor = conn.cursor()
        cursor.execute("SELECT ProviderId, ProviderName FROM Provider")
        for pid, name in cursor.fetchall():
            self.provider_combo.addItem(name, pid)
        conn.close()

    def _load_patients(self) -> None:
        conn = sqlite3.connect(PATIENT_DB)
        cursor = conn.cursor()
        cursor.execute("SELECT PatientId, PatientName FROM Patients")
        for pid, name in cursor.fetchall():
            self.patient_combo.addItem(name, pid)
        conn.close()

    def _schedule_visit(self) -> None:
        provider_id = self.provider_combo.currentData()
        patient_id = self.patient_combo.currentData()
        date_str = self.date_edit.date().toString("yyyy-MM-dd")
        slot_text = self.slot_combo.currentData()
        schedule_id = str(uuid.uuid4())

        data = {
            "ScheduleId": schedule_id,
            "ProviderId": provider_id,
            "PatientId": patient_id,
            "ScheduleDate": date_str,
            "ScheduleSlot": slot_text,
        }

        if write_to_database("patients", "Schedule", data):
            QMessageBox.information(self, "Scheduled", "Office visit scheduled successfully.")
            self.close()  # QWidget → close()
        else:
            QMessageBox.critical(self, "Error", "Failed to schedule office visit.")
