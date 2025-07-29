#!/usr/bin/env python3

from fastapi import FastAPI
from fastapi.responses import JSONResponse
import sqlite3
import random

app = FastAPI()
DB_NAME = "istikharah.db"

@app.get("/random")
def get_random_entry():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM istikharah")
    total = cursor.fetchone()[0]

    if total == 0:
        return JSONResponse(content={"error": "No entries found"}, status_code=404)

    offset = random.randint(0, total - 1)
    cursor.execute("SELECT * FROM istikharah LIMIT 1 OFFSET ?", (offset,))
    row = cursor.fetchone()
    conn.close()

    return dict(row)
