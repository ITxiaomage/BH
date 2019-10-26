from bs4 import BeautifulSoup,Comment
import lxml
import datetime
import time
import jieba
import jieba.analyse
import re
import json
import time
import requests
import pymysql
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui  import WebDriverWait

from .define import *
img_list =[]
#################################科协一家提供的新闻资讯和专家观点#####################################
#新闻资讯
def get_kxyj_news(url = r'http://ypt.cnki.net/znapp/ScienceAPI/GetKXHotList?keyWord=&pageIndex=1&pageSize=10',
                  base_url =r'http://ypt.cnki.net/znapp/api/NYAnswerAPI/GetXMLContent?filename='):
    r = requests.get(url = url).text
    r_dict = json.loads(r)
    result_list = []
    news_data = r_dict['resultModel']['data']
    for one_news in news_data:
        temp_dict = {}
        temp_dict['title'] = one_news['title']
        temp_dict['author'] = one_news['author']
        temp_dict['time'] = one_news['publishDate']
        temp_dict['source'] = one_news['chkm']
        temp_dict['title'] = one_news['title']
        content = requests.get(url = base_url + one_news['fileName']).text
        temp_dict['content'] = content
        temp_dict['keywords'] = TF_IDF(content)
        result_list.append(temp_dict)
    return result_list
#专家观点
def get_kxyj_exp_opi(url = r'http://ypt.cnki.net/znapp/ScienceAPI/GetNewsList?keyWord=&pageIndex=1&pageSize=50', base_url = r'http://ypt.cnki.net/znapp/ScienceAPI/GetNewsDetail?id='):
    r = requests.get(url = url).text
    r_dict = json.loads(r)
    news_data = r_dict['resultModel']['data']
    result_list =[]
    for one_news in news_data:
        temp_dict = {}
        temp_dict['title'] = one_news['title']
        temp_dict['img'] = one_news['coverImage']
        temp_dict['time'] = one_news['publishDate'].split(' ')[0].replace('/','-')
        temp_dict['source'] = one_news['resource']
        response = json.loads(requests.get(url = base_url + str(one_news['id'])).text)
        temp_dict['url'] = response['resultModel']['data']['spiderUrl']
        temp_dict['content'] = response['resultModel']['data']['content']
        temp_dict['keywords'] = TF_IDF(response['resultModel']['data']['content'])
        result_list.append(temp_dict)
    return result_list

#################################人民网时政新闻爬虫##################################################
def get_rmw_news_data(url=r'http://www.people.com.cn/rss/rect_default.json',base_url = r'http://politics.people.com.cn'):
    data_json= requests.get(url=url).text
    data_dict = json.loads(data_json)
    news_list=data_dict['otherNews']
    result_list = []
    for one_news in news_list:
        try:
            result_list.append(get_rmw_data_dict(
                news_url=one_news['newsLink'],
                news_content=None,
                news_title=one_news['title'],
                news_img=None,
                news_time=None,
                news_source=None,
                base_url=base_url))
        except Exception as err:
            print('爬取人民网时政新闻出错{0}'.format(one_news))
            print(err)
    return result_list

# def get_rmw_content_time_img(news_url,base_url):
#     print(news_url)
#     soup = rm_spider_head(news_url)
#     try:
#         news_content = soup.select('#rwb_zw')[0]
#         news_time_source = soup.select('.box01 > div')[0].text
#         news_time = news_time_source.split(' ')[0]
#         year,month,day = news_time[:4],news_time[5:7],news_time[8:10]
#         news_time =  year+'-'+ month+'-'+ day
#         news_source = news_time_source.split(' ')[-1].split('：')[-1]
#         if news_source == '闻':
#             news_source = '人民网-时政'
#         imgs = news_content.findAll('img')
#         img = deal_imgs_and_a(base_url, content=news_content, imgs=imgs)
#     except:
#         try:
#             news_content = soup.select('#picG')[0]
#             news_time_source = soup.select('.page_c')[1].text
#             news_source = news_time_source.split(' ')[0].split('：')[-1]
#             news_time = news_time_source.split(' ')[-1]
#             year,month,day = news_time[:4],news_time[5:7],news_time[8:10]
#             news_time =  year+'-'+ month+'-'+ day
#             img = ''
#         except:
#             news_content = ''
#             news_time =''
#             news_source=''
#             img =''
#     return news_content ,news_time,img,news_source

def rm_spider_head(url):
    headers = {"User_Agent": "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; en) Presto/2.8.131 Version/11.11"}
    try:
        response = requests.get(url=url, headers=headers)
        response.encoding=response.apparent_encoding
        soup = BeautifulSoup(response.text, 'lxml')
    except Exception as err:
        print('rm_spider_head出错')
        soup = None
    return soup
##################################人民网科技数据爬虫##############################################
def get_rmw_kj_data(url=r'http://scitech.people.com.cn/',base_url = r'http://scitech.people.com.cn'):
    result_list = []
    soup = rm_spider_head(url = url)
    #最大的新闻
    max_news_soup = soup.findAll(class_="title mt15")[0]
    max_news_title = max_news_soup.select('h1 > a')[0].text
    max_news_url = max_news_soup.select('h1 > a')[0]['href']

    if max_news_url.startswith('/'):
        new_max_news_url = base_url + max_news_url
    else:
        new_max_news_url = max_news_url
    result_list.append(get_rmw_data_dict(
        news_url=new_max_news_url,
        news_content = None ,
        news_title = max_news_title,
        news_img =None,
        news_time=None,
        news_source=None,
        base_url=base_url))
    #轮播图爬取
    lb_news_soup = soup.findAll(id='focus_list')[0].select('ul > li')
    for one_lb in lb_news_soup:
        lb_news_tilte = one_lb.text
        lb_news_url = one_lb.select('li > a')[0]['href']
        lb_news_img = one_lb.select('li > a > img')[0]['src']
        if lb_news_img.startswith('/'):
            new_lb_news_img = base_url + lb_news_img
        else:
            new_lb_news_img= lb_news_img
        result_list.append(get_rmw_data_dict(
        news_url=lb_news_url,
        news_content = None ,
        news_title = lb_news_tilte,
        news_img =new_lb_news_img,
        news_time=None,
        news_source=None,
        base_url=base_url))
    #独家专稿 + 高端访谈 + 热点排行
    djzg_news_soup = soup.findAll(class_='w1000 mt20 column_2 p9_con')[0].findAll(class_='right w310')[0].select('li')
    for one_news in djzg_news_soup:
        one_news_url = one_news.select('a')[0]['href']
        if one_news_url.startswith('/'):
            new_one_news_url = base_url + one_news_url
        else:
            new_one_news_url= one_news_url
        result_list.append(get_rmw_data_dict(
        news_url=new_one_news_url,
        news_content = None ,
        news_title = None,
        news_img =None,
        news_time=None,
        news_source=None,
        base_url=base_url))
    return result_list

def get_rmw_data_dict(news_url=None,news_content=None ,news_title=None,news_img=None,news_time=None,news_source=None,base_url=None):
    soup = rm_spider_head(news_url)
    try:
        #标题失败
        try:
            news_title = soup.findAll(class_='clearfix w1000_320 text_title')[0].select('h1')[0].text
        except:
            news_title = news_title
        #内容
        try:
            news_content = soup.select('#rwb_zw')[0]
        except:
            news_content = news_content
        #时间
        news_time_source = soup.select('.box01 > div')[0].text
        try:
            news_time = news_time_source.split(' ')[0]
            year, month, day = news_time[:4], news_time[5:7], news_time[8:10]
            news_time = year + '-' + month + '-' + day
        except:
            news_time = datetime.datetime.now().strftime("%Y-%m-%d")
        #新闻来源
        try:
            news_source = news_time_source.split(' ')[-1].split('：')[-1]
        except:
            news_source = '人民网'
        #处理图像
        try:
            imgs = news_content.findAll('img')
            news_img = deal_imgs_and_a(base_url, content=news_content, imgs=imgs)
        except:
            news_img = ' '
    except Exception as err:
        print('爬取新闻{0}出错'.format(news_url))
        pass
    #del content['style']
    #处理完content中图片的style
    if news_content:
        tables = news_content.findAll('table')
        if tables:
            for table in tables:
                del table['width']

    return package_data_dict(title=news_title, url=news_url, img=news_img, content=str(news_content), date=news_time, source=news_source, label=None)
##################################科协官网用selenium爬取##############################################
def update_kexie_news():
    result_list =[]
    try:
        browser = init_chrome()
        #新闻
        tt_url = r'http://www.cast.org.cn/col/col79/index.html'
        yw_url = r'http://www.cast.org.cn/col/col80/index.html'
        tzgc_url = r'http://www.cast.org.cn/col/col457/index.html'
        #视频
        xhfc_url = r'http://www.cast.org.cn/col/col106/index.html'
        cmkx_url = r'http://www.cast.org.cn/col/col107/index.html'
        base_url = r'http://www.cast.org.cn'
        try:
            #头条
            result_list.extend(get_kx_data(browser, tt_url, base_url,KXTT))
        except Exception as err:
            print('头条新闻出错')
            print(err)
        try:
            #要闻
            result_list.extend(get_kx_data(browser, yw_url, base_url,KXYW))
        except Exception as err:
            print('要闻出错')
            print(err)
        try:
            #通知
            result_list.extend(get_kx_data(browser, tzgc_url, base_url,KXTZ))
        except Exception as err:
            print('通知出错')
            print(err)
            pass

        try:
            result_list.extend(get_kx_video_data(browser, xhfc_url, base_url, KXSP))
        except Exception as err:
            print('协会风采出错')
            print(err)
        try:
            result_list.extend(get_kx_video_data(browser, cmkx_url, base_url, KXSP))
        except Exception as err:
            print('传媒风采')
            print(err)
    except Exception as err:
        print('爬取科协新闻出错')
        print(err)
    finally:
        browser.quit()
        return result_list

#初始化浏览器
def init_chrome():
    #创建对象
    option = webdriver.ChromeOptions()
    option.add_argument('--no-sandbox')
    #headless就是谷歌的无头模式
    option.add_argument('--headless')
    #这里是禁用了GPU，谷歌浏览器GPU加速在虚拟机上可能导致黑屏
    option.add_argument('--disable-gpu')
    #传入最终的参数就行了
    browser = webdriver.Chrome(options = option )
    return browser

#爬取科协视频
def get_video_content(browser,url,xpath):
    browser.execute_script('window.open()')
    browser.switch_to_window(browser.window_handles[1])
    browser.get(url)
    time.sleep(2)
    try:
        content = browser.find_element_by_xpath(xpath).get_attribute('src')
    except:
        print('获取内容错误。。。或者无内容')
        content = ''
    try:
        video_time = browser.find_element_by_xpath('//div[@class="center"]//div[@class=" time"]//span').text
        video_time = video_time.strip().split('：')[-1]
    except Exception as err :
        print(err)
        video_time = str(datetime.datetime.now().strftime('%Y-%m-%d'))
    browser.execute_script('window.close()')
    browser.switch_to_window(browser.window_handles[0])
    content = r"<video controls autoplay loop  src ='{0}'></video>".format(content)
    return content,video_time
#科协视频
def get_kx_video_data(browser, url,base_url,label):
    print('进入官网。。。')
    try:
        # 进入科协官网新闻
        browser.get(url)
        time.sleep(1)
        # 获取列表
        info_list = browser.find_elements_by_xpath('//div[@id="286"]//li')
        info_list_len = len(info_list) + 1
    except:
        info_list_len =0
        print('进入科协官网出错。。。')

    # 存放结果的列表
    temp_list = []
    if info_list_len :
        for i in range(1, info_list_len):
            news_url =  browser.find_element_by_xpath('//div[@id="286"]//li[{0}]/a'.format(i)).get_attribute('href')
            title = browser.find_element_by_xpath('//div[@id="286"]//li[{0}]//span'.format(i)).text
            img = browser.find_elements_by_xpath('//div[@id="286"]//li[{0}]/a//img'.format(i))[0].get_attribute('src')
            xpath = r'//video'
            content,video_time = get_video_content(browser,news_url,xpath)
            # 获取新闻文本
            try:
                del content['width']
            except:
                pass
            try:
                del content['height']
            except:
                pass
            print(title)
            temp_list.append(package_data_dict(title=title, url=news_url, img=img, content=str(content), date=video_time,source="中国科协", label=label))
    return temp_list
#科协数据
def get_kx_data(browser, url,base_url,label):
    print('进入{0}'.format(label))
    try:
        # 进入科协官网新闻
        browser.get(url)
        time.sleep(1)
        # 获取列表
        info_list = browser.find_elements_by_xpath('//div[@class="bt-mod-wzpb-02"]/ul/li')
        info_list_len = len(info_list) + 1
        print(info_list_len)
    except:
        info_list_len =0
        print('进入科协官网出错。。。')

    # 存放结果的列表
    temp_list = []
    if info_list_len :
        for i in range(1, info_list_len):
            news_url = browser.find_element_by_xpath('//div[@class="bt-mod-wzpb-02"]/ul/li[{0}]//p/a'.format(i)).get_attribute('href')
            title = browser.find_element_by_xpath('//div[@class="bt-mod-wzpb-02"]/ul/li[{0}]//p'.format(i)).text
            day = browser.find_element_by_xpath('//div[@class="bt-mod-wzpb-02"]/ul/li[{0}]//h2'.format(i)).text
            year_month = browser.find_element_by_xpath('//div[@class="bt-mod-wzpb-02"]/ul/li[{0}]//h5'.format(i)).text
            news_time = year_month.split('/')[0] + '-' + year_month.split('/')[1] + '-' + day
            headers = {"User-Agent": "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50"}
            # 获取新闻文本
            r = requests.get(url=news_url, headers=headers)
            r.encoding =  r.apparent_encoding
            soup = BeautifulSoup(r.text, 'lxml')
            content = soup.select('#zoom')[0]
            try:
                del content['style']
            except  Exception as err:
                print('取出科协官网style错误')
                print(err)
            imgs = content.findAll('img')
            img_path = deal_imgs_and_a(base_url, content=content, imgs=imgs)
            content = str(content).replace("style",' ')
            temp_list.append(package_data_dict(title=title, url=news_url, img =img_path,content=str(content), date=news_time, source="中国科协",label = label))
            print(title)
    return temp_list

#########################3###########科协官网用bs4爬取#############################################################

def get_kexie_news_data_list():
    result_list = []
    tt_url = r'http://www.cast.org.cn/col/col79/index.html'
    yw_url = r'http://www.cast.org.cn/col/col80/index.html'
    tzgc_url = r'http://www.cast.org.cn/col/col457/index.html'
    base_url = r'http://www.cast.org.cn'
    result_list.extend(get_kx_news_list(tt_url, base_url,KXTT))
    result_list.extend(get_kx_news_list(yw_url, base_url,KXYW))
    result_list.extend(get_kx_news_list(tzgc_url, base_url,KXTZ))
    return result_list

def spider_head(url):
    headers = {"User_Agent": "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; en) Presto/2.8.131 Version/11.11"}
    try:
        response = requests.get(url=url, headers=headers)
        html = response.text.encode(response.encoding).decode()
        soup = BeautifulSoup(html, 'lxml')
    except Exception as err:
        print('spider_head出错')
        soup = None
    return soup


def get_content_time_img(news_url, base_url):
    soup = spider_head(news_url)
    content = ''
    news_time = ''
    img_path = ''
    try:
        content = soup.select('#zoom')[0]
    except:
        pass
    if content:
        del content['style']
        try:
            news_time = soup.select('.time > span')[0]
            news_time.select('style')[0].extract()
            news_time = news_time.text.split('：')[1]
        except:
            news_time = str(datetime.datetime.now().strftime('%Y-%m-%d'))

        imgs = content.findAll('img')
        img_path = None
        if imgs:
            for img in imgs:
                img_path = img['src']
                if img_path[0] == '/':
                    img_path = base_url + img_path
                    img['src'] = img_path
        try:
            a_hrefs = content.findAll('a')
        except Exception as err:
            print('文章中没有a链接')
            a_hrefs = None
        if a_hrefs:
            for a_href in a_hrefs:
                try:
                    old_href = a_href['href']
                except Exception as err:
                    print('a标签没有href属性')
                    print(err)
                    continue
                if old_href[0] == '/':
                    new_href = base_url + old_href
                    a_href['href'] = new_href
    return news_time, img_path, content

def get_kx_news_list(url, base_url,label):
    result_list = []
    soup = spider_head(url=url)
    regx = re.compile(r'\<\!\[CDATA\[(.*?)\]\]\>', re.DOTALL)
    re_result = re.findall(regx, soup.text.strip())
    replace_list = [e.strip().replace('\t', '') for e in re_result]
    repalce_list_len = len(replace_list)
    for i in range(1, repalce_list_len):
        one_news_soup = BeautifulSoup(replace_list[i], 'lxml')
        news_url = base_url + one_news_soup.select('.list-title-bif > a')[0]['href']
        title = one_news_soup.select('.list-title > p')[0].text
        news_time, news_img, news_content = get_content_time_img(news_url, base_url)
        result_list.append(package_data_dict(title=title, url=news_url, img =news_img,content=news_content, date=news_time, source='中国科协',label =label))
    return result_list

#处理图片链接和文件链接
def deal_imgs_and_a(base_url,content =None,imgs=None):
    img_path = ''
    if imgs:
        for img in imgs:
            img_path = img['src']
            if img_path[0] == '/':
                img_path = base_url + img_path
                img['src'] = img_path
        img_path =imgs[0]['src']
    try:
        a_hrefs = content.findAll('a')
    except Exception as err:
        print('文章中没有a链接')
        a_hrefs = None
    if a_hrefs:
        for a_href in a_hrefs:
            try:
                old_href = a_href['href']
            except Exception as err:
                print('a标签没有href属性')
                print(err)
                continue
            if old_href[0] == '/':
                new_href = base_url + old_href
                a_href['href'] = new_href
    if img_path.startswith('data'):
        img_path = None
    return img_path

#########################3###########爬取每天的置顶时政新闻，来自与中国网#############################################################
def china_top_news():
    result_dict = {}
    url = r'http://www.china.com.cn/'
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50"}
    try:
        r = requests.get(url=url, headers=headers)
        html = r.text.encode(r.encoding).decode()
        soup = BeautifulSoup(html, 'lxml')
    except:
        return result_dict

    try:
        news = soup.select('.topNews > div > h1 > a')[0]
        news_title = news.text
        news_url = news['href']
        news_time = time.strftime('%Y-%m-%d')
    except Exception as err:
        print(err)

    try:
        r = requests.get(url=news_url, headers=headers)
        html = r.text.encode(r.encoding).decode()
        soup = BeautifulSoup(html, 'lxml')
        try:
            content = soup.select('.main')[0]
        except Exception as err:
            print('第一次失败')
            print(err)
            try:
                content = soup.select('.articleBody')[0]
            except Exception as err:
                print('第二次获取失败')
                print(err)
                try:
                    content = soup.select('.artiContent')[0]
                    img_list.append(IMG)
                except Exception as err:
                    print('第三次获取失败')
                    print(err)

        try:
            # 去除文章中的注释
            comments = soup.findAll(text=lambda text: isinstance(text, Comment))
            for comment in comments:
                comment.extract()
            try:
                # 把新闻的开始的视频处理了
                content.select("#videoarea")[0].extract()
            except:
                pass
            try:
                # 防止最后出现的app
                content.select(".app")[0].extract()
            except:
                pass

            try:
                content.select("embed")[0].extract()
            except:
                pass
        except Exception as err:
            print(err)
    except Exception as err:
        print(err)

        # 图片
    imgs = content.findAll("img")
    if not img_list:
        for one in imgs:
            img = one.attrs['src']
            if img.split('/')[-1] == '161021-02.jpg' or img.split('/')[-1] == '161021-03.jpg' or img.split('/')[
                -1] == 'logo.gif':
                continue
            else:
                img_list.append(img)
        if not img_list:
            img_list.append(IMG)

    # 把文章中记者的信息处理了
    content = re.sub(r"[（](.*?)[）]", '', str(content))

    result_dict['title'] = news_title
    result_dict['url'] = news_url
    # 获取到一张图片
    result_dict['img'] = img_list[0]
    result_dict['content'] = content
    result_dict['time'] = news_time
    result_dict['source'] = '中国网新闻中心'

    return result_dict
####################################新闻TF_IDF的提取#############################################################
#前n个用户关键字列表，关键字列表给用给用户画像
def TF_IDF(content,n = MAX_KEYWORDS):
    con = ' ' .join(re.findall('\w+', content))
    temp_list = jieba.analyse.extract_tags(con,topK = 10,withWeight = False,allowPOS=('n','ns','nr','nt','nz','v','vn'))
    if len(temp_list) > n:
        result =temp_list[:n]
    else:
        result = temp_list
    return result
####################################将新闻相关信息打包为一个字典#############################################################
def package_data_dict(title=None, url=None, img =None,content=None, date=None, source=None,label =None):
    temp_dict = {}
    if label == KXSP:#视频就是以标题作为关键字
        keywords = TF_IDF(title, MAX_KEYWORDS)
    else:
        keywords = TF_IDF(content,MAX_KEYWORDS)
    temp_dict['title'] = title
    temp_dict['url'] = url
    temp_dict['content'] = str(content)
    temp_dict['img'] = img
    temp_dict['time'] = date
    temp_dict['author'] = ''
    temp_dict['label'] = label
    temp_dict['keywords'] = ' '.join(keywords)
    temp_dict['source'] = source
    return temp_dict

