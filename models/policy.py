from models.db import get_connection

class PolicyModel:
    def __init__(self):
        self.conn = get_connection()
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS policies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                address TEXT NOT NULL,
                policy_name TEXT,
                premium REAL,
                coverage_amount REAL,
                created_at TEXT
            )
        """)
        self.conn.commit()

    def save_policy(self, address, name, premium, coverage):
        self.cursor.execute("""
            INSERT INTO policies (address, policy_name, premium, coverage_amount, created_at)
            VALUES (?, ?, ?, ?, datetime('now'))
        """, (address, name, premium, coverage))
        self.conn.commit()
