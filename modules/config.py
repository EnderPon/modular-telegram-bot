import json


def config(telebot, message):
    if message.from_["username"] != telebot.settings["admin_username"]:
        return

    if type(message).__name__ == "Message":
        if telebot.state is None:
            config_kb = {"inline_keyboard": []}
            for module in telebot.modules_settings:
                config_kb["inline_keyboard"].append([{"text": module.__name__, "callback_data": "config-mod-" + module.__name__}])

            if len(config_kb["inline_keyboard"]) == 0:
                message.answer("Нет модулей поддерживающих настройки")
            else:
                message.answer("Выберите модуль для настройки", keyboard=json.dumps(config_kb))
            return
        else:
            state = json.loads(telebot.state["state"])
            telebot.set_setting(state["setting"], message.text)
            telebot.clear_state()
            message.answer("Настройка сохранена")

    if type(message).__name__ == "Callback":
        callback = message
        data = callback.data.split("-")
        mode = data[1]
        if mode == "mod":
            function_name = data[2]
            function_ = telebot.variables[function_name]

            config_kb = {"inline_keyboard": []}
            for setting in telebot.modules_settings[function_]:
                config_kb["inline_keyboard"].append(
                    [{"text": setting, "callback_data": "config-set-" + function_name + "-" + setting}])

            callback.message.update("Выберите настройку для модуля " + function_name, keyboard=json.dumps(config_kb))
        if mode == "set":
            function_name = data[2]
            setting_name = data[3]
            callback.message.update("Отправьте новое состояние {} для модуля {} ".format(setting_name, function_name))
            telebot.set_state(json.dumps({"module": function_name, "setting": setting_name}))
        return


config.commands = ["^/config$"]
config.help = 'Настройка бота'
config.hidden = True
config.callbacks = ["^config.*$"]
