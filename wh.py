import json
import atexit

import cherrypy


class WebHook(object):
    def __init__(self, bot):
        self.bot = bot
        settings = self.bot.settings
        print(bot.settings)
        conf = {
                    # 'environment': 'production',
                    'engine.autoreload.on': False,  # todo: заменить на продакшн-режим
                    "server.socket_host": bot.settings["listen_url"],
                    "server.socket_port": int(bot.settings["listen_port"]),
                }
        if settings["cert_type"] != "none":
            conf["server.ssl_module"] = 'builtin'
            conf["server.ssl_certificate"] = settings["cert_path"]
            conf["server.ssl_private_key"] = settings["priv_key"]
        if settings["cert_type"] == "signed":
            conf["server.ssl_certificate_chain"] = settings["cert_chain"]

        cherrypy.config.update(conf)
        return

    @cherrypy.expose
    def index(self, *args, **kwargs):
        cl = cherrypy.request.headers['Content-Length']
        rawbody = cherrypy.request.body.read(int(cl)).decode()
        message = json.loads(rawbody)
        if len(message) == 0:
            return
        self.bot.parse_update(message)
        return
