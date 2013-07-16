#-*- coding:utf-8 -*-

USER_EMAIL = "***@****"
USER_PASSWD = "******"

import urllib
import requests
from Queue import Queue
from pymongo import MongoClient
import re
import threading

connection = MongoClient()
db = connection.fm
tags = db.tags
queue = Queue()


def get_songs():
    captcha_url = "http://douban.fm/j/new_captcha"
    captcha_r = requests.get(captcha_url)
    captcha_id = captcha_r.content.strip('"')
    print captcha_id
    urllib.urlretrieve("http://douban.fm/misc/captcha?size=m&id="+captcha_id, '/home/lastmayday/clawer/captcha.jpg')
    captcha = raw_input("Please input the captcha:\n")
    login_url = "http://douban.fm/j/login"
    data = {
        "source": "radio",
        "alias": USER_EMAIL,
        "form_password": USER_PASSWD,
        "captcha_solution": captcha,
        "captcha_id": captcha_id,
    }
    login_s = requests.Session()
    login_r = login_s.post(login_url, data=data)
    like_url = "http://douban.fm/mine?type=liked#!type=liked"
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Encoding": "gzip,deflate,sdch",
        "Accept-Language": "zh-CN,zh;q=0.8",
        "Connection": "keep-alive",
        "User-Agent": "Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.71 Safari/537.36"
    }
    like_r = login_s.get(like_url)
    try:
        ck = (like_r.cookies["ck"]).strip('"')
    except Exception:
        print "登录错误"
        return False
    headers = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip,deflate,sdch",
        "Accept-Language": "zh-CN,zh;q=0.8",
        "Connection": "keep-alive",
        "Host": "douban.fm",
        "Referer": "http://douban.fm/mine",
        "User-Agent": "Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.71 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest"
    }
    start = 0
    songs = []
    while True:
        songs_url = "http://douban.fm/j/play_record?ck=" + ck + "&type=liked&start=" + str(start)
        songs_r = login_s.get(songs_url, headers=headers)
        songs_temp = songs_r.json()['songs']
        if len(songs_temp) == 0:
            break
        songs += songs_temp
        start += 15
    songs_url = []
    for song in songs:
        songs_url.append(song['path'])
    print "get songs done."
    return songs_url


def get_tags(url):
    tag_re = re.compile(r'<a href="http://music.douban.com/tag/(.+?)">(.*?)</a>\((\d+)\)')
    tag_r = requests.get(url)
    tag_content = tag_r.content
    res = tag_re.findall(tag_content)
    res_tags = []
    for t in res:
        res_tags.append((t[1],t[2]))
    return res_tags


class threadUrl(threading.Thread):
    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue

    def run(self):
        while True:
            url = self.queue.get()
            print url, 'start'
            res_tags = get_tags(url)
            amount = 0.0
            for t in res_tags:
                amount += int(t[1])
            for t in res_tags:
                tag = t[0].lower()
                tmp = tags.find_one({'tag': tag})
                per = int(t[1])/amount
                if tmp:
                    tag_id = tmp['_id']
                    per_ori = tmp['per']
                    tags.update({"_id": tag_id},
                                {"$set": {'per': per_ori+per}})
                else:
                    tags.insert({'tag': tag, 'per': per})
                print tag
            self.queue.task_done()


def main():
    for i in range(10):
        t = threadUrl(queue)
        t.setDaemon(True)
        t.start()

    songs_url = get_songs()

    if songs_url != False:
        for url in get_songs():
            queue.put(url)

    queue.join()


if __name__ == '__main__':
    main()
