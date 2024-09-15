import sqlite3


def get_db_connection():
    conn = sqlite3.connect('/app/data/sensor_data.db')  # Persist data in Docker volume
    conn.row_factory = sqlite3.Row
    return conn


def create_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sensor_data (
            id TEXT,
            type TEXT,
            subtype TEXT,
            reading INTEGER,
            location TEXT,
            timestamp TIMESTAMP
        );
    ''')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_id ON sensor_data (id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_type ON sensor_data (type)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_subtype ON sensor_data (subtype)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_location ON sensor_data (location)')
    conn.commit()
    conn.close()
