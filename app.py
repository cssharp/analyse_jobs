#!/usr/bin/env
# coding:utf-8
import requests
import re
import threading
import Queue
import logging
import json
from pyquery import PyQuery as pq
from jieba import analyse
import sys
import Config
reload(sys)
sys.setdefaultencoding('utf-8')

'''
1）根据
职位，月薪
筛选top100
得到列表

2）根据列表
采集招聘启事



'''


class JobCrawlerUtils(object):

    @staticmethod
    def isInBalckList(blacklist, toSearch):
        for item in blacklist:
            if item in toSearch:
                return True
        return False


class Publisher(object):

    """docstring for Publisher"""

    def __init__(self, config, queue):
        super(Publisher, self).__init__()
        self.config = config
        self.queue = queue

    def run(self):
        url_format = 'http://www.lagou.com/jobs/positionAjax.json?px=default&yx={0}'
        key_list = self.config.key_search_word_list
        url = url_format.format(self.config.yx)
        for key in key_list:
            logging.warning(u'%s', key)
            print u'正在采集列表---->{0}\t{1}'.format(key, self.config.yx)
            para = dict(first='false', pn=1, kd=key)
            self.load_job_list(url, para)

    def load_job_list(self, url, para):
        try:
            r = requests.post(url, data=para)
            html = r.content
            j = json.loads(html)
            result_list = j['content']['result']
            blacklist = list(self.config.custom_black_list)
            for result in result_list:
                toSearch = result['positionName']
                if JobCrawlerUtils.isInBalckList(blacklist, toSearch):
                    print u'过滤掉。{0}'.format(toSearch)
                    continue
                logging.debug(result['positionId'])
                self.queue.put(result['positionId'])
        except Exception, e:
            logging.error(u'err, %s', e)


class Worker(object):

    """docstring for Worker"""

    def __init__(self, config, queue):
        super(Worker, self).__init__()
        self.config = config
        self.queue = queue

    def run(self):
        while not self.queue.empty():
            positionId = self.queue.get()
            url = 'http://www.lagou.com/jobs/{0}.html?source=search&i=search-1'.format(
                positionId)
            print u'正在采集---->{0}'.format(url)
            self.get_content(url)

    def get_content(self, url):
        try:
            r = requests.get(url)
            html = r.content
            html = html.decode(r.encoding)
            v = pq(html)
            job_bt = v('.job_bt').text()
            with(open(self.config.file, 'a')) as f:
                f.write(job_bt)
        except Exception, e:
            logging.error(u'err, %s,%s', url, e)


class JobCrawler(object):

    def __init__(self):
        self.config = Config.Config('config.ini')

    def run(self):
        queue = Queue.Queue()
        p = Publisher(self.config, queue)
        p.run()
        w = Worker(self.config, queue)
        w.run()

    def analyse(self):
        print u'开始分析职位需求---->'
        strx = open(self.config.file, 'r').read()
        strx = strx.upper()
        tags = analyse.extract_tags(strx, topK=50,withWeight=False)

        #export to html file
        with(open(self.config.result_file, 'w')) as f:
            f.writelines('<html><head>')
            f.writelines('<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>')
            f.writelines('<title>Job Crawer Result</title></head><body>')
            f.writelines('<table rules=all>')
            f.writelines('<h1>' + prog_info + '</h1>')
            f.writelines('<ul>')
            for tag in tags:
                f.writelines('<li>{0}</li>'.format(tag.capitalize()))
            f.writelines('</ul>')
            f.writelines('</body></html>')

if __name__ == '__main__':
    prog_info = "Job Crawler 1.0 [Base On Lagou]\nBy cs_sharp\nhttp://lagou.com\n"
    logging.warning(prog_info)

    job = JobCrawler()
    job.run()
    job.analyse()
