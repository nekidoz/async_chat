import enum
import time
import json

"""
# message text - maximum 500 characters
MESSAGE FORMATS:
{
    "action": "presence",                   # 15 characters max
    "time": <unix timestamp>, 
    "type": "status", 
    "user": {
        "account_name": "C0deMaver1ck",     # 25 characters max
        "status": "Yep, I am here!"
    }
}
RESPONSE FORMATS:
{
    "response": <код ответа>,               # 3 digits
    {"alert"|"error"}: <текст ответа> 
}
"""


# Max 15 characters
class Actions(str, enum.Enum):
    PRESENCE = "presence"
    PROBE = "probe"
    MESSAGE = "msg"
    QUIT = "quit"
    AUTHENTICATE = "authenticate"
    JOIN = "join"
    LEAVE = "leave"


class Responses(enum.IntEnum):
    # 1xx — информационные сообщения:
    NOTIFY_BASIC = 100          # базовое уведомление
    NOTIFY_IMPORTANT = 101      # важное уведомление
    # 2xx — успешное завершение:
    OK = 200                    # OK
    CREATED = 201               # объект создан
    ACCEPTED = 202              # подтверждение
    # 4xx — ошибка на стороне клиента:
    BAD_REQUEST = 400           # неправильный запрос / JSON - объект
    LOGIN_REQUIRED = 401        # не авторизован
    BAD_LOGIN = 402             # неправильный логин / пароль
    FORBIDDEN = 403             # пользователь заблокирован
    NOT_FOUND = 404             # пользователь / чат отсутствует на сервере
    CONFLICT = 409              # уже имеется подключение с указанным логином
    GONE = 410                  # адресат существует, но недоступен(offline)
    # 5xx — ошибка на стороне сервера:
    SERVER_ERROR = 500          # ошибка сервера

    @property
    def response(self):
        messages = {
            self.NOTIFY_BASIC: {"alert": "Базовое уведомление"},
            self.NOTIFY_IMPORTANT: {"alert": "Важное уведомление"},
            self.OK: {"alert": "OK"},
            self.CREATED: {"alert": "Объект создан"},
            self.ACCEPTED: {"alert": "Подтверждение"},
            self.BAD_REQUEST: {"error": "Неправильный запрос / JSON - объект"},
            self.LOGIN_REQUIRED: {"error": "Не авторизован"},
            self.BAD_LOGIN: {"error": "Неправильный логин / пароль"},
            self.FORBIDDEN: {"error": "Пользователь заблокирован"},
            self.NOT_FOUND: {"error": "Пользователь / чат отсутствует на сервере"},
            self.CONFLICT: {"error": "Уже имеется подключение с указанным логином"},
            self.GONE: {"error": "Адресат существует, но недоступен (offline)"},
            self.SERVER_ERROR: {"error": "Ошибка сервера"}
        }

        message = {
            "response": self.value,
        }
        message.update(messages.get(self.value, {"error": "Неизвестный код ответа"}))
        return message


# ATTRIBUTES:
# _action - message action
# _time - UNIX timestamp passed to initializer or timestamp of the moment the Message object was created
# _kwargs - other arguments dictionary
class Message:
    def __init__(self, action: Actions, **kwargs):
        self.action = Actions(action)
        self.time = kwargs.get("time")
        if not self.time:
            self.time = time.time_ns()
        self.kwargs = kwargs

    # class object constructor from JSON string
    @classmethod
    def from_str(cls, json_str: str):
        message = json.loads(json_str)
        return cls(**message)

    # return JSON string with the message
    @property
    def json(self) -> str:
        message = {
            "action": self.action,
            "time": self.time
        }
        message.update(**self.kwargs)
        return json.dumps(message)


# ATTRIBUTES:
# _action - message action
# _time - UNIX timestamp passed to initializer or timestamp of the moment the Message object was created
# _kwargs - other arguments dictionary
class Response:
    def __init__(self, response: Responses, **kwargs):
        self.response = Responses(response)
        self.time = kwargs.get("time")
        if not self.time:
            self.time = time.time_ns()
        self.kwargs = kwargs

    # class object constructor from JSON string
    @classmethod
    def from_str(cls, json_str: str):
        response = json.loads(json_str)
        return cls(**response)

    # return JSON string with the response
    @property
    def json(self) -> str:
        response = {
            "response": self.response,
            "time": self.time
        }
        response.update(**self.kwargs)
        return json.dumps(response)
