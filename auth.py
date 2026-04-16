import hashlib
from database import Database


class Auth:
    def __init__(self):
        self.db = Database()

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def register(self, username, password):
        password_hash = self.hash_password(password)
        try:
            cur = self.db.get_connection().cursor()
            cur.execute(
                "INSERT INTO users (username, password_hash) VALUES (%s, %s)",
                (username, password_hash)
            )
            self.db.get_connection().commit()
            cur.close()
            return True
        except:
            return False

    def login(self, username, password):
        password_hash = self.hash_password(password)
        cur = self.db.get_connection().cursor()

        # Проверяем блокировку
        cur.execute("SELECT is_blocked FROM users WHERE username = %s", (username,))
        result = cur.fetchone()
        if result and result[0]:
            cur.close()
            return None

        # Проверяем пароль
        cur.execute(
            "SELECT id, username FROM users WHERE username = %s AND password_hash = %s",
            (username, password_hash)
        )
        user = cur.fetchone()

        if user:
            # Сбрасываем попытки
            cur.execute("UPDATE users SET failed_attempts = 0 WHERE username = %s", (username,))
            self.db.get_connection().commit()
            cur.close()
            return {"id": user[0], "username": user[1]}
        else:
            # Увеличиваем счетчик попыток
            cur.execute(
                "UPDATE users SET failed_attempts = failed_attempts + 1 WHERE username = %s",
                (username,)
            )
            cur.execute(
                "UPDATE users SET is_blocked = TRUE WHERE username = %s AND failed_attempts >= 3",
                (username,)
            )
            self.db.get_connection().commit()
            cur.close()
            return None

    def is_blocked(self, username):
        cur = self.db.get_connection().cursor()
        cur.execute("SELECT is_blocked FROM users WHERE username = %s", (username,))
        result = cur.fetchone()
        cur.close()
        return result and result[0]