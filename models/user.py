import sqlite3
from datetime import datetime
import hashlib

class UserModel:
    def __init__(self, db_name="db/dapp.db"):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                email TEXT,
                phone_number TEXT,
                country TEXT,
                ip_address TEXT,
                browser TEXT,
                os TEXT,
                last_login TEXT,
                last_logout TEXT
            )
        """)
        self.conn.commit()

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def create_user(self, username, password, email=None, phone_number=None,
                    country=None, ip_address=None, browser=None, os=None):
        hashed_pw = self.hash_password(password)
        try:
            self.cursor.execute("""
                INSERT INTO users (username, password, email, phone_number, country,
                                   ip_address, browser, os)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (username, hashed_pw, email, phone_number, country, ip_address, browser, os))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError as e:
            print("User creation failed:", e)
            return False

    def validate_user(self, username, password):
        hashed_pw = self.hash_password(password)
        self.cursor.execute("""
            SELECT * FROM users WHERE username = ? AND password = ?
        """, (username, hashed_pw))
        return self.cursor.fetchone()

    def update_login_time(self, username):
        now = datetime.utcnow().isoformat()
        self.cursor.execute("""
            UPDATE users SET last_login = ?WHERE username = ?
        """, (now, username))
        self.conn.commit()

    def update_logout_time(self, username):
        now = datetime.utcnow().isoformat()
        self.cursor.execute("""
            UPDATE users SET last_logout = ? WHERE username = ?
        """, (now, username))
        self.conn.commit()

    def get_user(self, username):
        self.cursor.execute("""
            SELECT id, username, last_login, last_logout FROM users WHERE username = ?
        """, (username,))
        row = self.cursor.fetchone()
        if row:
            return {
                "id": row[0],
                "username": row[1],
                "last_login": row[2],
                "last_logout": row[3]
            }
        return None

    def close(self):
        self.conn.close()
