import sqlite3
import csv
import os
from pathlib import Path
from PySide6.QtWidgets import QPushButton, QMessageBox

from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QSizePolicy,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ui.config.paths import PATIENT_DB


class ReportsWindow(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("SubWindow")

        # --- Main vertical layout
        main_layout = QVBoxLayout(self)

        # --- Patient dropdown row
        dropdown_container = QHBoxLayout()
        self.patient_combo = QComboBox(self)
        dropdown_container.addWidget(QLabel("Select Patient:"))
        dropdown_container.addWidget(self.patient_combo)

        # ---Add dropdown row to main layout
        main_layout.addLayout(dropdown_container)

        # --- Visits table
        self.visits_table = QTableWidget(self)
        self.visits_table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.visits_table.verticalHeader().setVisible(False)
        self.visits_table.setColumnCount(5)
        self.visits_table.setHorizontalHeaderLabels(
            [
                "Visit Date",
                "Provider Name",
                "Visit Notes",
                "Follow Up",
                "Bill ID",
            ],
        )
        self.visits_table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        header = self.visits_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.visits_table.setAlternatingRowColors(True)
        main_layout.addWidget(self.visits_table)

        # --- Export button
        self.export_button = QPushButton("Export", self)
        self.export_button.setObjectName("ExportButton")
        self.export_button.clicked.connect(self._export_csv)
        main_layout.addWidget(self.export_button)

        main_layout.setStretch(1, 1)

        # ---Reload visits whenever a new patient is selected
        self.patient_combo.currentIndexChanged.connect(self._load_visits)

        # ---Load patients (and initial visits)
        self._load_patients()

    def _load_patients(self) -> None:
        try:
            conn = sqlite3.connect(PATIENT_DB)
            cursor = conn.cursor()
            cursor.execute("SELECT PatientName FROM Patients;")
            names = [row[0] for row in cursor.fetchall()]
        finally:
            conn.close()
        self.patient_combo.clear()
        self.patient_combo.addItems(names)
        # ---Load the visits for the first (or currently selected) patient
        self._load_visits()

    def _load_visits(self) -> None:
        # ---Fetch selected patient's ID
        patient_name = self.patient_combo.currentText()
        conn = sqlite3.connect(PATIENT_DB)
        cursor = conn.cursor()
        cursor.execute("SELECT PatientId FROM Patients WHERE PatientName = ?", (patient_name,))
        row = cursor.fetchone()
        patient_id = row[0] if row else ""
        # ---Query visit details joined with provider name
        cursor.execute(
            """
            SELECT vd.VisitDate, p.ProviderName, vd.VisitNotes, vd.FollowUpDetails, vd.BillId
            FROM VisitDetails vd
            LEFT JOIN Provider p ON vd.ProviderId = p.ProviderId
            WHERE vd.PatientId = ?
            ORDER BY vd.VisitDate ASC
        """,
            (patient_id,),
        )
        visits = cursor.fetchall()
        conn.close()

        # ---Populate table
        self.visits_table.setRowCount(len(visits))
        for i, (visit_date, prov_name, notes, follow_up, bill_id) in enumerate(visits):
            for j, value in enumerate((visit_date, prov_name, notes, follow_up, bill_id)):
                item = QTableWidgetItem(str(value))
                self.visits_table.setItem(i, j, item)

    def _export_csv(self) -> None:
        patient_name = self.patient_combo.currentText()
        desktop: Path = Path.home() / "Desktop"
        filename = f"{patient_name}.csv"
        path: Path = desktop / filename
        row_count = self.visits_table.rowCount()
        col_count = self.visits_table.columnCount()
        headers = []
        for col in range(col_count):
            header_item = self.visits_table.horizontalHeaderItem(col)
            headers.append(header_item.text() if header_item else "")
        try:
            with path.open("w", newline="", encoding="utf-8") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(headers)
                for row in range(row_count):
                    row_data = []
                    for col in range(col_count):
                        item = self.visits_table.item(row, col)
                        row_data.append(item.text() if item else "")
                    writer.writerow(row_data)
            QMessageBox.information(self, "Export Successful", f"Exported to:\n{path}", QMessageBox.StandardButton.Ok)
        except Exception as e:
            QMessageBox.critical(self, "Export Failed", f"Could not export CSV:\n{e}")
