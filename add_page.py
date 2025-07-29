#!/usr/bin/env python3

import json
import sqlite3

import pandas as pd

DB_NAME = "istikharah.db"
CSV_PATH = "sura_aya_page.csv"
REPORT_PATH = "page_update_report.json"


def main():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Add 'page' column if not exists
    try:
        cursor.execute("ALTER TABLE istikharah ADD COLUMN page INTEGER;")
        print("➕ Added 'page' column.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("ℹ️ 'page' column already exists.")
        else:
            raise

    # Load CSV
    df = pd.read_csv(CSV_PATH)
    page_lookup = {
        (int(row["sura"]), int(row["aya"])): int(row["page"])
        for _, row in df.iterrows()
    }

    # Update database
    missing_in_csv = []
    update_errors = []

    cursor.execute("SELECT sura_number, aya_number FROM istikharah")
    rows = cursor.fetchall()

    for sura, aya in rows:
        page = page_lookup.get((sura, aya))
        if page is None:
            missing_in_csv.append({"sura": sura, "aya": aya})
            continue
        try:
            cursor.execute(
                "UPDATE istikharah SET page = ? WHERE sura_number = ? AND aya_number = ?",
                (page, sura, aya),
            )
        except Exception as e:
            update_errors.append({"sura": sura, "aya": aya, "error": str(e)})

    conn.commit()

    # Null page check
    cursor.execute("SELECT sura_number, aya_number FROM istikharah WHERE page IS NULL")
    null_rows = [{"sura": r[0], "aya": r[1]} for r in cursor.fetchall()]

    # Save report
    report = {
        "missing_in_csv": missing_in_csv,
        "update_errors": update_errors,
        "null_page_rows": null_rows,
    }
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    conn.close()
    print("✅ Done. Report saved to", REPORT_PATH)


if __name__ == "__main__":
    main()
