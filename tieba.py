#!/usr/bin/env python
#-*- coding:utf-8 -*-

import threading
from Queue import Queue
import urllib2
from lxml import etree
import sys
import MySQLdb
import time

"""
百度贴吧爬虫脚本, 主要是爬主题贴的作者
刚看了python threading写了练手的~
"""

reload(sys)
sys.setdefaultencoding('utf-8')

con = MySQLdb.connect(host='localhost', user='lastmayday',
                      passwd='411531', charset="utf8")
con.ping(True)

BASE_URL = "http://tieba.baidu.com/f?kw=%BB%AA%D6%D0%BF%C6%BC%BC%B4%F3%D1%A7&tp=0&pn="
queue = Queue()

def getAuthor(html):
    content = etree.HTML(html.decode('GB18030', 'ignore'))
    authors = []
    results = content.xpath('//span[@class="tb_icon_author "]/a')
    for result in results:
        authors.append(result.text.encode('utf-8'))
    return authors


class threadUrl(threading.Thread):
    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue

    def run(self):
        cur = con.cursor()
        con.select_db('tieba')
        fails = 0
        while True:
            if self.queue.empty():
                break
            try:
                if fails > 50:
                    break
                url = self.queue.get()
                # proxy_support = urllib2.ProxyHandler({'http': 'http://110.4.12.170:80'})
                # opener = urllib2.build_opener(proxy_support, urllib2.HTTPHandler)
                # urllib2.install_opener(opener)
                print url, 'start'
                html = urllib2.urlopen(url, timeout=10).read()
            except Exception:
                fails = fails + 1
                print '网络链接错误, 重新链接中...', fails
            print 'read done'
            authors = getAuthor(html)
            for author in authors:
                try:
                    count = cur.execute("SELECT * from user WHERE name=%s", (author))
                except Exception:
                    count = 0 
                if count:
                    user_id = cur.fetchone()[0]
                    cur.execute('UPDATE user SET time=time+1 WHERE id=%s', (user_id))
                    con.commit()
                else:
                    sql = "INSERT INTO user(name) VALUES('%s')" % (author)
                    cur.execute(sql)
                    con.commit()
                print author
            self.queue.task_done()
            time.sleep(2)
        cur.close()


def main():
    for i in range(10):
        t = threadUrl(queue)
        t.setDaemon(True)
        t.start()

    for i in xrange(0, 227351, 50):
        url = BASE_URL + str(i)
        queue.put(url)

    queue.join()
    con.close()


if __name__ == "__main__":
    main()
