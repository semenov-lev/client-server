import dis
from socket import socket


class ServerVerifier(type):
    def __init__(cls, clsname, bases, cls_dict):
        super().__init__(clsname, bases, cls_dict)
        _func_attrs = []
        _func_methods = []

        for k, v in cls_dict.items():
            if k == "__init__":
                for ins in dis.get_instructions(cls_dict[k]):
                    if ins.opname == "LOAD_GLOBAL":
                        _func_attrs.append(ins.argval)
                if not ("SOCK_STREAM" in _func_attrs and "AF_INET" in _func_attrs):
                    raise Exception("Некорректная инициализация TCP-сокета")
                if k == "run":
                    for ins in dis.get_instructions(cls_dict[k]):
                        if ins.opname == "LOAD_METHOD":
                            _func_methods.append(ins.argval)
                    if "connect" in _func_methods:
                        raise Exception("Метод connect не может быть реализован в классе Server")


class ClientVerifier(type):
    def __init__(cls, clsname, bases, cls_dict):
        super().__init__(clsname, bases, cls_dict)
        _func_attrs = []
        _func_methods = []
        for k, v in cls_dict.items():
            if type(v) == socket:
                raise Exception(f"Инициализация сокета '{k}' не должна происходить на уровне класса!")
            if k == "__init__":
                for ins in dis.get_instructions(cls_dict[k]):
                    print(ins)
