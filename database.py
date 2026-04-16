import psycopg2


class Database:
    def __init__(self):

        self.conn = psycopg2.connect(
            host="localhost",
            database="exam_db",
            user="postgres",
            password="Lera12005"
        )

    def get_connection(self):
        return self.conn

    def close(self):
        self.conn.close()

        self.conn = psycopg2.connect(
            host="localhost",
            database="exam_db",
            user="postgres",
            password="Lera12005"
        )