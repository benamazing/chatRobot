__author__ = 'LIBE5'
import tornado.escape
import tornado.web
from config import *

class Sample(tornado.web.RequestHandler):
    def get(self):
        self.render("sample.html")
    def post(self):
        self.get()