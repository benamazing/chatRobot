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
            for news in responseObj['list']:
                resultString += "标题:" + news['artical'] + "\r\n"
                resultString += "来源:" + news['source'] + "\r\n"
                resultString += "链接:" + news['detailurl'] + "\r\n"
                print resultString
            return resultString
        if responseObj['code'] == 308000:
            print responseObj['text']
            resultString = responseObj['text'] + "\r\n"
            for food in responseObj['list']:
                resultString += "菜名:" + food['name'] + "\r\n"
                resultString += "图片:" + food['icon'] + "\r\n"
                resultString += "信息:" + food['info'] + "\r\n"
                resultString += "链接:" + food['detailurl'] + "\r\n"
                print resultString
            return resultString
        return response.read()
