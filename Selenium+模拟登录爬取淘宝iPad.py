from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import  TimeoutException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from urllib.parse import quote

from pyquery import PyQuery as pq
import json
#chrome_options = Options()
#chrome_options.add_argument('--headless')
#chrome_options.add_argument('--disable-gpu')
#browser = webdriver.Chrome(chrome_options=chrome_options)
browser = webdriver.Chrome()
wait = WebDriverWait(browser, 10)

keyword = 'iPad'
url = 'https://s.taobao.com/search?q=' + quote(keyword)
def login_cookies():
    browser.get('https://login.taobao.com/member/login.jhtml?redirectURL=http%3A%2F%2Fbuyertrade.taobao.com%2Ftrade%2Fitemlist%2Flist_bought_items.htm%3Fspm%3D875.7931836%252FB.a2226mz.4.66144265Vdg7d5%26t%3D20110530')
    input('请回车登录！')
    dictCookies = browser.get_cookies()
    jsonCookies = json.dumps(dictCookies)
    with open('cookies.json','w') as fp:
        fp.write(jsonCookies)

def login():
    browser.get(url)
    browser.delete_all_cookies()
    with open('cookies.json','r', encoding="utf8") as fp:
        ListCookies = json.loads(fp.read())
    for cookie in ListCookies:
        browser.add_cookie({
            'domain': '.taobao.com',  # 此处xxx.com前，需要带点
            'name': cookie['name'],
            'value': cookie['value'],
            'path': '/',
            'expires': None
        })

def index_page(page):
    print('正在爬取第', page, '页')
    try:
        #browser.get(url)
        # with open("cookies.txt", 'r') as fp:
        #     cookies = json.load(fp)
        #     for cookie in cookies:
        #         browser.add_cookie(cookie)
        login()
        browser.get(url)
        input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > div.form > input')))
        submit = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > div.form > span.btn.J_Submit')))
        input.clear()
        input.send_keys(page)
        submit.click()
        wait.until(EC.text_to_be_present_in_element((By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > ul > li.item.active > span'),str(page)))
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#mainsrp-itemlist .items .item')))    #判断所有ipad信息是否已加载出来
        get_product()
    except TimeoutException:                #当时间超时，则继续访问
        index_page(page)

def get_product():
    html = browser.page_source
    doc = pq(html)
    items = doc('#mainsrp-itemlist .items .item').items()
    for item in items:
        product = {
            'image': item.find('.pic .img').attr('data-src'),
            'price': item.find('.price').text(),
            'deal': item.find('.deal-cnt').text(),
            'title': item.find('.title').text(),
            'shop': item.find('.shop').text(),
            'location': item.find('.location').text()
        }
        print(product)
if __name__ == '__main__':
    login_cookies()

    for index in range(1,100):
        index_page(index)