import sqlite3
from datetime import datetime
from collections import namedtuple
from dataclasses import dataclass
import config
import os


@dataclass
class User:
    user_id: int | None = None
    mochi_api_key: str | None = None

class Database:
    def __init__(self):
        self.client = sqlite3.connect("db/mochi_db.sqlite")
        self.cursor = self.client.cursor()
        self.init_db()

    def get_user(self, user_id: str):
        variables = ["user_id", "mochi_api_key"]
        self.cursor.execute(
            f"SELECT {','.join(variables)} FROM Users WHERE user_id = ?",
            (user_id,),
        )
        result = self.cursor.fetchone()
        user = User(**dict(zip(variables, result)))
        return user

    def init_db(self):
        package_path = os.path.dirname(os.path.abspath(__file__))
        with open(f"{package_path}/schema.sql") as f:
            self.cursor.executescript(f.read())