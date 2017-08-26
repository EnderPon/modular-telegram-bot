import json

def remove_keyboard(bot, message):
    kb = json.dumps({'remove_keyboard': True})
    return message.answer(text='Removing keyboard', keyboard=kb)

remove_keyboard.commands = ['^/rm_kb$']
remove_keyboard.help = "Убирает клавиатуру"
