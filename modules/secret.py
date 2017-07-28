def secret(telebot, message):
    message.answer("Secret!")
    return
secret.commands = ["^/secret$"]
secret.hidden = True
secret.help = "Секретная команда, которую не показывает help"
