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
        print(kwargs)
        self.bot.parse_update(kwargs)
        return

if __name__ == "__main__":
    cherrypy.quickstart(WebHook("dfhgasdfg"), '/test')