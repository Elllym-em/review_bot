class NotApiResponse(Exception):
    """Ошибка отсутствия ответа API."""

    pass


class HttpStatusError(Exception):
    """Ошибка статус-кода ответа API."""

    pass
