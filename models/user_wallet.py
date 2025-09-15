import sqlite3
from models.db import get_connection  # Adjust path if needed

class UserWalletModel:
    def __init__(self):
        self.conn = get_connection()
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_wallets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                wallet_id INTEGER NOT NULL,
                date TEXT,
                UNIQUE(user_id, wallet_id),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (wallet_id) REFERENCES wallets(id) ON DELETE CASCADE
            )
        """)
        self.conn.commit()

    def link_user_wallet(self, user_id, wallet_id, date=None):
        self.cursor.execute("""
            INSERT INTO user_wallets (user_id, wallet_id, date)
            VALUES (?, ?, ?)
        """, (user_id, wallet_id, date))
        self.conn.commit()

    def get_wallets_for_user(self, user_id):
        self.cursor.execute("""
            SELECT wallet_id, date FROM user_wallets
            WHERE user_id = ?
        """, (user_id,))
        return self.cursor.fetchall()

    def get_users_for_wallet(self, wallet_id):
        self.cursor.execute("""
            SELECT user_id, date FROM user_wallets
            WHERE wallet_id = ?
        """, (wallet_id,))
        return self.cursor.fetchall()

    def close(self):
        self.conn.close()
