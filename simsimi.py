#!/usr/bin/env python
#-*- coding:utf-8 -*-

import urllib2, urllib, cookielib
import json

'''
simsimi小黄鸡调用脚本
'''

HEADERS = {
    'Content-Type': 'application/json; charset=utf-8',
    'X-Requested-With': 'XMLHttpRequest',
    'Referer': 'http://www.simsimi.com/talk.htm?lc=ch',
    'Accept': 'application/json, text/javascript, */*; q=0.01'
}

BASE_URL = 'http://www.simsimi.com/func/req?lc=zh&'

def get_jsessionid(url):
    '''得到cookie'''
    cookie = cookielib.CookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie))
    response = opener.open(url)
    for item in cookie:
        if item.name == "JSESSIONID":
            HEADERS['Cookie'] = cookie
            return item.value

def add_cookie_in_headers(jsessionid):
    cookie = 'sagree=true;JSESSIONID=%s'%jsessionid
    HEADERS['Cookie'] = cookie

def reply(msg):
    reply_url = BASE_URL + msg
    reply_request = urllib2.Request(reply_url, headers=HEADERS)
    reply_json = urllib2.urlopen(reply_request).read()
    reply = json.loads(reply_json)
    if reply['response']:
        return reply['response']


if __name__ == '__main__':
    msg = raw_input('Input your message(q to quit):')
    while msg:
        if msg == 'q':
            break
        else:
            req = dict(msg=msg)
            req = urllib.urlencode(req)
            jsessionid = get_jsessionid(BASE_URL)
            add_cookie_in_headers(jsessionid)
            resp = reply(req)
            print resp
            msg = raw_input('Input your message(q to quit):')
