import sqlite3

from ui.config.paths import BILLING_DB, CORE_DB, PATIENT_DB


def init_databases() -> None:
    # --- Company and Users
    with sqlite3.connect(CORE_DB) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Company (
                CompanyName TEXT,
                CompanyAddress TEXT,
                CompanyEmail TEXT,
                CompanyPhone TEXT
            );
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Users (
                UserName TEXT,
                UserEmail TEXT,
                UserPosition TEXT,
                UserPrivilegeLevel TEXT,
                UserPassword TEXT
            );
        """)

    # --- Patients, Providers, Visits, Notifications
    with sqlite3.connect(PATIENT_DB) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Patients (
                PatientId TEXT,
                PatientName TEXT,
                DOB TEXT,
                PhoneNumber TEXT,
                PatientEmail TEXT
            );
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Provider (
                ProviderId TEXT,
                ProviderName TEXT,
                ProviderRate REAL,
                MaxVisitsPerDay INTEGER
            );
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS VisitDetails (
                PatientId TEXT,
                ProviderId TEXT,
                VisitDate TEXT,
                VisitNotes TEXT,
                FollowUpDetails TEXT,
                BillId TEXT
            );
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Notification (
                NotificationId TEXT,
                PatientId TEXT,
                BillId TEXT,
                NotificationDate TEXT,
                MessageId TEXT
            );
        """)

    # --- Billing and Schedule
    with sqlite3.connect(BILLING_DB) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Billing (
                BillId TEXT,
                VisitId TEXT,
                DueDate TEXT,
                Paid INTEGER
            );
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Schedule (
                ScheduleId TEXT,
                ProviderId TEXT,
                PatientId TEXT,
                ScheduleDate TEXT,
                ScheduleSlot INTEGER
            );
        """)
