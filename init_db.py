import sqlite3
import os

def init_db():
    db_path = os.path.join('database', 'detections.db')
    
    # Connect (this creates the file if it doesn't exist)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 1. Detection History Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS detection_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            camera_id TEXT NOT NULL,
            object_class TEXT NOT NULL,
            confidence REAL NOT NULL,
            image_path TEXT
        )
    ''')
    
    # 2. Camera Configs Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS camera_configs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            camera_id TEXT UNIQUE NOT NULL,
            source TEXT NOT NULL,
            enable_detection BOOLEAN DEFAULT 1,
            enable_motion BOOLEAN DEFAULT 0
        )
    ''')
    
    # 3. Alerts Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            camera_id TEXT NOT NULL,
            message TEXT NOT NULL,
            image_path TEXT,
            cloud_url TEXT
        )
    ''')
    
    conn.commit()
    conn.close()
    print(f"Database initialized at {db_path}")

if __name__ == '__main__':
    init_db()
