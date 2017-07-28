def help(bot, message):
    commands = []
    for cmd, funcs in bot.commands.items():
        if not hasattr(funcs[0], 'hidden'):
            if hasattr(funcs[0], 'help'):
                help = funcs[0].help
            else:
                help = ""
            commands.append((cmd.pattern.strip('^$*.'), help))

    commands.sort()
    commands_str = ""
    for cmd in commands:
        commands_str += cmd[0] + ' ' + cmd[1] + '\n'
    message.answer(commands_str)
    return

help.commands = ['^/help$']
help.help = "Выводит список команд и описание первой функции этой команды"