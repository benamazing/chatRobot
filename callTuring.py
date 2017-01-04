#coding=utf-8
# -*- coding: utf-8 -*-

import sys, urllib, urllib2, json

turing_url = 'http://www.tuling123.com/openapi/api'
api_key = '462d0950420a46ce99911c68bd032ae4'

import urllib
import urllib2

values = {}
values['key'] = api_key
values['info'] = '你好吗？'
values['userid'] = '12345678'
data = urllib.urlencode(values)
request = urllib2.Request(turing_url, data)
response = urllib2.urlopen(request)
print response.read()

