import datetime

from sqlalchemy import create_engine, Table, Column, MetaData, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import mapper, sessionmaker


class ClientStorage:
    class Users:
        def __init__(self, username):
            self.id = None
            self.username = username

    class Contacts:
        def __init__(self, username):
            self.id = None
            self.username = username

    class Messages:
        def __init__(self, source_username, destination_username, timestamp, content):
            self.id = None
            self.source_username = source_username
            self.destination_username = destination_username
            self.content = content
            self.timestamp = timestamp

    def __init__(self, login):
        self.db_engine = create_engine(f"sqlite:///client_{login}_base.db", echo=False, pool_recycle=7200,
                                       connect_args={"check_same_thread": False})
        self.metadata = MetaData()

        users_table = Table("Users", self.metadata,
                            Column("id", Integer, primary_key=True),
                            Column("username", String, unique=True))

        contacts_table = Table("Contacts", self.metadata,
                               Column("id", Integer, primary_key=True),
                               Column("username", ForeignKey("Users.username", ondelete="CASCADE")))

        messages_table = Table("Messages", self.metadata,
                               Column("id", Integer, primary_key=True),
                               Column("source_username", String),
                               Column("destination_username", String),
                               Column("timestamp", DateTime, default=datetime.datetime.now()),
                               Column("content", Text))

        self.metadata.create_all(self.db_engine)
        mapper(self.Users, users_table)
        mapper(self.Contacts, contacts_table)
        mapper(self.Messages, messages_table)

        Session = sessionmaker(bind=self.db_engine)
        self.session = Session()

        # Перед началом работы, очищаем список контактов (для дальнейшего обновления с сервера)
        self.session.query(self.Users).delete()
        self.session.commit()

    def update_users(self, users_lst):
        self.session.query(self.Users).all().delete()
        for user in users_lst:
            self.session.add(self.Users(user))
        self.session.commit()

    def get_user(self, username):
        return self.session.query(self.Users).filter_by(username=username)

    def get_contact(self, username):
        return self.session.query(self.Contacts).filter_by(username=username)

    def add_contact(self, username):
        self.session.add(self.Users(username))
        self.session.commit()

    def del_contact(self, username):
        self.session.query(self.Users).filter_by(username=username).delete()
        self.session.commit()


if __name__ == "__main__":
    test_db = ClientStorage("test")
    test_db.del_contact("TEST")
