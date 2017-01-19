# -*- coding: utf-8 -*-
import tornado.escape
import tornado.web


class Index(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html")

    def post(self):
        pass
