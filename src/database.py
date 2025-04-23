import sqlite3
from pathlib import Path

class ConnectSQLite:
    def __init__(self, db_path="database.db"):
        self.db_path = Path(db_path)
        self.conn = None
        self.cursor = None
        self.ensure_table_exists()

    def connect(self):
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()

    def ensure_table_exists(self):
        self.connect()
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS list_annotation (
            cne TEXT NOT NULL PRIMARY KEY,
            timestamp TEXT NOT NULL,
            risk_level TEXT NOT NULL,
            operator TEXT NOT NULL
        );
        """
        self.cursor.execute(create_table_sql)
        self.conn.commit()
        self.cursor.close()
        self.conn.close()

    def get_data(self, sql, params=None):
        self.connect()
        try:
            self.cursor.execute(sql, params or ())
            return [dict(row) for row in self.cursor.fetchall()]
        except Exception as e:
            print(f"Erreur dans get_data: {e}")
            return []
        finally:
            self.cursor.close()
            self.conn.close()

    def update_data(self, sql, params=None):
        self.connect()
        try:
            self.cursor.execute(sql, params or ())
            self.conn.commit()
            return True
        except Exception as e:
            print(f"SQLite update failed: {e}")
            return False
        finally:
            self.cursor.close()
            self.conn.close()

    def delete_all_annotations(self):
        sql = "DELETE FROM list_annotation"
        return self.update_data(sql)

    def get_list_annotation(self):
        sql = "SELECT * FROM list_annotation"
        return self.get_data(sql)

    def check_cne(self, cne):
        sql = "SELECT * FROM list_annotation WHERE cne=?"
        return self.get_data(sql, (cne,))

    def add_to_list_annotation(self, cne, timestamp, risk_level, operator):
        sql = """
        INSERT INTO list_annotation (cne, timestamp, risk_level, operator)
        VALUES (?, ?, ?, ?)
        """
        return self.update_data(sql, (cne, timestamp, risk_level, operator))
