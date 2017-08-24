import json

import cherrypy


class WebHook(object):
    def __init__(self, bot):
        self.bot = bot
        print(bot.settings)
        cherrypy.config.update({
            "server.socket_host": bot.settings["listen_url"],
            "server.socket_port": int(bot.settings["listen_port"]),
        })
        return

    @cherrypy.expose
    def index(self, *args, **kwargs):
        cl = cherrypy.request.headers['Content-Length']
        rawbody = cherrypy.request.body.read(int(cl)).decode()
        message = json.loads(rawbody)
        # print("-----------")
        # print(message)
        # print(self.bot.request("getWebhookInfo"))
        # print("-----------")
        if len(message) == 0:
            return
        self.bot.parse_update(message)
        return
