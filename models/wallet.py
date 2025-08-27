from models.db import get_connection

class WalletModel:
    def __init__(self):
        self.conn = get_connection()
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS wallets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                address TEXT UNIQUE NOT NULL,
                connected_at TEXT
            )
        """)
        self.conn.commit()

    def add_wallet(self, address):
        self.cursor.execute(
            "INSERT OR IGNORE INTO wallets (address, connected_at) VALUES (?, datetime('now'))",
            (address,)
        )
        self.conn.commit()
