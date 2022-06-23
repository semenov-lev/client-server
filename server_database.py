import datetime

from sqlalchemy import create_engine, Table, Column, MetaData, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import mapper, sessionmaker

"""
Начать реализацию класса «Хранилище» для серверной стороны. Хранение необходимо осуществлять в базе данных. 
 качестве СУБД использовать sqlite. Для взаимодействия с БД можно применять ORM.
Опорная схема базы данных:
На стороне сервера БД содержит следующие таблицы:
    Client:
        логин;
        информация.
        
    ClientHistory:
        время входа;
        ip-адрес.
        
    Contacts (составляется на основании выборки всех записей с id_владельца):
        id_владельца;
        id_клиента.
"""


class ServerStorage:
    class Users:
        def __init__(self, login, ip, port):
            self.id = None
            self.login = login
            self.ip = ip
            self.port = port

    class LoginHistory:
        def __init__(self, user_id, ip):
            self.id = None
            self.user_id = user_id
            self.ip = ip

    class Contacts:
        def __init__(self, owner_id, client_id):
            self.id = None
            self.owner_id = owner_id
            self.client_id = client_id

    def __init__(self):
        self.db_engine = create_engine('sqlite:///server_base.db', echo=False, pool_recycle=7200)
        self.metadata = MetaData()

        users_table = Table("Users", self.metadata,
                            Column("id", Integer, primary_key=True),
                            Column("login", String, unique=True),
                            Column("ip", String),
                            Column("port", Integer)
                            )

        login_history_table = Table("login_history", self.metadata,
                                    Column("id", Integer, primary_key=True),
                                    Column("user_id", ForeignKey("Users.id", ondelete="CASCADE")),
                                    Column("datatime", DateTime, default=datetime.datetime.now()),
                                    Column("ip", String)
                                    )

        contacts_table = Table("Contacts", self.metadata,
                               Column("id", Integer, primary_key=True),
                               Column("owner_id", ForeignKey("Users.id", ondelete="CASCADE")),
                               Column("client_id", ForeignKey("Users.id", ondelete="CASCADE"))
                               )

        self.metadata.create_all(self.db_engine)
        mapper(self.Users, users_table)
        mapper(self.LoginHistory, login_history_table)
        mapper(self.Contacts, contacts_table)

        Session = sessionmaker(bind=self.db_engine)
        self.session = Session()

    def login(self, login, ip, port):
        rez = self.session.query(self.Users).filter_by(login=login)
        if rez.count():
            user = rez.first()
        else:
            user = self.Users(login, ip, port)
            self.session.add(user)
        self.session.commit()

        self.session.add(self.LoginHistory(user.id, ip))
        self.session.commit()

    def get_contacts(self, login):
        contacts = []
        login_id = self.session.query(self.Users).filter_by(login=login).first().id
        rez = self.session.query(self.Contacts, self.Users.login).\
            filter_by(owner_id=login_id).\
            join(self.Users, self.Contacts.client_id == self.Users.id).all()
        for i in rez:
            contacts.append(i.login)
        return contacts

    def add_contact(self, login, username):
        contacts = self.get_contacts(login)
        if username not in contacts:
            login_id = self.session.query(self.Users).filter_by(login=login).first().id
            username_id = self.session.query(self.Users).filter_by(login=username).first().id
            self.session.add(self.Contacts(login_id, username_id))
            self.session.commit()

    def del_contact(self, login, username):
        contacts = self.get_contacts(login)
        if username in contacts:
            login_id = self.session.query(self.Users).filter_by(login=login).first().id
            username_id = self.session.query(self.Users).filter_by(login=username).first().id
            self.session.query(self.Contacts).filter_by(owner_id=login_id, client_id=username_id).delete()
            self.session.commit()


if __name__ == "__main__":
    debugging_db = ServerStorage()

    contacts_to_add = [debugging_db.Contacts(1, 2),
                       debugging_db.Contacts(2, 3),
                       debugging_db.Contacts(1, 3),
                       debugging_db.Contacts(1, 4)]

    debugging_db.login("first", "127.0.0.2", 7777)
    debugging_db.login("second", "127.0.0.3", 7777)
    debugging_db.login("third", "127.0.0.4", 7777)
    debugging_db.session.add_all(contacts_to_add)
    debugging_db.session.commit()
    print(debugging_db.get_contacts("first"))
