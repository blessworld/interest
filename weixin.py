#!/usr/bin/env python
#-*- coding:utf-8 -*-
"""
微信公众号, 发送书名返回豆瓣读书该书的评分及简介
采用web.py编写, 部署在BAE上, TOKEN为自己在微信公众平台设置的Token
"""


import web

import hashlib
from lxml import etree
import urllib
import urllib2
import json

urls = (
    '/', 'weixin',
)

config = {"TOKEN": "lastmayday"}


class weixin:
    def GET(self):
        data = web.input()
        signature = data.signature
        timestamp = data.timestamp
        nonce = data.nonce
        echostr = data.echostr
        token = config['TOKEN']
        tmplist = [token, timestamp, nonce]
        tmplist.sort()
        tmpstr = ''.join(tmplist)
        hashstr = hashlib.sha1(tmpstr).hexdigest()
        if hashstr == signature:
            return echostr
        print signature, timestamp, nonce
        print tmpstr, hashstr
        return 'Error: ' + echostr

    def POST(self):
        #接收微信的请求内容
        data = web.data()
        #解析XML内容
        root = etree.fromstring(data)
        child = list(root)
        recv = {}
        for i in child:
            recv[i.tag] = i.text

        q = recv['Content']
        if q == 'Hello2BizUser':
            recv['Content'] = '欢迎使用豆瓣读书信息查询~请发送书本名称然后豆瓣读书信息就会发给你啦~^ ^'
            textTpl = """<xml>
                <ToUserName><![CDATA[%s]]></ToUserName>
                <FromUserName><![CDATA[%s]]></FromUserName>
                <CreateTime>%s</CreateTime>
                <MsgType><![CDATA[%s]]></MsgType>
                <Content><![CDATA[%s]]></Content>
                <FuncFlag>0</FuncFlag>
                </xml>"""
            echostr = textTpl % (recv['FromUserName'], recv['ToUserName'],
                                 recv['CreateTime'], recv['MsgType'],
                                 recv['Content'])
            return echostr

        params = urllib.urlencode({'q': q, 'count': 1})
        url = "https://api.douban.com/v2/book/search?" + params
        req = urllib2.urlopen(url)
        response_json = req.read()
        response = json.loads(response_json)
        details = response['books'][0]
        rating = details['rating']['average']
        title = details['title']
        douban = details['alt']
        image = details['images']['large']
        summary = details['summary']
        description = "评分: " + rating + '\n' + "简介: " + summary
        textTpl = """
            <xml>
            <ToUserName><![CDATA[%s]]></ToUserName>
            <FromUserName><![CDATA[%s]]></FromUserName>
            <CreateTime>%s</CreateTime>
            <MsgType><![CDATA[news]]></MsgType>
            <ArticleCount>1</ArticleCount>
            <Articles>
            <item>
            <Title><![CDATA[%s]]></Title>
            <Description><![CDATA[%s]]></Description>
            <PicUrl><![CDATA[%s]]></PicUrl>
            <Url><![CDATA[%s]]></Url>
            </item>
            </Articles>
            <FuncFlag>1</FuncFlag>
            </xml>
        """
        echostr = textTpl % (recv['FromUserName'], recv['ToUserName'],
                             recv['CreateTime'], title, description,
                             image, douban)
        return echostr


app = web.application(urls, globals()).wsgifunc()
from bae.core.wsgi import WSGIApplication
application = WSGIApplication(app)
