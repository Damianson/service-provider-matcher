import sqlite3
import os
from typing import List, Dict, Any, Optional

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "providers.db")

def get_db_connection(db_path: Optional[str] = None) -> sqlite3.Connection:
    path = db_path or DB_PATH
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn

def init_db(db_path: Optional[str] = None) -> None:
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS providers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            hourly_rate REAL NOT NULL,
            rating REAL NOT NULL,
            review_count INTEGER NOT NULL DEFAULT 0,
            availability TEXT NOT NULL,
            skills TEXT NOT NULL,
            bio TEXT NOT NULL,
            years_experience INTEGER DEFAULT 5,
            badge TEXT DEFAULT ''
        )
    """)
    conn.commit()
    conn.close()

def row_to_dict(row: sqlite3.Row) -> Dict[str, Any]:
    d = dict(row)
    # Parse availability and skills as lists for convenience
    d["availability_list"] = [a.strip().lower() for a in d["availability"].split(",") if a.strip()]
    d["skills_list"] = [s.strip() for s in d["skills"].split(",") if s.strip()]
    return d

def get_all_providers(db_path: Optional[str] = None) -> List[Dict[str, Any]]:
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM providers ORDER BY rating DESC")
    rows = cursor.fetchall()
    conn.close()
    return [row_to_dict(r) for r in rows]

def get_providers_by_category(category: str, db_path: Optional[str] = None) -> List[Dict[str, Any]]:
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM providers WHERE LOWER(category) = LOWER(?) ORDER BY rating DESC", (category,))
    rows = cursor.fetchall()
    conn.close()
    return [row_to_dict(r) for r in rows]

def insert_provider(p: Dict[str, Any], db_path: Optional[str] = None) -> int:
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO providers (name, category, hourly_rate, rating, review_count, availability, skills, bio, years_experience, badge)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        p["name"],
        p["category"].lower(),
        float(p["hourly_rate"]),
        float(p["rating"]),
        int(p.get("review_count", 10)),
        p["availability"],
        p["skills"],
        p["bio"],
        int(p.get("years_experience", 5)),
        p.get("badge", "")
    ))
    provider_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return provider_id

