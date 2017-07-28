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
    message.answer("0", keyboard=kb_test)
    # telebot.send("0", chat_id=message.chat_id, keyboard=kb_test)
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

test.commands = ["^/test$"]
test_callbacks.callbacks = ["^test_.*$"]
test.help = "Тест инлайн клавиатуры"