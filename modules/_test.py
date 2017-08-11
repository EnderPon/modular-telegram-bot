import json

kb_test = json.dumps({"inline_keyboard":
    [
        [
            {"text": "+1",
             "callback_data": 'test_increment'},
            {"text": "-1",
             "callback_data": 'test_decrement'},
            {"text": "=0",
             "callback_data": 'test_zero'}
        ]
    ]
})

def test(telebot, message):
    # message.answer("0", keyboard=kb_test)
    # telebot.send("0", chat_id=message.chat_id, keyboard=kb_test)
    message.answer("Это сообщение всегда должно быть первым.")
    # Запрешаем число 3
    if "3" in message.text:
        telebot.break_ = True
        message.answer("Сообщение не обработано из-за числа '3'")
    return

def test2(telebot, message):
    # message.answer("0", keyboard=kb_test)
    # telebot.send("0", chat_id=message.chat_id, keyboard=kb_test)
    message.answer("Это сообщение всегда должно быть последним.")
    return

def test3(telebot, message):
    # message.answer("0", keyboard=kb_test)
    # telebot.send("0", chat_id=message.chat_id, keyboard=kb_test)
    message.answer("Это сообщение отвечает на любые сообщения начинающиеся на /test.")
    return

def test_callbacks(telebot, callback):
    data = callback.data
    try:
        text = int(callback.message.text)
    except ValueError:
        callback.message.update(0, keyboard=kb_test)
    else:
        if data == 'test_increment':
            callback.message.update(text+1, keyboard=kb_test)
        elif data == 'test_decrement':
            callback.message.update(text-1, keyboard=kb_test)
        elif data == 'test_zero':
            callback.message.update(0, keyboard=kb_test)

test.commands = ["^.*$"]
test_callbacks.callbacks = ["^test_.*$"]
test.help = "Тестовый модуль для приоритетов"
test.priority = "high"

test2.commands = ["^.*$"]
test2.help = "Тестовый модуль для приоритетов 2"
test2.priority = "low"

test3.commands = ["^/test.*$"]
test3.help = "Тестовый модуль для приоритетов 3"
test3.priority = "mid"
