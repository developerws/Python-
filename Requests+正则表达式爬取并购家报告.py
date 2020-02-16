import urllib.parse
import requests
import re
import gui as g
import zipfile
import threading
from queue import Queue
import time
import sys

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36'
}

class Solution():
    search_keyword = ""
    number = 0
    index = 1
    count = 0
    Cookie = ""
    directory = ""

    def __init__(self, keyword, num):
        self.search_keyword = keyword
        self.number = num
        self.Cookie = self.get_cookie()
        self.directory = g.diropenbox()

    def get_cookie(self):
        '''
        获取主页面的cookie，用于后面构造请求头
        :return:
        '''
        res = requests.get('http://ipoipo.cn/')
        resd = requests.utils.dict_from_cookiejar(res.cookies)
        cookie = "".join([f"{key}={value};" for key, value in resd.items()])        #提取cookie里的健和值，然后用分号隔开
        return cookie

    def construct_url(self, queue):
        while 1:
            if self.count < self.number:
                url = 'http://ipoipo.cn/search.php?q=' + urllib.parse.quote(self.search_keyword) + '&page=' + str(
                    self.index)  # 下一页的地址
                self.get_every_report_url(url, queue)
                self.index += 1
            else:
                break

    def get_every_report_url(self, url, queue):
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            html = response.text
            pattern = re.compile(r'<div.*?wapost card.*?multi-ellipsis.*?href="(.*?)".*?>(.*?)</a>.*?</div>', re.S)
            items = re.findall(pattern, html)
            for item in items:
                if self.count >= self.number:
                    break
                queue.put(item)
                time.sleep(0.00001)
                self.count += 1

    # def multiThread(self, queue, html_thread):
    #     index = 0
    #     while index < 3:
    #         thread2 = threading.Thread(target=Solution.download_report, args=(self, queue,))  # 线程2、3、4负责下载提取出来的压缩包链接
    #         html_thread.append(thread2)
    #         index += 1

    def download_report(self, queue):
        while True:
            if queue.empty() == False:
                print('线程{0}正在运行'.format(threading.current_thread().getName()))
                url = (queue.get()[0]).replace('post', 'download')
                title = queue.get()[1] + '.zip'
                #url = url.replace('post', 'download')  # 省了一步访问post页面的过程，直接用download替换掉post
                response = requests.get(url, headers=headers)
                if response.status_code == 200:
                    html = response.text
                    # pattern = re.compile('http://(?:www.)?ipoipo.cn/zb_users/upload/(.*?).zip', re.S)
                    # pattern = re.compile('<p style.*?<img.*?<a style.*?href="(.*?)".*?zip', re.S)
                    pattern = re.compile('<div.*?con main.*?<p>.*?</p><p.*?<a.*?href="(.*?)".*?zip', re.S)
                    download_url = re.findall(pattern, html)[0]
                    print(download_url)
                    headers2 = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36',
                        'Referer': url,
                        'cookie': self.Cookie
                    }
                    r = requests.get(download_url, headers=headers2, stream=True)
                    print(r.status_code)
                    path = self.directory + "\\" + title
                    with open(path, 'wb') as f:
                        f.write(r.content)
                    # f = zipfile.ZipFile(path, 'r')
                    # for file in f.namelist():
                    #     f.extract(file, self.directory)
            else:
                print('队列空了！')

if __name__ == '__main__':
    url_queue = Queue(maxsize=100)  #用Queue构造一个大小为1000的线程安全的先进先出队列
    msg = "爬取内容"
    title = "并购家简易爬取界面"
    Fields = ['请输入爬取关键词：', '请输入爬取的篇数：']
    try:
        result = g.multenterbox(msg, title, Fields)
        sol = Solution(result[0], int(result[1]))
        thread = threading.Thread(target=sol.construct_url, args=(url_queue, ))             #线程1负责提取出每份报告的链接
        html_thread = []
        index = 0
        while index < 3:
            thread2 = threading.Thread(target=sol.download_report, args=(url_queue,))  # 线程2、3、4负责下载提取出来的压缩包链接
            html_thread.append(thread2)
            index += 1
        start_time = time.time()  # 开始时间
        thread.start()
        for i in range(3):
            html_thread[i].start()
        thread.join()
        for i in range(3):
            html_thread[i].join()
        print("爬取时间为：{0}s".format(time.time()-start_time))
    except:
        g.exceptionbox()


