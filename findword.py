#!/usr/bin/env python
#-*- coding:utf-8 -*-

"""
在指定目录及其子目录下的文件中查找关键词
输出含有改关键词的文件名及行数
"""

import os


def findwords(*args, **kwargs):
    """
    usage: ./findword [dir] [word]
    """
    dirs = kwargs['dir']
    words = kwargs['word']
    if dirs[:1] == '~':
	#把相对路径改为绝对路径
	username = getpass.getuser()
	dirs = '/home/%s' % username + dirs[1:]
    for path, subdirs, files in os.walk(dirs):
        for one in files:
            one = os.path.join(path, one)
            os.system('awk "/'+words+'/{print FILENAME, FNR}" '+one)


if __name__ == "__main__":
    import sys
    if len(sys.argv) == 3:
        findwords(dir=sys.argv[1], word=sys.argv[2])
    else:
        print "%s" % findwords.__doc__
        sys.exit(100)
