#!/usr/bin/env python
#-*- coding:utf-8 -*-

import threading
from Queue import Queue
import urllib2
from lxml import etree
import sys
import time
from pymongo import MongoClient

"""
百度贴吧爬虫脚本, 主要是爬主题贴的作者
刚看了python threading写了练手的~
"""

reload(sys)
sys.setdefaultencoding('utf-8')

connection = MongoClient()
db = connection.tieba
users = db.users

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
        time.sleep(1)
        fails = 0
        while True:
            if self.queue.empty():
                break
            try:
                if fails > 50:
                    break
                url = self.queue.get()
                print url, 'start'
                html = urllib2.urlopen(url, timeout=10).read()
            except Exception:
                fails = fails + 1
                print '网络链接错误, 重新链接中...', fails
            print 'read done'
            authors = getAuthor(html)
            for author in authors:
                t = users.find_one({'name': author})
                if t:
                    user_id = t['_id']
                    user_time = t['time']
                    users.update(
                        {"_id": user_id}, {"$set": {'time': user_time+1}}
                    )
                else:
                    users.insert({'name': author, 'time': 1})
                print author
            self.queue.task_done()


def main():
    for i in range(10):
        t = threadUrl(queue)
        t.setDaemon(True)
        t.start()

    for i in xrange(0, 227651, 50):
        url = BASE_URL + str(i)
        queue.put(url)

    queue.join()


if __name__ == "__main__":
    main()
