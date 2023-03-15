class NotApiResponse(Exception):
    """Ошибка отсутствия ответа API."""

    def __init__(self, message='Ответ API не получен.'):
        """Возврат сообщения об ошибке."""
        self.message = message
        super().__init__(self.message)


class HttpStatusError(Exception):
    """Ошибка статус-кода ответа API."""

    def __init__(self, message='Ошибка статус-кода ответа API.'):
        """Возврат сообщения об ошибке."""
        self.message = message
        super().__init__(self.message)
