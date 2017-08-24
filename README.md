# modular-telegram-bot
Telegram bot supporting plugins (phenny-like)

Modules with names starting with "_" will be ignored


## Settings file:
* "key": "123456789:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
Telegram bot token

* "mode": "requests"
"requests" or "webhook"

* "cert_type": "selfsigned"
If mode is "webhook" chose type of certificate:
"selfsigned", "signed" or "none" (use none if you planing use nginx proxy with ssl)

* "cert_path": "./bot.crt"
Path to your ssl cert (if "cert_type" not "none")

* "pub_key": "./bot.pem"
Path to your public key (only for selfsigned cert)

* "url": "example.com/telegrambot"
url for telegram servers where to send updates

* "port": "8443"
port for telegram servers where to send updates

* "listen_on": "0.0.0.0"
ip or url to listen
(can be different from "url" if bot behind nginx proxy)

* "listen_port": "31337"
port to listen
(can be different from "port" if bot behind nginx proxy)

* "listen_route": "/telegrambot"
route for flask to listen for telegram updates
if not behind nginx proxy, must be same as in "url"
(can be "/" if bot behind nginx proxy)


## todo:
1. Модуль распределения прав
1.1 sudo
1.2 права по именам

2. Выбор между вебхуком и обычным способом

3. модуль RSS