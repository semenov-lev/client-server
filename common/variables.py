"""Константы"""

# Порт по умолчанию для сетевого ваимодействия
DEFAULT_PORT = 7777
# IP адрес по умолчанию для подключения клиента
DEFAULT_IP_ADDRESS = '127.0.0.1'
# Максимальная очередь подключений
MAX_CONNECTIONS = 5
# Максимальная длинна сообщения в байтах
MAX_PACKAGE_LENGTH = 1024
# Кодировка проекта
ENCODING = 'utf-8'

# Протокол JIM основные ключи:
ACTION = 'action'
TIME = 'time'
USER = 'user'
MESSAGE = 'message'
TO = 'to'
FROM = 'from'

# Прочие ключи, используемые в протоколе
PRESENCE = "presence"
GET_CONTACTS = "get_contacts"
RESPONSE = "response"
QUIT = "quit"
ERROR = "error"
MSG = "msg"
LISTEN_ACCOUNT_NAME = "listen_account"
SENDER_ACCOUNT_NAME = "sender_account"
