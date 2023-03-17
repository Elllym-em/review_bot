class NotApiResponse(Exception):
    """Ошибка отсутствия ответа API."""

    pass


class HttpStatusError(Exception):
    """Ошибка статус-кода ответа API."""

    pass


class RequestApiError(Exception):
    """Ошибка при запросе к эндпоинту."""

    pass


class SendMessageError(Exception):
    """Ошибка отправки сообщения в Telegram."""

    pass
