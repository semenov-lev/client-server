import json

from common.variables import ENCODING
from decorators import log


@log
def encode_message(message):
    js_data = json.dumps(message)
    jim_bytes = js_data.encode(ENCODING)
    return jim_bytes


@log
def decode_data(jim_bytes):
    data = {}
    try:
        js_data = jim_bytes.decode(ENCODING)
        data = json.loads(js_data)
    except ValueError:
        print("Не удалось обработать полученные данные")
    return data
