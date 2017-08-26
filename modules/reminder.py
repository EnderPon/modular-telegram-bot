import threading
import time
import json


remind_kb = json.dumps({"inline_keyboard":
    [
        [
            {"text": "+ 5 мин",
             "callback_data": 'remind_+5min'},
            {"text": "- 5 мин",
             "callback_data": 'remind_-5min'}
        ],
        [
            {"text": "+ 15 мин",
             "callback_data": 'remind_+15min'},
            {"text": "- 15 мин",
             "callback_data": 'remind_-15min'}
        ],
        [
            {"text": "+ 1 час",
             "callback_data": 'remind_+1h'},
            {"text": "- 1 час",
             "callback_data": 'remind_-1h'}
        ],
        [
            {"text": "+ 5 часов",
             "callback_data": 'remind_+5h'},
            {"text": "- 5 часов",
             "callback_data": 'remind_-5h'}
        ],        [
            {"text": "+ 1 день",
             "callback_data": 'remind_+1d'},
            {"text": "- 1 день",
             "callback_data": 'remind_-1d'}
        ],
        [
            {"text": "+ 7 дней",
             "callback_data": 'remind_+7d'},
            {"text": "- 7 дней",
             "callback_data": 'remind_-7d'}
        ],
        [
            {"text": "+ 1 мес",
             "callback_data": 'remind_+1month'},
            {"text": "- 1 мес",
             "callback_data": 'remind_-1month'}
        ],
        [
            {"text": "+ 1 год",
             "callback_data": 'remind_+1y'},
            {"text": "- 1 год",
             "callback_data": 'remind_-1y'}
        ],
        [
            {"text": "Создать",
             "callback_data": 'remind_done'},
        ]
    ]
})


dates = {
    'remind_+5min': 5*60,
    'remind_-5min': -5*60,
    'remind_+15min': 15*60,
    'remind_-15min': -15*60,
    'remind_+1h': 60*60,
    'remind_-1h': -60*60,
    'remind_+5h': 5*60*60,
    'remind_-5h': -5*60,
    'remind_+1d': 60*60*24,
    'remind_-1d': -60*60*24,
    'remind_+7d': 7*60*60*24,
    'remind_-7d': -7*60*60*24,
    'remind_+1month': 30*60*60*24,
    'remind_-1month': -30*60*60*24,
    'remind_+1y': 365*60*60*24,
    'remind_-1y': -365*60*60*24
}


def load_db(filename):
    data = {}
    try:
        with open(filename, 'rb') as file:
            for line in file:
                print(line)
                time_, chat_id, message = str(line, 'UTF-8').split('\t')
                message = message[:-1]
                time_ = int(time_)
                if time_ not in data:
                    data[time_] = []
                data[time_].append((chat_id, message))
    except FileNotFoundError:
        pass
    return data


def save_db(filename, data):
    with open(filename, 'wb') as file:
        for time_, reminders in data.items():
            for chat_id, message in reminders:
                out = '{time}\t{chat_id}\t{message}\n'.format(time=time_,
                                                              chat_id=chat_id,
                                                              message=message)
                file.write(bytes(out, 'UTF-8'))
    return


def setup(bot):
    bot.db = load_db('reminders.db')

    def monitor(bot):
        time.sleep(5)
        while True:
            now = int(time.time())
            times = [int(key) for key in bot.db]
            old_times = [t for t in times if t <= now]
            if len(old_times) > 0:
                for old_time in old_times:
                    for chat_id, message in bot.db[old_time]:
                        bot.send(message, chat_id=chat_id)
                    del bot.db[old_time]
                save_db('reminders.db', bot.db)
            time.sleep(5)

    thread = threading.Thread(target=monitor, args=(bot,), daemon=True)
    thread.start()


def remind(bot, message):
    if message.text.lower() == '/remind':
        message.answer("Вы не указали о чём напомнить!\n/remind какой-то-текст")
        return
    else:
        now = time.localtime(time.time())
        text = "Будет создано напоминание:\n" + \
               message.text[8:] + \
               "\nНа дату:\n" + \
               time.strftime("%Y-%m-%d %R", now)
        message.answer(text, keyboard=remind_kb)


def remind_cb(bot, callback):
    text = callback.message.text
    data = callback.data
    chat_id = callback.message.chat_id
    text_lines = text.split('\n')
    try:
        date_str = text_lines[3]
    except IndexError:
        callback.message.update("Произошла ошибка, попробуйте снова.")
        return
    date = time.strptime(date_str, "%Y-%m-%d %H:%M")
    date = int(time.mktime(date))
    if data == "remind_done":
        if date not in bot.db:
            bot.db[date] = []
        bot.db[date].append((chat_id, text_lines[1]))
        save_db('reminders.db', bot.db)
        text = "Cоздано напоминание:\n" + text_lines[1] + "\nНа дату:\n" + time.strftime("%Y.%m.%d %R", time.localtime(date))
        callback.message.update(text)
        return
    else:
        date += dates[data]
        text = text_lines[0] + "\n" + text_lines[1] + "\n" + text_lines[2] + "\n" + time.strftime("%Y.%m.%d %R", time.localtime(date))
        callback.message.update(text, keyboard=remind_kb)
    return


remind_cb.callbacks = ["^remind.*$"]
remind.commands = ['^/remind.*$']
remind.help = "Создаёт напоминание"


# с, сек*
# м, мин*
# ч, час*
# д, день, дней, дня

