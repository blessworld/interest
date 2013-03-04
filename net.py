#!/usr/bin/env python
#-*- coding:utf-8 -*-

import urllib2
import cookielib
from base64 import b64encode
from socket import socket, SOCK_DGRAM, AF_INET
from bs4 import BeautifulSoup

'''
华中科技大学校园网无线网脚本
'''

username = 'dq096283'
password = '******'

HOST = '192.168.50.2'
ROOT_URL = 'http://192.168.50.2:8080/portal/hust/desk/'
INDEX_PAGE = 'index.jsp'
LOGIN_PAGE = 'onlogin.jsp'
ONLINE_PAGE = 'login_succ.jsp'

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:17.0) \
                   Gecko/20100101 Firefox/17.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*; \
               q=0.8',
    'Accept-Language': 'zh-cn,zh;q=0.8,en-us;q=0.5,en;q=0.3',
    'Accept-Encoding': 'gzip, deflate',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Connection': 'keep-alive',
    'Referer': 'http://192.168.50.2:8080/portal/hust/desk/index.jsp',
    'Content-Length': '85'
}


def get_ip():
    s = socket(AF_INET, SOCK_DGRAM)
    s.connect((HOST, 0))
    return s.getsockname()[0]


def get_jsessionid(url):
    cookie = cookielib.CookieJar()
    for item in cookie:
        if item.name == 'JSESSIONID':
            HEADERS['Cookie'] = cookie
            return item.value


def add_cookie_in_headers(username, jsessionid):
    cookie = 'hello1={0};hello2=true;hello3=%CB%CE%CE%CA%CC%CE;JSESSIONID={1}'
    cookie.format(username, jsessionid)
    HEADERS['Cookie'] = cookie


def login(username, password, jsessionid, ip):
    password = b64encode(password)
    login_url = ROOT_URL + LOGIN_PAGE
    login_data = 'userName={0}&userPwd={1}&serviceType=&isSavePwd=on&\
                  isQuickAuth=false&language=English&browserFinalUrl=&\
                  userip={2}'
    login_data = login_data.format(username, password, ip)
    login_request = urllib2.Request(login_url, login_data, HEADERS)
    response = urllib2.urlopen(login_request).read()

    soup = BeautifulSoup(response)

    online_info = soup.find_all('input')

    language = online_info[0]['value'].decode()
    heartbeatCyc = online_info[1]['value'].decode()
    heartBeatTimeOutMaxTime = online_info[2]['value'].decode()
    userDevPort = online_info[3]['value'].decode()
    userStatus = online_info[4]['value'].decode()
    userip = ip
    serialNo = online_info[6]['value'].decode()

    online_data = 'language={0}&heartbeatCyc={1}&heartBeatTimeoutMaxTime={2}\
                   &userDevPort={3}&userStatus={4}&userip={5}&serialNo={6}'
    online_data = online_data.format(language, heartbeatCyc,
                                     heartBeatTimeOutMaxTime, userDevPort,
                                     userStatus, userip, serialNo)
    online_url = ROOT_URL + ONLINE_PAGE
    online_request = urllib2.Request(online_url, online_data, HEADERS)
    response = urllib2.urlopen(online_request).read()
    return response

if __name__ == '__main__':
    ip = get_ip()
    INDEX_URL = ROOT_URL + INDEX_PAGE
    jsessionid = get_jsessionid(INDEX_URL)
    add_cookie_in_headers(username, jsessionid)
    resp = login(username, password, jsessionid, ip)
    print resp
