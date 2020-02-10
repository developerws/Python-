from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from pyquery import PyQuery as pq
import urllib.parse
import requests
# chrome_options = Options()
# chrome_options.add_argument('--headless')
# chrome_options.add_argument('--disable-gpu')
# browser = webdriver.Chrome(chrome_options=chrome_options)
browser = webdriver.Chrome()
wait = WebDriverWait(browser, 10)
count = 0

def search_content():
    '''
    输入搜索关键词和篇数
    :return:
    '''
    search_keyword = input('请输入搜索关键词：')
    number = int(input('请输入所要搜索的篇数：'))
    url = 'http://ipoipo.cn/'
    browser.get(url)
    search = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#search > i')))
    search.click()
    keywords = browser.find_element_by_css_selector('#header > div > div.search > form > input[type=text]')    #获取搜索框
    submit = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#header > div > div.search > form > button')))    #获取搜索按钮
    keywords.clear()
    keywords.send_keys(search_keyword)              #输入搜索关键词
    submit.click()

    next_page(search_keyword, number)

def next_page(search_keyword, number):
    '''
    当抓取篇数不够时，实现翻页功能
    :param search_keyword:
    :param number:
    :return:
    '''
    global count
    index = 1
    while 1:
        get_every_report_url(number)
        if count < number:
            index += 1
            url = 'http://ipoipo.cn/search.php?q=' + urllib.parse.quote(search_keyword) + '&page=' + str(index)      #下一页的地址
            browser.get(url)
        else:
            break


def get_every_report_url(number):
    '''
    提取当前页面所有报告的链接
    :param number:
    :return:
    '''
    global count
    html = browser.page_source
    doc = pq(html)
    items = doc('#imgbox .wapost').items()
    for item in items:
        count += 1
        product = {
            'html': item.find('.multi-ellipsis a').attr('href'),
            'title': item.find('.multi-ellipsis').text()
        }
        download_report(product)
        if count >= number:
            break

def get_cookie():
    '''
    获取主页面的cookie，用于后面构造请求头
    :return:
    '''
    res = requests.get('http://ipoipo.cn/')
    resd = requests.utils.dict_from_cookiejar(res.cookies)
    cookie = "".join([f"{key}={value};" for key, value in resd.items()])        #提取cookie里的健和值，然后用分号隔开
    print(cookie)
    return cookie

#Cookie = get_cookie()

def download_report(result):
    '''
    提取出报告压缩包的下载链接，并访问下载压缩包
    :param result:
    :return:
    '''
    url = result.get('html')
    title = result.get('title') + '.zip'
    print(title)
    #source_url = url
    url = url.replace('post', 'download')                   #省了一步访问post页面的过程，直接用download替换掉post
    browser.get(url)
    html = browser.page_source
    doc = pq(html)
    item = doc('body > div > div.con.main > p:nth-child(2)')
    download_url = item.find('a').attr('href')
    print(download_url)
    # headers = {
    #     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36',
    #     'Referer': source_url,
    #     'cookie': Cookie
    # }
    # r = requests.get(download_url, headers=headers, stream=True)
    # print(r.status_code)
    # path = title
    # with open(path, 'wb') as f:
    #     f.write(r.content)

if __name__ == '__main__':
    search_content()
    browser.quit()
