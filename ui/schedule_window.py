import sqlite3
import uuid
from datetime import time

from PySide6.QtCore import QDate, Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QDateEdit,
    QFormLayout,
    QHeaderView,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ui.config.paths import PATIENT_DB
from ui.database.write_to_db import write_to_database


class Schedule(QWidget):
    HOURS = range(9, 17)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("SubWindow")
        self.setWindowTitle("Schedule Office Visit")

        container = QWidget(self)
        container_layout = QVBoxLayout(container)
        container_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        form_layout = QFormLayout()

        self.provider_combo = QComboBox(self)
        self.provider_combo.currentIndexChanged.connect(self._refresh_controls)
        form_layout.addRow("Provider:", self.provider_combo)

        self.patient_combo = QComboBox(self)
        form_layout.addRow("Patient:", self.patient_combo)

        self.date_edit = QDateEdit(self)
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.dateChanged.connect(self._refresh_controls)
        form_layout.addRow("Date:", self.date_edit)

        self.slot_combo = QComboBox(self)
        form_layout.addRow("Time Block:", self.slot_combo)

        container_layout.addLayout(form_layout)

        self.day_grid = QTableWidget(self)
        self.day_grid.setColumnCount(2)
        self.day_grid.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.day_grid.verticalHeader().setVisible(False)
        self.day_grid.setHorizontalHeaderLabels(["Time Slot", "Patient"])
        self.day_grid.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        container_layout.addWidget(self.day_grid)

        self.schedule_btn = QPushButton("Schedule", self)
        self.schedule_btn.clicked.connect(self._schedule_visit)
        container_layout.addWidget(self.schedule_btn, alignment=Qt.AlignmentFlag.AlignHCenter)

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(container)

        self._load_providers()
        self._load_patients()
        self._refresh_controls()

    @staticmethod
    def _conn():
        return sqlite3.connect(PATIENT_DB)

    def _load_providers(self) -> None:
        with self._conn() as conn:
            for pid, name in conn.execute("SELECT ProviderId, ProviderName FROM Provider"):
                self.provider_combo.addItem(name, pid)

    def _load_patients(self) -> None:
        with self._conn() as conn:
            for pid, name in conn.execute("SELECT PatientId, PatientName FROM Patients"):
                self.patient_combo.addItem(name, pid)

    @staticmethod
    def _slot_label(hour: int) -> str:
        start = time(hour=hour).strftime("%I:%M %p")
        end = time(hour=hour + 1).strftime("%I:%M %p")
        return f"{start} - {end}"

    def _current_date(self) -> str:
        return self.date_edit.date().toString("yyyy-MM-dd")

    def _day_map(self, provider_id: str, date_str: str) -> dict[int, str]:
        with self._conn() as conn:
            cur = conn.execute(
                """SELECT ScheduleSlot, PatientId
                    FROM Schedule
                    WHERE ProviderId = ?
                        AND ScheduleDate = ?""",
                (provider_id, date_str),
            )
            return {row[0]: row[1] for row in cur.fetchall()}

    def _patient_name(self, pid: str | None) -> str:
        if not pid:
            return ""
        with self._conn() as conn:
            cur = conn.execute("SELECT PatientName FROM Patients WHERE PatientId = ?", (pid,))
            row = cur.fetchone()
            return row[0] if row else ""

    def _refresh_controls(self) -> None:
        provider_id = self.provider_combo.currentData()
        date_str = self._current_date()
        bookings = self._day_map(provider_id, date_str)

        self.slot_combo.blockSignals(True)
        self.slot_combo.clear()
        for h in self.HOURS:
            label = self._slot_label(h)
            self.slot_combo.addItem(label, h)
            idx = self.slot_combo.count() - 1
            if h in bookings:
                self.slot_combo.model().item(idx).setEnabled(False)
        self.slot_combo.blockSignals(False)

        self.day_grid.setRowCount(len(self.HOURS))
        for row, h in enumerate(self.HOURS):
            label = self._slot_label(h)
            patient_name = self._patient_name(bookings.get(h))

            slot_item = QTableWidgetItem(label)
            patient_item = QTableWidgetItem(patient_name)

            if patient_name:
                for item in (slot_item, patient_item):
                    item.setBackground(QColor("#f8d7da"))

            self.day_grid.setItem(row, 0, slot_item)
            self.day_grid.setItem(row, 1, patient_item)

    def _schedule_visit(self) -> None:
        provider_id = self.provider_combo.currentData()
        patient_id = self.patient_combo.currentData()
        date_str = self._current_date()
        slot_hour = self.slot_combo.currentData()

        if slot_hour is None:
            QMessageBox.warning(self, "Slot unavailable", "Selected time block is already booked.")
            return

        with self._conn() as conn:
            cur = conn.execute(
                "SELECT 1 FROM Schedule WHERE ProviderId=? AND ScheduleDate=? AND ScheduleSlot=?",
                (provider_id, date_str, slot_hour),
            )
            if cur.fetchone():
                QMessageBox.warning(
                    self,
                    "Slot taken",
                    "The provider is already booked for that time.",
                )
                self._refresh_controls()
                return

        schedule_id = str(uuid.uuid4())
        data = {
            "ScheduleId": schedule_id,
            "ProviderId": provider_id,
            "PatientId": patient_id,
            "ScheduleDate": date_str,
            "ScheduleSlot": slot_hour,
        }

        if write_to_database("patients", "Schedule", data):
            QMessageBox.information(self, "Scheduled", "Office visit scheduled successfully.")
            self._refresh_controls()
        else:
            QMessageBox.critical(self, "Error", "Failed to schedule office visit.")
