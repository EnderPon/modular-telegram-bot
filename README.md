# modular-telegram-bot
Telegram bot supporting plugins (phenny-like)

Modules with names starting with "_" will be ignored


## Settings file:
* "key": "123456789:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"<br />
Telegram bot token

* "mode": "requests"<br />
"requests" or "webhook"

* "cert_type": "selfsigned"<br />
If mode is "webhook" chose type of certificate:<br />
"selfsigned", "signed" or "none" (use none if you planing use nginx proxy with ssl)

* "cert_path": "./bot.crt"<br />
Path to your ssl cert (if "cert_type" not "none")

* "cert_chain": "./bot_chain.crt"<br />
Path to your ssl cert chain (if "cert_type" is "signed")

* "priv_key": "./bot.pem"<br />
Path to your private key (if "cert_type" not "signed")

* "url": "example.com"<br />
url for telegram servers where to send updates

* "port": "8443"<br />
port for telegram servers where to send updates

* "route": "/telegrambot"<br />
route for telegram servers where to send updates

* "listen_on": "0.0.0.0"<br />
ip or url to listen<br />
(can be different from "url" if bot behind nginx proxy)

* "listen_port": "31337"<br />
port to listen<br />
(can be different from "port" if bot behind nginx proxy)

* "listen_route": "/telegrambot"<br />
route for cherrypy to listen for telegram updates<br />
if not behind nginx proxy, must be same as in "url"<br />
(can be "" if bot behind nginx proxy)<br />
You should use your token as route to be sure than only telegram knows it.

* "admin_username": "username"<br />
username for user who can use /config module

* "log_level": 0<br />
logging level (from -1 (silent) to 2 (verbose))

* "https_proxy": "socks5h://user:passwords@example.com:1080"<br />
proxy for requests mode (if needed)

## todo:
1. Модуль распределения прав
    1. супер-пользователь с полными правами
    1. права по именам
    1. права по ролям
2. при окончании работы закрывать вебхук
3. модуль RSS
4. модуль reload
5. модуль для реализации чата "клиент-оператор"
