import tornado.web
import tornado.httpserver
from tornado.options import define, options

from config import *

define("port", default=8081, help="run on the given port", type=int)


class Application(tornado.web.Application):
    def __init__(self):
        tornado.web.Application.__init__(self, handlers,template_path=os.path.join(os.path.dirname(__file__), "templates"),static_path=os.path.join(os.path.dirname(__file__), "static"))



if __name__ == '__main__':
	# app = Application()
	tornado.options.parse_command_line()
	app = tornado.web.Application(handlers,template_path=os.path.join(os.path.dirname(__file__), "templates"),static_path=os.path.join(os.path.dirname(__file__), "static"))
	http_server = tornado.httpserver.HTTPServer(app)
	http_server.listen(options.port)
	print 'Start listening on port 8081'
	tornado.ioloop.IOLoop.instance().start()
    
