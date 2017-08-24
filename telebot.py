import os
import re
import json
import importlib
import time

import requests
import cherrypy

import wh


class Telebot:
    def __init__(self, settings_file=None):
        if settings_file is None:
            with open('settings.json', 'w') as file:
                json.dump({"key": "123456789:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
                           "mode": "requests",
                           "cert_type": "selfsigned",
                           "cert_path": "./bot.crt",
                           "pub_key": "./bot.pem",
                           "port": "8443",
                           "url": "example.com/telegrambot",
                           "listen_port": "31337",
                           "listen_url": "0.0.0.0"}, file, indent=2)
                print("Created example settings.json")
                exit()
        self.settings = json.load(open(settings_file, 'r'))
        self.api_key = self.settings["key"]
        self.offset = 0
        self.home = os.getcwd()
        self.variables = {}
        self.commands = {"high": {}, "mid": {}, "low": {}}
        self.priorities = {}
        self.reg_cb = {}
        self.callbacks = {}
        self.break_ = False  # can be set to True by any module to prevent other modules from work with command.
        self.setup()
        self.offset = 0
        pass

    def setup(self):
        filenames = []
        for fn in os.listdir(os.path.join(self.home, 'modules')):
            if fn.endswith('.py') and not fn.startswith('_'):
                filenames.append(os.path.join(self.home, 'modules', fn))
        modules = []
        for filename in filenames:
            name = os.path.basename(filename)[:-3]
            try:
                module_ = importlib.import_module("modules."+name)
            except Exception as e:
                print("Import error:", e)
            else:
                if hasattr(module_, 'setup'):
                    module_.setup(self)
                self.register(vars(module_))
                modules.append(name)
        print("Loaded modules:", modules)
        self.bind_commands()
        self.bind_callbacks()
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

    def call(self, func, telebot, message):
        try:
            func(telebot, message)
        except Exception as e:
            self.error(e)

    def error(self, e):
        print(e)

    def request(self, method, **kwargs):
        url = "https://api.telegram.org/bot" + self.api_key + '/' + method
        req = requests.get(url, params=kwargs).json()
        if req['ok'] is False:
            print("error in request?", req)
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
            self.request('sendMessage', text=text, chat_id=chat_id, reply_markup=keyboard)
        else:
            self.request('editMessageText', text=text, chat_id=chat_id,
                         reply_markup=keyboard, message_id=message_id)

    def whoami(self):
        answer = self.request("getMe")
        if answer["ok"] is True:
            answer = answer["result"]
            print("My id is " + str(answer["id"]))
            print("My name is " + str(answer["first_name"]))
            print("My username is @" + str(answer["username"]))
            time.sleep(0.1)
            return True
        else:
            return False

    def parse_update(self, message):
        self.offset = message['update_id']
        self.break_ = False
        if 'message' in message:
            message = message['message']
            mess_obj = Message(self, message)
            text = message['text']
            for p in ("high", "mid", "low"):
                for command in self.commands[p]:
                    if command.match(text):
                        for func in self.commands[p][command]:
                            if not self.break_:
                                func(self, mess_obj)
                            else:
                                break
        elif 'callback_query' in message:
            callback = message['callback_query']
            cb_obj = Callback(self, callback)
            data = callback['data']
            for cb in self.callbacks:
                if cb.match(data):
                    for func in self.callbacks[cb]:
                        func(self, cb_obj)
        else:
            pass

    def get_updates(self):
        for message in self.request("getUpdates", offset=self.offset+1)['result']:
            self.parse_update(message)
        return

    def setup_webhook(self):
        self.wh = wh.WebHook(self)
        pass

    def start_webhook_loop(self):
        cherrypy.quickstart(self.wh, self.settings['listen_route'])
        pass

    def stop_webhook(self):
        pass


class Message:
    def __init__(self, bot, message):
        self.bot = bot
        self.text = message['text']
        self.from_ = message['from']
        self.chat = message['chat']
        self.id = message["message_id"]
        self.chat_id = self.chat['id']
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
        return


class Dialog:
    def __init__(self):
        pass
