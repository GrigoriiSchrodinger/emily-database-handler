import logging
import sqlite3

logger = logging.getLogger('root')

class RequestsSql:
    ADD_USER_TO_USER_QUERY = "INSERT INTO users (username, first_name, last_name, id_users) VALUES (?, ?, ?, ?)"
    ADD_USER_TO_BELOW_QUERY = "INSERT INTO below_track (id) VALUES ((SELECT id FROM users WHERE id = ?))"
    ADD_USER_TO_HIGHER_QUERY = "INSERT INTO higher_track (id) VALUES ((SELECT id FROM users WHERE id = ?))"
    CHECK_USER_QUERY = "SELECT id_users from '{}' WHERE id_users = ?"
    UPDATE_CURRENCY_QUERY = "UPDATE '{}' SET '{}'='{}' WHERE id=(SELECT id FROM users WHERE id_users = ?)"
    DELETE_CURRENCY_QUERY = "UPDATE '{}' SET '{}'=NULL WHERE id=(SELECT id FROM users WHERE id_users = ?)"

class Sqlite(RequestsSql):
    def __init__(self, path):
        self.connect = sqlite3.connect(path)
        self.cursor = self.connect.cursor()

    def request(self, query: str, parameters: tuple = ()) -> None:
        logger.info(f"execute - {query}")
        self.cursor.execute(query, parameters)
        self.connect.commit()

    def fetchone(self, query: str, parameters: tuple = ()) -> tuple:
        self.request(query, parameters)
        return self.cursor.fetchone()

    def fetchall(self, query: str, parameters: tuple = ()) -> list[tuple]:
        self.request(query, parameters)
        return self.cursor.fetchall()

    def execute_script(self, script: str) -> None:
        with open(f'database/sql_query/{script}', 'r') as sqlite_file:
            file = sqlite_file.read()
            logger.info(f"Execute script - {file}")
            self.connect.executescript(file)

    def __del__(self) -> None:
        logger.info(f"Connect close")
        self.connect.close()

class DataBaseManager(Sqlite):
    def create_tables(self) -> None:
        self.execute_script("sqlite_create_tables.sql")