import json
import re

import requests


kb = json.dumps({"inline_keyboard": [[{"text": "Отмена",
                                       "callback_data": 'sms_cancel'}]]})

send_kb = json.dumps({"inline_keyboard": [[{"text": "Отправить",
                                            "callback_data": 'sms_confirm'},
                                           {"text": "Отмена",
                                            "callback_data": 'sms_cancel'}
                                           ]]})


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
            return "Сообщение отправлено\n/sms_status_{}".format(sms["sms_id"].replace("-", "_"))
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
        sms_ = answer["sms"][sms_id]
        return sms_["status_text"]


def send_conf(telebot, message, text):
    cost = check_cost(telebot.get_setting("apikey"),
                      telebot.get_setting("number"),
                      text)
    if cost == -1:
        message.answer("Произошла ошибка.")
    elif cost > 0.0:
        message.answer("Цена смс больше 0. Отправка не произойдёт.")
    elif cost == 0.0:
        sender = message.from_["id"]
        if "username" in message.from_:
            sender = message.from_["username"]
        elif "first_name" in message.from_:
            sender = message.from_["first_name"]
        elif "last_name" in message.from_:
            sender = message.from_["last_name"]
        message.answer("Будет отправленно сообщение:\n{}:\n{}".format(sender, text),
                       keyboard=send_kb)
    else:
        message.answer("Цена ниже 0, что-то не так.")


def sms(telebot, message):
    # if "smsru_apikey" not in telebot.settings:
    #     message.answer("АПИ ключ не указан /config")
    #     return
    # if "smsru_number" not in telebot.settings:
    #     message.answer("Номер телефона не указан /config")
    #     return

    if telebot.state is not None:
        if telebot.state["state"] == "waiting for sms":
            send_conf(telebot, message, message.text)
        telebot.clear_state()
        return

    left = free_left(telebot.get_setting("apikey"))
    if left == -1:
        message.answer("Произошла ошибка.")
    elif left == 0:
        message.answer("Бесплатные СМС кончились.")
    else:
        text = message.text.strip()
        if text.lower() == "/sms":
            message.answer("Введите текст сообщения.\n"
                           "Не длиннее 70 символов кириллицы или 160 латинницы.\n"
                           "Осталось {} СМС на сегодня".format(left),
                           keyboard=kb)
            telebot.set_state("waiting for sms")
        else:
            text = text[4:].strip()
            send_conf(telebot, message, text)
    return


def sms_status(telebot, message):
    try:
        text = message.text
        message_id = re.findall("^/sms_status[_ ](\d+)[-_](\d+)$", text)[0]
    except IndexError:
        message.answer("Использование: /sms_status message_id")
        return
    message_id = "{}-{}".format(message_id[0], message_id[1])
    message.answer("Статус сообщения {}:\n"
                   "{}".format(message_id, check_status(telebot.get_setting("apikey", module="sms"), message_id)))
    return


def sms_cb(telebot, callback):
    data = callback.data
    if data == "sms_cancel":
        text = "Отправка отменена."
        callback.message.update(text)
        telebot.clear_state()
        return
    if data == "sms_confirm":
        lines = callback.message.text.split("\n")
        message_ = ""
        for i in lines[1:]:
            message_ += i + "\n"
        message_ = message_[:-1]
        callback.message.update(callback.message.text)
        result = send_sms(telebot.get_setting("apikey", module="sms"),
                          telebot.get_setting("number", module="sms"),
                          message_)
        callback.message.answer(result)
        return


sms.commands = ["^/sms[^_]", "^/sms$"]
sms.settings = {"apikey": "", "number": "\d{10}"}
sms_status.commands = ["^/sms_status"]
sms_cb.callbacks = ["^sms.*$"]
sms.help = 'Отправляет СМС владельцу бота (не больше 5 в сутки, не длиннее 70 (160) символов)'
sms_status.help = 'Узнать успешность отправки смс'
