import json
import re

import requests


kb = json.dumps({"inline_keyboard": [[{"text": "Отмена",
                                       "callback_data": 'sms_cancel'}]]})


def free_left(api_id):
    params = {"api_id": api_id, "json": 1}
    answer = requests.get("https://sms.ru/my/free", params=params).json()
    if answer["status"] == "OK":
        if answer["used_today"] is None:
            used = 0
        else:
            used = int(answer["used_today"])
        return answer["total_free"] - used
    else:
        return -1


def check_cost(api_id, phone, message):
    params = {"api_id": api_id,
              "to": phone,
              "msg": message,
              "json": 1}
    answer = requests.get("https://sms.ru/sms/cost", params=params).json()
    if answer["status"] != "OK":
        return -1
    else:
        return answer["total_cost"]


def send_sms(api_id, phone, message):
    params = {"api_id": api_id,
              "to": phone,
              "msg": message,
              "json": 1}
    answer = requests.get("https://sms.ru/sms/send", params=params).json()
    if answer["status"] != "OK":
        return -1
    else:
        sms = answer["sms"][phone]
        if sms["status"] == "OK":
            return "Сообщение отправлено\n/sms_status_{})".format(sms["sms_id"].replace("-", "_gfh"))
        else:
            return sms["status_text"]


def check_status(api_id, sms_id):
    params = {"api_id": api_id,
              "sms_id": sms_id,
              "json": 1}
    answer = requests.get("https://sms.ru/sms/status", params=params).json()
    if answer["status"] != "OK":
        return -1
    else:
        print(answer)
        sms = answer["sms"][sms_id]
        return sms["status_text"]


def sms(telebot, message):
    if "smsru_apikey" not in telebot.settings:
        message.answer("АПИ ключ не указан (\"smsru_apikey\": \"ABCDEF\") в settings.json")
        return
    if "smsru_number" not in telebot.settings:
        message.answer("Номер телефона не указан (\"smsru_number\": \"79001234567\") в settings.json")
        return

    left = free_left(telebot.settings["smsru_apikey"])
    if left == -1:
        message.answer("Произошла ошибка.")
    elif left == 0:
        message.answer("Бесплатные СМС кончились.")
    else:
        message.answer("Введите текст сообщения.\n"
                       "Не длиннее 70 символов кириллицы или 160 латинницы.\n"
                       "Осталось {} СМС на сегодня".format(left),
                       keyboard=kb)
        telebot.sms_waiting = True
    return


def sms_text(telebot, message):
    if hasattr(telebot, "sms_waiting") and telebot.sms_waiting is True:
        telebot.break_ = True
        telebot.sms_waiting = False
        cost = check_cost(telebot.settings["smsru_apikey"],
                          telebot.settings["smsru_number"],
                          message.text)
        if cost == -1:
            message.answer("Произошла ошибка.")
        elif cost > 0.0:
            message.answer("Цена смс больше 0. Отправка не произойдёт.")
        elif cost == 0.0:
            result = send_sms(telebot.settings["smsru_apikey"],
                              telebot.settings["smsru_number"],
                              message.text)
            message.answer(result)
        else:
            message.answer("Цена ниже 0, что-то не так.")
    return


def sms_status(telebot, message):
    try:
        text = message.text
        id = re.findall("^/sms_status[_ ](\d+)[-_](\d+)$", text)[0]
    except IndexError:
        message.answer("Укажите ID сообщения")
        return
    id = "{}-{}".format(id[0], id[1])
    message.answer("Статус сообщения {}:\n"
                   "{}".format(id, check_status(telebot.settings["smsru_apikey"], id)))
    return


def sms_cb(telebot, callback):
    data = callback.data
    if data == "sms_cancel":
        text = "Отправка отменена."
        callback.message.update(text)
        telebot.sms_waiting = False
        return


sms.commands = ["^/sms$"]
sms_text.commands = [".*"]
sms_status.commands = ["^/sms_status"]
sms_text.priority = "high"
sms_cb.callbacks = ["^sms.*$"]
sms.help = 'Отправляет СМС владельцу бота (не больше 5 в сутки, не длиннее 70 (160) символов)'
sms_status.help = 'Узнать успешность отправки смс'

# Пример модуля, перехватывающего любой ввод в процессе ожидание текста СМС
