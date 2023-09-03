import sqlite3


class AuthDatabase:
    def get_cursor(self):
        self.conn = sqlite3.connect('auth.db', check_same_thread=False)
        self.cursor = self.conn.cursor()

    def create_table(self, table_name, columns):
        self.get_cursor()
        query = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(columns)})"
        self.cursor.execute(query)
        self.conn.commit()
        self.close()

    def insert_data(self, table_name, data):
        self.get_cursor()
        placeholders = ', '.join(['?' for _ in range(len(data))])
        query = f"INSERT INTO {table_name} VALUES ({placeholders})"
        self.cursor.execute(query, data)
        self.conn.commit()
        self.close()

    def fetch_data(self, table_name, condition=None):
        self.get_cursor()
        if condition:
            query = f"SELECT * FROM {table_name} WHERE {condition}"
        else:
            query = f"SELECT * FROM {table_name}"
        print(query)
        self.cursor.execute(query)
        result = self.cursor.fetchall()
        self.close()
        return result

    def close(self):
        self.conn.close()
