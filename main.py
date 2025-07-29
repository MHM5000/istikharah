#!/usr/bin/env python3

import sqlite3
import time

import requests

DB_NAME = "istikharah.db"
API_URL = "https://api.forghan.com/istikharah"


def main():
    # Setup database
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS istikharah (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sura_number INTEGER NOT NULL,
        aya_number INTEGER NOT NULL,
        sura TEXT NOT NULL,
        aya TEXT NOT NULL,
        result_fa TEXT,
        result_ur TEXT,
        translates_fa TEXT,
        UNIQUE(sura_number, aya_number)
    );
    """
    )
    conn.commit()

    def fetch_and_store():
        try:
            r = requests.get(API_URL)
            if r.status_code != 200:
                print("Failed:", r.status_code)
                return

            data = r.json()
            cursor.execute(
                """
                INSERT OR IGNORE INTO istikharah (
                    sura_number, aya_number, sura, aya, result_fa, result_ur, translates_fa
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    data["sura_number"],
                    data["aya_number"],
                    data["sura"],
                    data["aya"],
                    data["result"].get("fa"),
                    data["result"].get("ur"),
                    data["translates"].get("fa"),
                ),
            )
            conn.commit()
            print(f"Stored: {data['sura_number']}:{data['aya_number']}")

        except Exception as e:
            print("Error:", e)

    while True:
        cursor.execute("SELECT COUNT(*) FROM istikharah")
        count = cursor.fetchone()[0]
        if count >= 604:
            print("✅ All 604 entries collected.")
            break

        fetch_and_store()
        time.sleep(1)

    conn.close()


if __name__ == "__main__":
    main()
