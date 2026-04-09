import sqlite3
from flask import g

def get_db( app ):
    if "db" not in g:
        g.db = sqlite3.connect( app.config[ "DATABASE" ] )
        g.db.row_factory = sqlite3.Row
    return g.db

# simple sqlite3 db (id = int, title = text, description = text, completed = boolean, created_at = time)
def init_db( app ):
    with app.app_context():
        db = get_db( app )
        db.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                completed INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
        db.commit()
        db.close()