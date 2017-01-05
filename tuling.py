#coding=utf-8
# -*- coding: utf-8 -*-

import sys, urllib, urllib2, json
reload(sys)
sys.setdefaultencoding('utf-8')

class Tuling(object):
    def __init__(self, url, apikey):
        self.url = url
        self.apikey = apikey

    def chat(self, info, userid, loc=None):
        values = {}
        values['key'] = self.apikey
        values['info'] = info
        values['userid'] = userid
        if loc is not None:
            values['loc'] = loc
        print info
        data = urllib.urlencode(values)
        print data
        request = urllib2.Request(self.url, data)
        response = urllib2.urlopen(request)
        responseObj = json.loads(response.read())
        if responseObj['code'] == 100000:
            return responseObj['text']
        if responseObj['code'] == 200000:
            return responseObj['text'] + "\r\n" + responseObj['url']
        if responseObj['code'] == 302000:
            resultString = ''.join(responseObj['text'] + "\r\n")
            ind = 0
            for news in responseObj['list']:
                if ind < 3:
                    resultString += str(ind + 1) + ". 标题:" + news['article'] + "\r"
                    resultString += "来源:" + news['source'] + "\r"
                    resultString += "链接:" + news['detailurl'] + "\r\n"
                    ind += 1
                print resultString
            return resultString

        if responseObj['code'] == 308000:
            articles = [{"title": food['name'], "description": food['info'], "picurl": food['icon'], "url": food['detailurl']} for food in responseObj['list'][:3]]
            return articles
        return response.read()

