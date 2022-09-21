import cherrypy
from telebot.types import Update
from time import sleep
from bot.util import bot

WEBHOOK_HOST = "..."
WEBHOOK_PORT = 8443  # 443, 80, 88 или 8443 (порт должен быть открыт!)
WEBHOOK_LISTEN = '0.0.0.0'  # На некоторых серверах придется указывать такой же IP, что и выше

WEBHOOK_SSL_CERT = 'bot/pub_key.crt'  # Путь к сертификату
WEBHOOK_SSL_PRIV = 'bot/priv_key.key'  # Путь к приватному ключу


WEBHOOK_URL_BASE = "https://%s:%s" % (WEBHOOK_HOST, WEBHOOK_PORT)
WEBHOOK_URL_PATH = "/%s/" % bot.token


class WebhookServer(object):
    @cherrypy.expose
    def index(self):
        if 'content-length' in cherrypy.request.headers and \
                        'content-type' in cherrypy.request.headers and \
                        cherrypy.request.headers['content-type'] == 'application/json':
            length = int(cherrypy.request.headers['content-length'])
            json_string = cherrypy.request.body.read(length).decode("utf-8")
            update = Update.de_json(json_string)
            bot.process_new_updates([update])
            return ''
        else:
            raise cherrypy.HTTPError(403)


def start_server():
    bot.remove_webhook()

    sleep(1)
    # Ставим заново вебхук
    bot.set_webhook(url=WEBHOOK_URL_BASE + WEBHOOK_URL_PATH,
                    certificate=open(WEBHOOK_SSL_CERT, 'r'))

    cherrypy.config.update({
        'server.socket_host': WEBHOOK_LISTEN,
        'server.socket_port': WEBHOOK_PORT,
        #'server.ssl_module': 'pyopenssl',
        'server.ssl_module': 'builtin',
        'server.ssl_certificate': WEBHOOK_SSL_CERT,
        'server.ssl_private_key': WEBHOOK_SSL_PRIV
    })

    # Собственно, запуск!
    cherrypy.quickstart(WebhookServer(), WEBHOOK_URL_PATH, {'/': {}})
