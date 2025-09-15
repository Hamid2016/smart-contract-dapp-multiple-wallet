import sqlite3
import os

os.makedirs("db", exist_ok=True)


def get_connection():
    conn = sqlite3.connect("db/dapp.db", check_same_thread=False)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

