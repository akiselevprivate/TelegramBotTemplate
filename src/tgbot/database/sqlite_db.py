import sqlite3 as sq
from datetime import datetime, timedelta


def date_now():
    return datetime.now()


def get_text_date():
    now = date_now()
    return now.isoformat(' ')


def get_date_from_text(date_text: str):
    return datetime.fromisoformat(date_text)


class DataBaseHelper:
    def __init__(self):
        self.dbname = "db.sqlite3"
        self.connect = sq.connect(self.dbname)
        self.cursor = self.connect.cursor()

    def setup(self):
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS UserList (
                telegram_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                date_reg TEXT,
                date_activity TEXT,
                memory TEXT DEFAULT "",
                block INTEGER DEFAULT 0,
                action_count INTEGER DEFAULT 0,
                referral_tokens INTEGER DEFAULT 0
            );
            """)

        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS MessageList (
                id INTEGER PRIMARY KEY,
                telegram_id INTEGER,
                username TEXT DEFAULT "",
                message_q TEXT DEFAULT "",
                message_a TEXT DEFAULT "",
                message_a_t TEXT DEFAULT "",
                date_q TEXT DEFAULT "",
                date_a TEXT DEFAULT "",
                message_a_url_count INTEGER DEFAULT 0,
                FOREIGN KEY (telegram_id) references UserList(telegram_id)
            );
            """)

        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS ReferralList (
                id INTEGER PRIMARY KEY,
                telegram_id INTEGER,
                username TEXT DEFAULT "",
                referral_telegram_id INTEGER,
                date TEXT DEFAULT "",
                FOREIGN KEY (telegram_id) references UserList(telegram_id)
                FOREIGN KEY (referral_telegram_id) references UserList(telegram_id)
            );
            """)

        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS UserActionList (
                id INTEGER PRIMARY KEY,
                telegram_id INTEGER,
                username TEXT DEFAULT "",
                date TEXT DEFAULT "",
                action_type TEXT,
                FOREIGN KEY (telegram_id) references UserList(telegram_id)
            );
            """)

    def add_user(self, telegram_id, username, first_name, last_name):
        user = self.cursor.execute(
            """
            SELECT username FROM UserList WHERE telegram_id = ?
            """, (telegram_id,)
        ).fetchone()

        if not user:
            self.cursor.execute(
                """
                INSERT INTO UserList 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (telegram_id, username, first_name, last_name, get_text_date(),
                 get_text_date(), "", 0, 0, 0)
            )
            self.connect.commit()
        return not user

    def check_user_registered(self, telegram_id: int):
        user = self.cursor.execute(
            """
            SELECT username FROM UserList WHERE telegram_id = ?
            """, (telegram_id,)
        ).fetchone()
        if not user:
            return False
        return True

    def add_message_q(self, telegram_id, username, message_q):
        self.cursor.execute(
            """
            INSERT OR IGNORE INTO MessageList (telegram_id, username, message_q, date_q)
            VALUES (?, ?, ?, ?);
            """,
            (telegram_id, username, message_q, get_text_date())
        )
        self.connect.commit()

        self.cursor.execute(
            """
            UPDATE UserList SET memory = ?, date_activity = ?
            WHERE telegram_id = ?
            """, (message_q, get_text_date(), telegram_id)
        )
        self.connect.commit()

    def add_message_a(self, telegram_id, message_q, message_a, message_a_t):
        self.cursor.execute(
            """
            UPDATE MessageList SET message_a = ?, message_a_t = ?, date_a = ?
            WHERE telegram_id = ? AND message_q = ?
            """,
            (message_a, message_a_t, get_text_date(),
             telegram_id, message_q)
        )
        self.connect.commit()

    def get_last_user_action_count(self, telegram_id: int):
        min_date_text = (date_now() - timedelta(hours=24)).isoformat(' ')
        return self.cursor.execute(
            """
            SELECT COUNT(*) FROM UserActionList
            WHERE telegram_id = ? AND date > ?
            """, (telegram_id, min_date_text)
        ).fetchone()[0]

    def add_user_action(self, telegram_id: int, username: str, action_type: str):
        self.cursor.execute(
            """
            INSERT INTO UserActionList (telegram_id, username, date, action_type)
            VALUES (?, ?, ?, ?)
            """,
            (telegram_id, username, get_text_date(),
             action_type)
        )
        self.cursor.execute(
            """
            UPDATE UserList SET action_count = action_count + 1
            WHERE telegram_id = ?
            """, (telegram_id,)
        )
        self.connect.commit()

    def get_user_action_count(self, telegram_id: int):
        return self.cursor.execute(
            """
            SELECT action_count, referral_tokens FROM UserList
            WHERE telegram_id = ?
            """, (telegram_id,)
        ).fetchone()

    def get_user_block(self, telegram_id: int):
        return self.cursor.execute(
            """
            SELECT block FROM UserList
            WHERE telegram_id = ?
            """, (telegram_id,)
        ).fetchone()[0]

    def add_referral(self, telegram_id: int, username: str, referral_user_id: int, referral_tokens: int):
        referral_user = self.cursor.execute(
            """
            SELECT username FROM UserList WHERE telegram_id = ?
            """, (referral_user_id,)
        ).fetchone()

        if not referral_user:
            return False, 'реферал не существует'

        user = self.cursor.execute(
            """
            SELECT username FROM ReferralList WHERE telegram_id = ? AND referral_telegram_id = ?
            """, (telegram_id, referral_user_id)
        ).fetchone()

        if user:
            return False, 'реферал уже сушествует'

        self.cursor.execute(
            """
            INSERT INTO ReferralList (telegram_id, username, referral_telegram_id, date)
            VALUES (?, ?, ?, ?)
            """,
            (telegram_id, username, referral_user_id,
             get_text_date())
        )

        self.cursor.execute(
            """
            UPDATE UserList SET referral_tokens = referral_tokens + ?
            WHERE telegram_id = ?
            """, (referral_tokens, referral_user_id)
        )
        self.connect.commit()

        return True, None

    def use_token(self, telegram_id: int):
        self.cursor.execute(
            """
            UPDATE UserList SET referral_tokens = referral_tokens - 1
            WHERE telegram_id = ?
            """, (telegram_id,)
        )
        self.connect.commit()


db = DataBaseHelper()
