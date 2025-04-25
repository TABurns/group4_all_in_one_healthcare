import csv
import sqlite3
from pathlib import Path

from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ui.config.paths import BILLING_DB, PATIENT_DB


class ReportsWindow(QWidget):

    COLS = [  # noqa: RUF012
        "Visit Date",
        "Provider Name",
        "Visit Notes",
        "Follow Up",
        "Bill ID",
        "Amount",
        "Due Date",
        "Paid",
    ]

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("SubWindow")

        main_layout = QVBoxLayout(self)

        dropdown_container = QHBoxLayout()
        self.patient_combo = QComboBox(self)
        dropdown_container.addWidget(QLabel("Select Patient:"))
        dropdown_container.addWidget(self.patient_combo)
        main_layout.addLayout(dropdown_container)

        self.visits_table = QTableWidget(self)
        self.visits_table.setSelectionMode(QAbstractItemView.NoSelection)
        self.visits_table.verticalHeader().setVisible(False)
        self.visits_table.setColumnCount(len(self.COLS))
        self.visits_table.setHorizontalHeaderLabels(self.COLS)
        self.visits_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.visits_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.visits_table.setAlternatingRowColors(True)
        main_layout.addWidget(self.visits_table)

        self.export_button = QPushButton("Export", self)
        self.export_button.setObjectName("ExportButton")
        self.export_button.clicked.connect(self._export_csv)
        main_layout.addWidget(self.export_button)

        main_layout.setStretch(1, 1)

        self.patient_combo.currentIndexChanged.connect(self._load_visits)

        self._load_patients()

    def _load_patients(self) -> None:
        with sqlite3.connect(PATIENT_DB) as conn:
            cur = conn.execute("SELECT PatientId, PatientName FROM Patients")
            self.patient_combo.clear()
            for pid, name in cur.fetchall():
                self.patient_combo.addItem(name, pid)
        self._load_visits()

    def _load_visits(self) -> None:
        patient_id = self.patient_combo.currentData()
        if patient_id is None:
            return

        billing_path = str(BILLING_DB)
        with sqlite3.connect(PATIENT_DB) as conn:
            conn.execute(f"ATTACH DATABASE '{billing_path}' AS billing;")
            query = """
                SELECT vd.VisitDate,
                       p.ProviderName,
                       vd.VisitNotes,
                       vd.FollowUpDetails,
                       vd.BillId,
                       b.BillAmount,
                       b.DueDate,
                       CASE b.Paid WHEN 1 THEN 'Yes' ELSE 'No' END
                FROM VisitDetails vd
                LEFT JOIN Provider p ON vd.ProviderId = p.ProviderId
                LEFT JOIN billing.Billing b ON vd.BillId = b.BillId
                WHERE vd.PatientId = ?
                ORDER BY vd.VisitDate ASC;
                """
            rows = conn.execute(query, (patient_id,)).fetchall()
            conn.execute("DETACH DATABASE billing;")

        self.visits_table.setRowCount(len(rows))
        for r, row in enumerate(rows):
            for c, value in enumerate(row):
                self.visits_table.setItem(r, c, QTableWidgetItem(str(value)))

    def _export_csv(self) -> None:
        patient_name = self.patient_combo.currentText()
        path = Path.home() / "Desktop" / f"{patient_name}.csv"
        try:
            with path.open("w", newline="", encoding="utf-8") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(self.COLS)
                for r in range(self.visits_table.rowCount()):
                    writer.writerow([
                        self.visits_table.item(r, c).text() if self.visits_table.item(r, c) else "" for c in range(self.visits_table.columnCount())
                    ])
            QMessageBox.information(self, "Export Successful", f"Exported to:\n{path}")
        except Exception as exc:
            QMessageBox.critical(self, "Export Failed", f"Could not export CSV:\n{exc}")
