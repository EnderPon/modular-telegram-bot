import os.path

from telebot import *


def main():
    path = os.path.dirname(__file__)
    bot = Telebot(os.path.join(path, "settings.json"))
    if not bot.whoami():
        raise Exception("Whoami don`t work. Something gone wrong.")
    if bot.settings["mode"] == "requests":
        while True:
            time.sleep(1)
            bot.get_updates()
    if bot.settings["mode"] == "webhook":
        bot.start_webhook_loop()


if __name__ == '__main__':
    main()
