#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import web
import nlp_basic_web


urls = [
    # sub modules
    '/nlp', nlp_basic_web.app_nlp,

    # main functionality
    '/', 'index',
]


class index:
    def GET(self):
        # redirect to the static file ...
        raise web.seeother('/static/index.html')


if __name__ == "__main__":
    app = web.application(urls, globals())
    HOST_PORT = 8080
    web.httpserver.runsimple(app.wsgifunc(), ("0.0.0.0", HOST_PORT))
