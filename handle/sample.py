__author__ = 'LIBE5'
import tornado.escape
import tornado.web
from config import *

class Sample(tornado.web.RequestHandler):
    def get(self):
        user = {}
        user['name'] = 'ben'
        user['age'] = 30
        user['cars'] = ['benz', 'bmw', 'honda']
        self.render("sampleTemplateWithVariables.html", user=user)
    def post(self):
        self.get()