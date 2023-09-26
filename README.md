# Бот-ассистент
Telegram-бот, который обращается к API сервиса Практикум.Домашка и узнает статус домашней работы:
- раз в 10 минут опрашивает API сервиса Практикум.Домашка и проверяет статус отправленной на ревью домашней работы;
- при обновлении статуса анализирует ответ API и отправляет соответствующее уведомление в Telegram;
- логирует свою работу и сообщает о важных проблемах сообщением в Telegram.

## Стек технологий:
- Python 3.9
- python-telegram-bot

### Как запустить проект:
Клонировать репозиторий и перейти в него в командной строке:
```
git clone git@github.com:Elllym-em/review_bot.git
```
```
cd review_bot
```
Cоздать и активировать виртуальное окружение:
```
python3 -m venv env
```
* Если у вас Linux/macOS
    ```
    source env/bin/activate
    ```
* Если у вас windows
    ```
    source env/scripts/activate
    ```
Установить зависимости из файла requirements.txt:
```
pip install -r requirements.txt
```
Запустить проект:
```
python3 homework.py
```

**Автор:**
[Elina Mustafaeva](https://github.com/Elllym-em)
