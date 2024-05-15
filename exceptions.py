class TelegramMessageException(Exception):
    """Ошибка отправки."""

    pass


class NoTokensException(Exception):
    """Нет токена."""

    pass


class NoKeyHmwrkException(Exception):
    """Нет ключа."""

    pass


class NoKeyHmwrkNameException(Exception):
    """Нет имени."""

    pass


class StatusException(Exception):
    """Статус не найден."""

    pass


class GetApiException(Exception):
    """api exception."""

    pass


class NoHmWrkException(Exception):
    """no homework."""

    pass
