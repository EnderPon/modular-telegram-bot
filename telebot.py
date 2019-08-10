import os
import os.path
import re
import json
import importlib
import time
import threading

import requests
import cherrypy

import wh
import db


class Telebot:
    def __init__(self, settings_file=None):
        self.path = os.path.dirname(__file__)
        if settings_file is None:
            self.gen_settings_file(self.path_join("settings.json"))
        try:
            self.settings = json.load(open(settings_file, 'r'))
        except FileNotFoundError:
            self.gen_settings_file(settings_file)
        self.api_key = self.settings["key"]
        if "https_proxy" in self.settings and self.settings["https_proxy"] != "":
            self.proxy = {"https": self.settings["https_proxy"]}
        else:
            self.proxy = {}
        self.offset = 0
        self.db = db.DB()
        self.variables = {}
        self.current_state = None
        self.state = None
        self.modules_settings_list = {}
        self.user_states = {}
        self.mod_settings = {}
        self.commands = {"high": {}, "mid": {}, "low": {}}
        self.priorities = {}
        self.reg_cb = {}
        self.callbacks = {}
        self.setup()
        self.offset = 0
        self.wh = None
        self.stop_webhook()  # stopping old webhook in case it was not stopped correctly
        pass

    def log(self, *args, lvl=0):
        # три уровня вывода: 0, 1, 2
        # 0 - обычные сообщения
        # 1 - подробные
        # 2 - очень подробные
        # -1 - игнорируем все сообщения
        if self.settings["log_level"] < lvl:
            # выводим только сообщения того же уровня или ниже
            return
        if len(args) == 0:
            return
        else:
            out = ""
            for i in args:
                out += "{} ".format(i)
            out = out[:-1]
        print("{}: {}".format(time.strftime("%Y-%m-%d %H:%M"),
                              out))
        return

    def path_join(self, path):
        return os.path.join(self.path, path)

    def gen_settings_file(self, settings_file):
        with open(settings_file, 'w') as file:
            json.dump({
                "key": "123456789:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
                "mode": "requests",
                "cert_type": "selfsigned",
                "cert_path": "./bot.crt",
                "cert_chain": "./chain.pem",
                "priv_key": "./priv.pem",
                "port": "8443",
                "url": "example.com",
                "route": "/telegrambot",
                "listen_port": "31337",
                "listen_url": "0.0.0.0",
                "listen_route": "/telegrambot",
                "db_prefix": "telebot",
                "admin_username": "username",
                "log_level": 0,
                "https_proxy": ""
            }, file, indent=2)
            self.log("Created example settings.json", lvl=0)
            exit()

    def setup(self):
        filenames = []
        for fn in os.listdir(self.path_join('modules')):
            if fn.endswith('.py') and not fn.startswith('_'):
                filenames.append(os.path.join(self.path, 'modules', fn))
        modules = []
        for filename in filenames:
            name = os.path.basename(filename)[:-3]
            try:
                module_ = importlib.import_module("modules."+name)
            except Exception as e:
                self.log("Import error:", e)
            else:
                if hasattr(module_, 'setup'):
                    module_.setup(self)
                self.register(vars(module_))
                modules.append(name)
        self.log("Loaded modules:", modules)
        self.bind_commands()
        self.bind_callbacks()
        self.load_db()
        if self.settings["mode"] == "requests":
            pass
        elif self.settings["mode"] == "webhook":
            self.setup_webhook()
        return

    def register(self, variables):
        for name, obj in variables.items():
            if hasattr(obj, "commands"):
                self.variables[name] = obj
            if hasattr(obj, 'callbacks'):
                self.reg_cb[name] = obj
            if hasattr(obj, "priority"):
                self.priorities[name] = obj.priority
            else:
                self.priorities[name] = "mid"
            if hasattr(obj, "settings"):
                self.modules_settings_list[obj] = obj.settings
        return

    def bind_commands(self):
        def bind(self, regexp, func, name):
            self.commands[self.priorities[name]].setdefault(regexp, []).append(func)

        for name, func in self.variables.items():
            for command in func.commands:
                regexp = re.compile(command)
                bind(self, regexp, func, name)

    def bind_callbacks(self):
        def bind(self, regexp, func):
            self.callbacks.setdefault(regexp, []).append(func)

        for name, func in self.reg_cb.items():
            for command in func.callbacks:
                regexp = re.compile(command)
                bind(self, regexp, func)

    def call(self, func, message):
        try:
            self.current_state = {"function": func.__name__, "chat": message.chat_id, "from": message.from_id}
            func(self, message)
            self.current_state = None
        except KeyboardInterrupt as e:
            self.error(e)

    def error(self, e):
        self.log(e)

    def load_db(self):
        self.user_states = self.db.get_all_states()
        self.mod_settings = self.db.get_all_settings()
        return

    def request(self, method, **kwargs):
        url = "https://api.telegram.org/bot" + self.api_key + '/' + method
        self.log("sending request:\nURL: {}\nDATA: {}".format(url, kwargs), lvl=2)
        if len(self.proxy) > 0:
            answer = requests.post(url, data=kwargs, proxies=self.proxy)
        else:
            answer = requests.post(url, data=kwargs)
        self.log("request answer: {}".format(answer.text), lvl=2)
        try:
            req = answer.json()
        except ValueError:
            raise Exception("Error parsing JSON:\n{}".format(answer.text))
        if req['ok'] is False:
            self.log("error in request?", req)
        return req

    def send(self, text, dialog=None, message=None, chat_id=None, keyboard=None, message_id=None):
        if dialog is None and message is None and id is None:
            raise Exception('Need dialog, message or id to answer.')
        if dialog is not None:
            chat_id = dialog['chat_id']
        elif message is not None:
            chat_id = message['chat_id']
        else:
            chat_id = chat_id
        if message_id is None:
            self.log("Sending message to {}\nText: {}".format(chat_id, text), lvl=1)
            self.request('sendMessage', text=text, chat_id=chat_id, reply_markup=keyboard)
        else:
            self.log("Updating message to {}\nText: {}".format(chat_id, text), lvl=1)
            self.request('editMessageText', text=text, chat_id=chat_id,
                         reply_markup=keyboard, message_id=message_id)

    def whoami(self):
        answer = self.request("getMe")
        if answer["ok"] is True:
            answer = answer["result"]
            self.log("My id is " + str(answer["id"]))
            self.log("My name is " + str(answer["first_name"]))
            self.log("My username is @" + str(answer["username"]))
            time.sleep(0.1)
            return True
        else:
            return False

    def parse_update(self, message):
        if "channel_post" in message or "edited_channel_post" in message:
            # self.request("leaveChat", chat_id=message["chat"]["id"])
            self.log("Got channel message, ingnoring!", lvl=1)
            return
        if 'update_id' in message:
            self.offset = message['update_id']
        if 'message' in message:
            message = message['message']
            mess_obj = Message(self, message)
            try:
                text = message['text']
            except KeyError:
                return
            self.state = self.db.get_state(mess_obj.chat_id, mess_obj.from_id)
            if self.state is not None:
                self.call(self.variables[self.state["module"]], mess_obj)
                return
            for p in ("high", "mid", "low"):
                for command in self.commands[p]:
                    if command.match(text):
                        for func in self.commands[p][command]:
                            self.call(func, mess_obj)
        elif 'callback_query' in message:
            callback = message['callback_query']
            cb_obj = Callback(self, callback)
            data = callback['data']
            for cb in self.callbacks:
                if cb.match(data):
                    for func in self.callbacks[cb]:
                        self.call(func, cb_obj)
        else:
            pass

    def get_updates(self):
        for message in self.request("getUpdates", offset=self.offset+1)['result']:
            self.log("Got message: {}".format(message), lvl=1)
            self.parse_update(message)
        return

    def setup_webhook(self):
        self.wh = wh.WebHook(self)
        pass

    def wh_request(self):
        url = "https://api.telegram.org/bot" + self.api_key + '/' + "setWebhook"
        if self.settings['cert_type'] == "selfsigned":
            files = {"certificate": open(self.settings["cert_path"], "rb")}
        else:
            files = None
        if self.settings['route'][-1] != "/":
            self.settings['route'] += "/"
            # cherrypy listening on "example.com/route/" and returning 301
            # if someone trying to access "example.com/route"
        data = {
            "url": self.settings["url"] + ":" + str(self.settings["port"]) + self.settings["route"]
        }
        return requests.post(url, data=data, files=files)

    def start_webhook_loop(self):
        def start_webhook():
            time.sleep(1)
            self.wh_request()
            wh_status = self.request("getWebhookInfo")["result"]
            self.log(wh_status)
            self.log("Last error time: {}\nLast error text: {}\nHas custom cert: {}\nURL: {}\nPending: {}".format(
                wh_status["last_error_date"],
                wh_status["last_error_message"],
                wh_status["has_custom_certificate"],
                wh_status["url"],
                wh_status["pending_update_count"]
            ))

        thread_start = threading.Thread(target=start_webhook, daemon=True)
        thread_start.start()
        cherrypy.quickstart(self.wh, self.settings['listen_route'])

    def stop_webhook(self):
        self.log("stoping webhook:", self.request("deleteWebhook"))

    def set_state(self, text, module=None):
        """
        Сохраняем состояние в базу, на случай выключения бота
        """
        state = self.current_state
        chat = state["chat"]
        from_ = state["from"]
        if module is None:
            module = state["function"]
        if chat not in self.user_states:
            self.user_states[chat] = {}
        self.user_states[chat][from_] = {"module": module, "state": text}
        self.db.set_state(chat, from_, module, text)
        return

    def clear_state(self):
        state = self.current_state
        try:
            del self.user_states[state["chat"]][state["from"]]
        except KeyError:
            pass
        self.db.clear_state(state["chat"], state["from"])
        return

    def set_setting(self, setting_name, setting_state, module=None):
        state = self.current_state
        if module is None:
            module = state["function"]
        if module not in self.mod_settings:
            self.mod_settings[module] = {}
        self.mod_settings[module][setting_name] = setting_state
        self.db.set_setting(module, setting_name, setting_state)
        return

    def get_setting(self, setting_name, module=None):
        state = self.current_state
        if module is None:
            module = state["function"]
        try:
            return self.mod_settings[module][setting_name]
        except KeyError:
            pass
        try:
            return self.db.get_setting(module, setting_name)
        except KeyError:
            pass
        return None


class Message:
    def __init__(self, bot, message):
        self.bot = bot
        try:
            self.text = message['text']
        except KeyError:
            pass
        self.from_ = message['from']
        self.chat = message['chat']
        self.id = message["message_id"]
        self.chat_id = self.chat['id']
        self.from_id = self.from_['id']
        return

    def answer(self, text, keyboard=None):
        return self.bot.send(text, chat_id=self.chat_id, keyboard=keyboard)

    def update(self, text, keyboard=None):
        return self.bot.send(text, chat_id=self.chat_id, keyboard=keyboard, message_id=self.id)


class Callback:
    def __init__(self, bot, callback):
        self.bot = bot
        self.data = callback['data']
        self.message = Message(bot, callback['message'])
        self.from_ = callback['from']
        self.chat = self.message.chat
        self.chat_id = self.chat['id']
        self.from_id = self.from_['id']
        return


class Dialog:
    def __init__(self):
        pass
