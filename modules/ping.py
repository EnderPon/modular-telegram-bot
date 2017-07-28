def ping(telebot, message):
    message.answer("pong")
    return
ping.commands = ["^/ping$"]
ping.help = 'Просто отвечает словом pong'