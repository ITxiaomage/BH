from requests.packages.urllib3.packages.six.moves import urllib
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
import re
from bs4 import BeautifulSoup
import datetime
import json
import requests
import numpy as np

from TuiJian.models import DFKX
from . import spider


def get_text(url):
    header = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.75 Safari/537.36"}
    try:
        r = requests.get(url=url, headers=header)
        r.encoding = r.apparent_encoding
        soup = BeautifulSoup(r.text, 'lxml')
    except Exception as err:
        soup = None
    return soup


def get_selenium_head(url):
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(options=options)
    try:
        driver.get(url)
    except Exception as err:
        driver = None
    return driver


def news_to_json(result_list, file):
    keys = [str(x) for x in np.arange(len(result_list))]
    list_json = dict(zip(keys, result_list))


def dict_list(title, url, img, content, time, label):
    temp_dict = {}
    temp_dict["title"] = title
    temp_dict["url"] = url
    temp_dict["img"] = img
    temp_dict["content"] = content
    temp_dict["time"] = time
    temp_dict["label"] = label
    return temp_dict


def complete_img_a(base_url, content):
    if not content:
        return None
    imgs = content.findAll("img")
    img_path = ''
    if imgs:
        for img in imgs:
            img_path = img["src"].strip()
            if not img_path.startswith("http"):
                img_path = base_url + img_path
            img['src'] = img_path  ####是否有set_attribute????
            # ['src'] = img_path
        img_path = imgs[0]['src']
    try:
        a_hrefs = content.findAll('a')
    except Exception as err:
        a_hrefs = None
    if a_hrefs:
        for a_href in a_hrefs:
            try:
                old_href = str(a_href["href"])
            except Exception as err:
                continue
            if old_href.startswith("http"):
                new_href = old_href
            else:
                new_href = base_url + old_href
            a_href['href'] = new_href
    if img_path.startswith('data'):
        img_path = None
    return img_path


def s_complete_img_a(base_url, content):
    if not content:
        return None
    imgs = content.find_elements_by_tag_name("img")
    img_path = ''
    if imgs:
        for img in imgs:
            img_path = img.get_attribute("src")
            if not img_path.startswith("http"):
                img_path = base_url + img_path
            img.__setattr__("src", img_path)
            content.__setattr__("arguments[0].value=img_path", img)
            # img['src'] = img_path
        img_path = imgs[0].get_attribute("src")
    try:
        a_hrefs = content.find_elements_by_tag_name('a')
    except Exception as err:
        # print('文章中没有a链接')
        a_hrefs = None
    if a_hrefs:
        for a_href in a_hrefs:
            try:
                old_href = str(a_href.get_attribute("href"))
            except Exception as err:
                # print('a标签没有href属性')
                # None
                continue
            if old_href.startswith("http"):
                new_href = old_href
            else:
                new_href = base_url + old_href
            a_href.__setattr__("href", new_href)
            # a_href['href'] = new_href
    if img_path.startswith('data'):
        img_path = None
    return img_path


########################北京科协####################################
def get_bjkx_news(label, url, base_url=r'http://www.bast.net.cn'):
    temp_list = []
    soup = get_text(url)
    try:
        gzdt_news_list = soup.find_all("div", id="72459")[0].select("ul>li")
    except Exception as err:
        #None
        gzdt_news_list = []

    for one_gzdt_news in gzdt_news_list:
        gzdt_news_title = one_gzdt_news.select("li>a")[0]["title"]
        gzdt_news_url = one_gzdt_news.select("li>a")[0]["href"]
        if gzdt_news_url.startswith("/"):
            gzdt_news_url = base_url + gzdt_news_url
        gzdt_news_time = one_gzdt_news.select("li>span")[0].text
        gzdt_news_time = datetime.datetime.strptime(gzdt_news_time, '%Y/%m/%d').date()
        gzdt_news_time = gzdt_news_time.strftime("%Y-%m-%d")
        gzdt_news_label = label
        ssoup = get_text(gzdt_news_url)
        if not ssoup:
            content = None
        gzdt_news_zoom = ssoup.find_all("div", id="zoom")[0]
        t_content = gzdt_news_zoom.select("p")
        content = ""
        for t in t_content:
            content = content + t.text
        gzdt_news_content = (content)
        gzdt_news_content = str(gzdt_news_zoom)
        if gzdt_news_zoom.select("p>img"):  # 北京科协第一种图片标签
            gzdt_news_img = gzdt_news_zoom.select("p>img")[0]["src"]
            gzdt_news_img = base_url + gzdt_news_img
        elif gzdt_news_zoom.select("p>a>img"):  # 北京科协第二种图片标签
            gzdt_news_img = gzdt_news_zoom.select("p>a>img")[0]["src"]
            gzdt_news_img = base_url + gzdt_news_img
        elif gzdt_news_zoom.select("p>span>img"):  # 北京科协第三种图片标签
            gzdt_news_img = gzdt_news_zoom.select("p>span>img")[0]["src"]
            gzdt_news_img = base_url + gzdt_news_img
        else:
            gzdt_news_img = None

        temp_list.append(
            spider.package_data_dict(
                title=gzdt_news_title, url=gzdt_news_url, img=gzdt_news_img,
                content=gzdt_news_content, date=gzdt_news_time,
                source='北京市科学技术协会', label=gzdt_news_label, tag=1))

    return temp_list


def get_bjkx():
    result_list = []
    try:
        result_list.extend(get_bjkx_news(1, r'http://www.bast.net.cn/col/col16643/index.html'))  # 1
        result_list.extend(get_bjkx_news(1, r'http://www.bast.net.cn/col/col16644/index.html'))  # 1
        result_list.extend(get_bjkx_news(1, r'http://www.bast.net.cn/col/col16645/index.html'))  # 1
        result_list.extend(get_bjkx_news(3, r'http://www.bast.net.cn/col/col18127/index.html'))  # 3
        result_list.extend(get_bjkx_news(2, r'http://www.bast.net.cn/col/col16647/index.html'))  # 2
        result_list.extend(get_bjkx_news(2, r'http://www.bast.net.cn/col/col16648/index.html'))  # 2
    except Exception as err:
        None
    finally:
        return result_list
    ############list类型的temp_dict转换为json#############
    # keys = [str(x) for x in np.arange(len(result_list))]
    # list_json = dict(zip(keys, result_list))



###########################安徽科协###########################
def get_ankx_news(label, url, base_url=r'http://www.ahpst.net.cn/'):
    temp_list = []
    soup = get_text(url)
    if not soup:
        return temp_list

    try:
        news_list = soup.find_all("div", class_="pub_rig")[0].select("ul>li")
    except :
        news_list = []
    for one_news in news_list:
        news_title = one_news.select("li>a")[0]["title"]
        news_url = one_news.select("li>a")[0]["href"]
        news_url = base_url +'ahpst/web/'+ news_url
        news_time = one_news.select("li>i")[0].text
        news_time = datetime.datetime.strptime(news_time, '[%Y-%m-%d]').date()
        news_time = news_time.strftime("%Y-%m-%d")
        news_label = label
        ssoup = get_text(news_url)
        if ssoup:
            news_zoom = ssoup.find_all("div", class_="article")[0]

        else:
            news_zoom = None
        #处理掉下标
        try:
            news_zoom.select(".down_bottom")[0].extract()
        except:
            pass
        news_img = complete_img_a(base_url, news_zoom)

        news_content = str(news_zoom)
        #dict = dict_list(news_title, news_url, news_img, news_content, news_time, news_label)
        temp_list.append(
            spider.package_data_dict(
                title=news_title, url=news_url, img=news_img,
                content=news_content, date=news_time,
                source='安徽省科学技术协会', label=news_label, tag=1))
        #temp_list.append(dict)
    return temp_list


def get_ahkx():
    result_list = []
    try:
        result_list.extend(get_ankx_news(1,
                                         r"http://www.ahpst.net.cn/ahpst/web/list.jsp?strColId=1435548396259002"))
        result_list.extend(get_ankx_news(1,
                                         r"http://www.ahpst.net.cn/ahpst/web/list.jsp?strColId=1435548451157004"))
        result_list.extend(get_ankx_news(3,
                                         r"http://www.ahpst.net.cn/ahpst/web/list.jsp?strColId=1435548481679005"))
        result_list.extend(get_ankx_news(2,
                                         r"http://www.ahpst.net.cn/ahpst/web/list.jsp?strColId=1435548532739006"))
    except Exception as err:
        pass
    finally:
        #news_to_json(result_list, "ahkx.json")
        return result_list


###########################福建科协###########################
def get_fjkx_news(label, url, base_url=r'http://www.fjkx.org/'):
    temp_list = []
    soup = get_text(url)
    if not soup:
        return temp_list
    try:
        news_list = soup.find_all("div", class_="dj_list")[0].select("ul>li")
    except Exception as err:
        news_list = []

    for one_news in news_list:
        news_title = one_news.select("li>a")[0]["title"]
        news_url = one_news.select("li>a")[0]["href"]
        news_url = base_url + news_url
        news_time = str(one_news.select("li>span")[0].text)
        news_time = news_time.replace("\r", "").replace("\n", "").replace(" ", "")
        news_label = label
        ssoup = get_text(news_url)
        if ssoup:
            news_zoom = ssoup.find_all("div", class_="news_font")[0]
        else:
            news_zoom = None

        news_img = complete_img_a(base_url, news_zoom)
        news_content = str(news_zoom)
        # if news_zoom.select("p>img"):  # 图片标签
        #     news_img = news_zoom.select("p>img")[0]["src"]
        #     news_img = base_url + news_img
        # else:
        #     news_img = None
        #dict = dict_list(news_title, news_url, news_img, news_content, news_time, news_label)
        temp_list.append(
            spider.package_data_dict(
                title=news_title, url=news_url, img=news_img,
                content=news_content, date=news_time,
                source='福建省科学技术协会', label=news_label, tag=1))
    return temp_list


def get_fjkx():
    result_list = []
    try:
        result_list.extend(get_fjkx_news(1,
                                         r"http://www.fjkx.org/NewsList.aspx?ID=3"))
        result_list.extend(get_fjkx_news(1,
                                         r"http://www.fjkx.org/NewsList.aspx?ID=6"))
        result_list.extend(get_fjkx_news(3,
                                         r"http://www.fjkx.org/NewsList.aspx?ID=7"))
        result_list.extend(get_fjkx_news(2,
                                         r"http://www.fjkx.org/NewsList.aspx?ID=8"))
    except Exception as err:
        pass
    finally:
        return result_list

###########################甘肃科协###########################
def get_gskx_news(label, url, base_url=r'http://www.gsast.org.cn'):
    temp_list = []
    try:
        driver = get_selenium_head(url)
        if not driver:
            return temp_list
        try:
            news_list = driver.find_elements_by_class_name("mBd")[0].find_elements_by_tag_name("li")
        except:
            news_list = []
        for news in news_list:
            news_time = news.find_element_by_tag_name("span").text
            news_url = news.find_element_by_tag_name("a").get_attribute("href")
            try:
                ddriver = get_selenium_head(news_url)
                news_label = label
                news_title = ddriver.find_element_by_class_name("title").text
                news_zoom = ddriver.find_element_by_class_name("conTxt")
                bs = BeautifulSoup(news_zoom.get_attribute("outerHTML"), 'lxml')
                news_img = complete_img_a(base_url, bs)
                news_content = str(bs)
                #dict = dict_list(news_title, news_url, news_img, news_content, news_time, news_label)
                temp_list.append(
                    spider.package_data_dict(
                        title=news_title, url=news_url, img=news_img,
                        content=news_content, date=news_time,
                        source='甘肃省科学技术协会', label=news_label, tag=1))
            except:
                pass
            finally:
                ddriver.quit()
    except:
        pass
    finally:
        driver.quit()
        return temp_list


def get_gskx():
    result_list = []
    try:
        result_list.extend(get_gskx_news(1,
                                         r"http://www.gsast.org.cn/kxyw"))
        result_list.extend(get_gskx_news(1,
                                         r"http://www.gsast.org.cn/tzgg"))
        result_list.extend(get_gskx_news(3,
                                         r"http://www.gsast.org.cn/xsxh/xshd"))
        result_list.extend(get_gskx_news(1,
                                         r"http://www.gsast.org.cn/kxpj/kjgjs"))
        result_list.extend(get_gskx_news(2,
                                         r"http://www.gsast.org.cn/jcdt/lzskx3/szxw1"))
        result_list.extend(get_gskx_news(2,
                                         r"http://www.gsast.org.cn/jcdt/tsskx3/szxw2"))
    except Exception as err:
        pass
    finally:
        return result_list


###########################广东科协###########################
def get_gdkx_news(label, url, base_url=r'http://gdsta.cn'):
    temp_list = []
    soup = get_text(url)
    if not soup:
        return temp_list
    try:
        news_list = soup.find_all("div", class_="tzgg_new")[0].select("ul>li")
    except:
        news_list = []
    for one_news in news_list:
        news_url = one_news.select("li>a")[0]["href"]
        news_url = str(base_url + news_url)
        news_time = str(one_news.select("li>span")[0].text)
        news_label = str(label)
        ssoup = get_text(news_url)
        news_title = str(ssoup.find_all("div", class_="content_title")[0].text)
        news_zoom = ssoup.find_all("div", id="articleContnet")[0]
        news_img = complete_img_a(base_url, news_zoom)
        news_content = str(news_zoom)
        temp_list.append(
            spider.package_data_dict(
                title=news_title, url=news_url, img=news_img,
                content=news_content, date=news_time,
                source='广东省科学技术协会', label=news_label, tag=1))
    return temp_list


def get_gdkx_newss(label, url, base_url=r'http://gdsta.cn'):
    temp_list = []
    soup = get_text(url)
    if not soup:
        return  temp_list
    try:
        news_list = soup.find_all("div", class_="article_list_ld")[0].select("ul>li")
    except:
        news_list = []
    for one_news in news_list:
        news_title = str(one_news.select(".list_title")[0].select("div>a")[0].text)
        #print(news_title)
        news_url = one_news.select(".list_title")[0].select("div>a")[0]["href"]
        # news_url = one_news.select("li>a")[0]["href"]
        news_url = base_url + news_url
        #print(news_url)
        news_time = str(one_news.select(".ld_tag_l")[0].text)
        news_time = str(news_time.replace("\r", "").replace("\n", "").replace(" ", ""))
        #print(news_time)
        news_label = label
        #print(news_label)
        ssoup = get_text(news_url)
        if ssoup:
            if (ssoup.find_all("div", class_="c_content_overflow")):
                news_zoom = ssoup.find_all("div", class_="c_content_overflow")[0]
            else:
                news_zoom = ssoup.find_all("div", id="articleContnet")[0]
        else:
            news_zoom = None
        news_img = complete_img_a(base_url, news_zoom)
        if not news_img: news_img = None
        #print(news_img)
        news_content = str(news_zoom)
        temp_list.append(
            spider.package_data_dict(
                title=news_title, url=news_url, img=news_img,
                content=news_content, date=news_time,
                source='广东省科学技术协会', label=news_label, tag=1))
    return temp_list


def get_gdkx():
    result_list = []
    try:
        result_list.extend(get_gdkx_news(1, r'http://gdsta.cn/Category_28/Index.aspx'))
        result_list.extend(get_gdkx_newss(1, r'http://gdsta.cn/Category_72/Index.aspx'))
        result_list.extend(get_gdkx_newss(1, r'http://gdsta.cn/Category_204/Index.aspx'))
        result_list.extend(get_gdkx_newss(3, r'http://gdsta.cn/Category_221/Index.aspx'))
        result_list.extend(get_gdkx_newss(2, r'http://gdsta.cn/Category_29/Index.aspx'))
    except Exception as err:
        pass
    finally:
        #news_to_json(result_list, "gdkx.json")
        return result_list


###########################广西科协###########################
def get_gxkx_news(label, url, base_url=r'http://www.gxast.org.cn'):
    temp_list = []
    soup = get_text(url)
    if not soup:
        return temp_list
    try:
        news_list = soup.find_all("div", class_="recognition_awards_list")[0].select("ul>li")
    except :
        news_list = []
    for one_news in news_list:
        news_title = str(one_news.select("li>span>a")[0]["title"])
        news_url = str(one_news.select("li>span>a")[0]["href"])
        news_time = str(one_news.select("li>span")[1].text)
        news_label = str(label)
        ssoup = get_text(news_url)
        if  ssoup:
            news_zoom = ssoup.find_all("div", class_="recognition_awards_list")[0]
        else:
            news_zoom = None
        news_img = complete_img_a(base_url, news_zoom)
        if news_img == 'http://www.gxast.org.cn/r/cms/www_gxast_org_cn/default/images/fj_icon.gif':
            news_img = None
        news_content = str(news_zoom)

        temp_list.append(
            spider.package_data_dict(
                title=news_title, url=news_url, img=news_img,
                content=news_content, date=news_time,
                source='广西壮族自治区科协', label=news_label, tag=1))
    return temp_list


def get_gxkx():
    result_list = []
    try:
        result_list.extend(get_gxkx_news(1, r'http://www.gxast.org.cn/tongzhigonggao2/index.jhtml'))
        result_list.extend(get_gxkx_news(1, r'http://www.gxast.org.cn/gxastttyw/index.jhtml'))
        result_list.extend(get_gxkx_news(1, r'http://www.gxast.org.cn/dongtaixinxi/index.jhtml'))
        result_list.extend(get_gxkx_news(3, r'http://www.gxast.org.cn/xuehuixueshu/index.jhtml'))
        result_list.extend(get_gxkx_news(2, r'http://www.gxast.org.cn/jckp/index.jhtml'))
        result_list.extend(get_gxkx_news(2, r'http://www.gxast.org.cn/kepudongtai/index.jhtml'))
    except Exception as err:
        pass
    finally:
        #news_to_json(result_list, "gxkx.json")
        return result_list


###########################海南省科学技术协会###########################
def get_hnkx_news(label, url, base_url=r'http://www.hainanast.org.cn'):
    temp_list = []
    try:
        driver = get_selenium_head(url)
        news_list = driver.find_elements_by_class_name("d_nr1")[0].find_elements_by_tag_name("a")
        # news_list = soup.find_all("div", class_="d_nr1")
        # print(news_list)
        # news_list = news_list[0].select("a")
        for one_news in news_list:
            news_title = str(one_news.find_elements_by_class_name("biaoti_h")[0].text)
            # print(news_title)
            news_url = one_news.get_attribute("href")
            # news_url = str(base_url + news_url)
            # print(news_url)
            # news_time = str(one_news.select("tr>td>span")[0].text)
            news_label = str(label)
            try:
                ssoup = get_selenium_head(news_url)
                news_time = ssoup.find_elements_by_class_name("wz_qita")[0].text
                # news_time = ssoup.find_all("div", class_="wz_qita")[0].text
                news_time = re.search(r"(\d{4}/\d{1,2}/\d{1,2})", news_time)[0]
                news_time = datetime.datetime.strptime(news_time, '%Y/%m/%d').date()
                news_time = news_time.strftime("%Y-%m-%d")
                # print(news_time)
                news_zoom = ssoup.find_elements_by_class_name("d_nr")[0]
                bs = BeautifulSoup(news_zoom.get_attribute("outerHTML"), 'lxml')
                news_img = complete_img_a(base_url, bs)
                # news_img = s_complete_img_a(base_url, news_zoom)
                if not news_img: news_img = None
                news_content = str(bs)
                #dict = dict_list(news_title, news_url, news_img, news_content, news_time, news_label)
                temp_list.append(
                    spider.package_data_dict(
                        title=news_title, url=news_url, img=news_img,
                        content=news_content, date=news_time,
                        source='海南省科学技术协会', label=news_label, tag=1))
            except:
                pass
            finally:
                ssoup.quit()
    except:
        pass
    finally:
        driver.quit()
        return temp_list


def get_hnkx():
    result_list = []
    try:
        result_list.extend(get_hnkx_news(1, r'http://www.hainanast.org.cn/wz_list.asp?pd_id=230'))
        result_list.extend(get_hnkx_news(1, r'http://www.hainanast.org.cn/wz_list.asp?pd_id=257'))
        result_list.extend(get_hnkx_news(1, r'http://www.hainanast.org.cn/wz_list.asp?pd_id=212'))
        result_list.extend(get_hnkx_news(2, r'http://www.hainanast.org.cn/wz_list.asp?pd_id=233'))
        result_list.extend(get_hnkx_news(2, r'http://www.hainanast.org.cn/wz_list.asp?daohang_id=59'))
        result_list.extend(get_hnkx_news(3, r'http://www.hainanast.org.cn/wz_list.asp?daohang_id=73'))
    except Exception as err:
        pass
    finally:
        #news_to_json(result_list, "hnkx.json")
        return result_list


###########################贵州省科学技术协会###########################
def get_gzkx_news(label, url, base_url=r'http://www.gzast.org'):
    temp_list = []
    soup = get_text(url)
    if not soup:
        return temp_list
    try:
        news_list = soup.find_all("table")[0].select("tr")
    except:
        news_list = []
    for one_news in news_list:
        if (one_news.select("tr>td>a")):
            news_title = str(one_news.select("tr>td>a")[0].text)
            news_url = str(one_news.select("tr>td>a")[0]["href"])
            news_url = str(base_url + news_url)
            news_time = str(one_news.select("tr>td>span")[0].text)
            news_label = str(label)
            ssoup = get_text(news_url)
            if ssoup:
                news_zoom = ssoup.find_all("div", id="Zoom")[0]
            else:
                news_zoom = None
            news_img = complete_img_a(base_url, news_zoom)
            if not news_img: news_img = None
            news_content = str(news_zoom)
            #dict = dict_list(news_title, news_url, news_img, news_content, news_time, news_label)
            #temp_list.append(dict)
            temp_list.append(
                spider.package_data_dict(
                    title=news_title, url=news_url, img=news_img,
                    content=news_content, date=news_time,
                    source='贵州省科学技术协会', label=news_label, tag=1))

    return temp_list


def get_gzkx():
    result_list = []
    try:
        result_list.extend(get_gzkx_news(1, r'http://www.gzast.org/kxdt/tzgg/index.shtml'))
        result_list.extend(get_gzkx_news(1, r'http://www.gzast.org/xhxw/zyxw/index.shtml'))
        result_list.extend(get_gzkx_news(1, r'http://www.gzast.org/kxdt/gzdt/index.shtml'))
        result_list.extend(get_gzkx_news(3, r'http://www.gzast.org/kxdt/xhdt/index.shtml'))
        result_list.extend(get_gzkx_news(1, r'http://www.gzast.org/kxdt/dggz/index.shtml'))
        result_list.extend(get_gzkx_news(2, r'http://www.gzast.org/kxdt/dfkx/index.shtml'))
    except Exception as err:
        pass
    finally:
        #news_to_json(result_list, "gzkx.json")
        return result_list


###########################河北省科学技术协会###########################
def get_hbkx_news(label, url, base_url=r'http://www.hbast.org.cn'):
    temp_list = []
    try:
        soup = get_selenium_head(url)
        if not soup:
            return temp_list

        try:
            news_list = soup.find_elements_by_tag_name("table")[19].find_elements_by_tag_name("tr")
        except:
            news_list = []
        for one_news in news_list:
            if (one_news.find_elements_by_tag_name("a")):
                news_title = str(one_news.find_elements_by_tag_name("a")[0].text)
                print(news_title)
                news_url = str(one_news.find_elements_by_tag_name("a")[0].get_attribute("href"))
                news_label = str(label)
                try:
                    ssoup = get_selenium_head(news_url)
                    # print(ssoup.page_source)
                    news_time = ssoup.find_elements_by_tag_name("td")[38].text
                    news_time = re.search(r"(\d{4}-\d{1,2}-\d{1,2})", news_time)[0]
                    news_time = datetime.datetime.strptime(news_time, '%Y-%m-%d').date()
                    news_time = news_time.strftime("%Y-%m-%d")
                    # print(news_time)
                    news_zoom = ssoup.find_elements_by_id("newscontent")[0]
                    # print(news_zoom)
                    bs = BeautifulSoup(news_zoom.get_attribute("outerHTML"), 'lxml')
                    news_img = complete_img_a(base_url, bs)
                    # news_img = s_complete_img_a(base_url, news_zoom)
                    if not news_img: news_img = None
                    news_content = str(bs)
                    #dict = dict_list(news_title, news_url, news_img, news_content, news_time, news_label)
                    #temp_list.append(dict)
                    temp_list.append(
                        spider.package_data_dict(
                            title=news_title, url=news_url, img=news_img,
                            content=news_content, date=news_time,
                            source='河北省科学技术协会', label=news_label, tag=1))
                except Exception as e:
                    print(e)
                finally:
                    ssoup.quit()

    except Exception as e:
        print(e)
    finally:
        soup.quit()
        return temp_list


def get_hbkx():
    result_list = []
    try:
        result_list.extend(get_hbkx_news(1, r'http://www.hbast.org.cn/News/TZGG/index.html'))
        result_list.extend(get_hbkx_news(1, r'http://www.hbast.org.cn/News/YWZL/index.html'))
        result_list.extend(get_hbkx_news(1, r'http://www.hbast.org.cn/News/GZDT/ZH/index.html'))
        result_list.extend(get_hbkx_news(3, r'http://www.hbast.org.cn/News/GZDT/XH/index.html'))
        result_list.extend(get_hbkx_news(2, r'http://www.hbast.org.cn/News/GZDT/KP/index.html'))
        result_list.extend(get_hbkx_news(2, r'http://www.hbast.org.cn/News/TTXW/index.html'))
    except Exception as err:
        pass
    finally:
        #news_to_json(result_list, "hbkx.json")
        return result_list


###########################河南省科学技术协会###########################
def get_henankx_news(label, url, base_url=r'http://www.hast.net.cn'):
    temp_list = []
    soup = get_text(url)
    if not soup:
        return  temp_list
    try:
        news_list = soup.find_all("div", class_="news-list")[0].select("a")
    except:
        news_list = []
    for one_news in news_list:
        news_title = str(one_news.select("a>div>p>b")[0].text)
        #print(news_title)
        news_url = str(one_news["href"])
        news_url = str(base_url + news_url)
        news_time = str(one_news.select("a>div>div")[0].select("span")[1].text)
        news_label = str(label)
        ssoup = get_text(news_url)
        if ssoup:
            t_zoom = ssoup.find_all("article", class_="show")[0]
        else:
            t_zoom = None
        news_img = complete_img_a(base_url, t_zoom)
        if t_zoom:
            t_zoom = t_zoom.select("p")
            news_zoom = ""
            for p in t_zoom:
                news_zoom = news_zoom + str(p)
        else:
            news_zoom = None
        # print(news_zoom)
        if not news_img: news_img = None
        news_content = str(news_zoom)
        #dict = dict_list(news_title, news_url, news_img, news_content, news_time, news_label)
        #temp_list.append(dict)
        temp_list.append(
            spider.package_data_dict(
                title=news_title, url=news_url, img=news_img,
                content=news_content, date=news_time,
                source='河南省科学技术协会', label=news_label, tag=1))

    return temp_list


def get_henankx():
    result_list = []
    try:
        result_list.extend(get_henankx_news(1, r'http://www.hast.net.cn/general?cid=313'))
        result_list.extend(get_henankx_news(1, r'http://www.hast.net.cn/general?cid=129'))
        result_list.extend(get_henankx_news(1, r'http://www.hast.net.cn/general?cid=187'))
        result_list.extend(get_henankx_news(1, r'http://www.hast.net.cn/general?cid=188'))
        result_list.extend(get_henankx_news(3, r'http://www.hast.net.cn/general?cid=189'))
        result_list.extend(get_henankx_news(2, r'http://www.hast.net.cn/organization?cid=204'))
    except Exception as err:
        pass
    finally:
        #news_to_json(result_list, "henan.json")
        return result_list


###########################黑龙江省科学技术协会###########################
def get_hljkx_news(label, url, base_url=r'http://www.hljkx.org.cn'):
    temp_list = []
    try:

        soup = get_selenium_head(url)
        if not soup:
            return temp_list
        try:
            news_list = soup.find_elements_by_class_name("default_pgContainer")[0].find_elements_by_tag_name("li")
        except:
            news_list = []
        for one_news in news_list:
            news_title = str(one_news.find_elements_by_tag_name("a")[0].text)

            news_url = str(one_news.find_elements_by_tag_name("a")[0].get_attribute("href"))
            news_label = label
            try:
                ssoup = get_selenium_head(news_url)
                news_time = ssoup.find_elements_by_class_name("detail_extend")[0].text
                news_time = re.search(r"(\d{4}-\d{1,2}-\d{1,2})", news_time)[0]
                news_zoom = ssoup.find_elements_by_id("fontzoom")[0]
                bs = BeautifulSoup(news_zoom.get_attribute("outerHTML"), 'lxml')
                news_img = complete_img_a(base_url, bs)
                news_content = str(bs)
                if not news_img: news_img = None
                #dict = dict_list(news_title, news_url, news_img, news_content, news_time, news_label)
                #temp_list.append(dict)
                temp_list.append(
                    spider.package_data_dict(
                        title=news_title, url=news_url, img=news_img,
                        content=news_content, date=news_time,
                        source='黑龙江省科学技术协会', label=news_label, tag=1))

            except Exception as err:
                pass

            finally:
                ssoup.quit()
    except Exception as err:
        pass
    finally:
        soup.quit()
        return temp_list


def get_hljkx():
    result_list = []
    try:
        result_list.extend(get_hljkx_news(1, r'http://www.hljkx.org.cn/col/col581/index.html'))
        result_list.extend(get_hljkx_news(1, r'http://www.hljkx.org.cn/col/col562/index.html'))
        result_list.extend(get_hljkx_news(1, r'http://www.hljkx.org.cn/col/col607/index.html'))
        result_list.extend(get_hljkx_news(2, r'http://www.hljkx.org.cn/col/col620/index.html'))
        result_list.extend(get_hljkx_news(2, r'http://www.hljkx.org.cn/col/col621/index.html'))
        result_list.extend(get_hljkx_news(3, r'http://www.hljkx.org.cn/col/col1003/index.html'))
    except Exception as err:
        pass
    finally:
        #news_to_json(result_list, "hlj.json")
        return result_list


###########################湖北省科学技术协会###########################
def get_hubeikx_news(label, url, base_url=r'http://www.hbkx.org.cn'):
    temp_list = []
    try:
        soup = get_text(url)
        if not soup:
            return temp_list
        try:
            news_list = soup.find_all("ul", class_="min600")[0].select("li")
        except:
            news_list = []
        for one_news in news_list:
            news_title = str(one_news.select("li>a")[0].text)

            news_url = str(one_news.select("li>a")[0]["href"])
            news_url = str(base_url + news_url)
            news_time = str(one_news.select("li>span")[0].text)
            news_label = str(label)
            try:
                ssoup = get_text(news_url)
                if ssoup:
                    news_zoom = ssoup.find_all("div", class_="detailed_W_p2 txt")[0]
                else:
                    news_zoom=None
                news_img = complete_img_a(base_url, news_zoom)
                if not news_img: news_img = None
                news_content = str(news_zoom)
                #dict = dict_list(news_title, news_url, news_img, news_content, news_time, news_label)
                #temp_list.append(dict)
                temp_list.append(
                    spider.package_data_dict(
                        title=news_title, url=news_url, img=news_img,
                        content=news_content, date=news_time,
                        source='湖北省科学技术协会', label=news_label, tag=1))

            except Exception as err:
                pass
                #print("error occors while request " + news_url + " !!!!!")
    except Exception as err:
        pass
        #print("an error occors while request " + url + " !!!!!")
    return temp_list


def get_hubeikx():
    result_list = []
    try:
        result_list.extend(
            get_hubeikx_news(1, r'http://www.hbkx.org.cn/news/list?columnid=29189de9c17b4140acd39d76a472a6cb'))
        result_list.extend(
            get_hubeikx_news(1, r'http://www.hbkx.org.cn/news/list?columnid=f6315c8a52914f15a12ffd4fba73ee90'))
        result_list.extend(
            get_hubeikx_news(3, r'http://www.hbkx.org.cn/news/list?columnid=7ae247e0f72b417ba711c6008908fda0'))
        result_list.extend(
            get_hubeikx_news(2, r'http://www.hbkx.org.cn/news/list?columnid=357015de377c42a2943cf96733df0674'))
        result_list.extend(
            get_hubeikx_news(2, r'http://www.hbkx.org.cn/news/list?columnid=948cf82839654aa2b33c0affa0904249'))
        result_list.extend(
            get_hubeikx_news(2, r'http://www.hbkx.org.cn/news/list?columnid=b45fe74919c4438885274ab4ff57ee6c'))
        result_list.extend(
            get_hubeikx_news(1, r'http://www.hbkx.org.cn/news/list?columnid=0559e99867bb4039958aaff8fdf73cb1'))
    except Exception as err:
        pass
    finally:
        #news_to_json(result_list, "hubei.json")
        return result_list


###########################湖南省科学技术协会###########################
def get_hunankx_news(label, url, base_url=r'http://www.hnast.org.cn'):
    temp_list = []
    # try:
    soup = get_text(url)
    if not soup:
        return  temp_list
    # print(soup)
    try:
        news_list = soup.find_all("div", class_="gg-mian-gengduo")[0].select("h3")
    except:
        news_list = []
    for one_news in news_list:
        news_title = str(one_news.select("h3>a")[0]["title"])
        news_url = str(one_news.select("h3>a")[0]["href"])
        news_url = re.search(r"/.*", news_url)[0]
        news_url = str(base_url + '/portal'+  news_url)
        news_label = str(label)
        ssoup = get_text(news_url)
        if ssoup:
            news_time = ssoup.find_all("td", class_="gggengxin time-font")[0].text
            news_time = re.search(r"(\d{4}-\d{1,2}-\d{1,2})", news_time)[0]
            news_zoom = ssoup.find_all("iframe", id="contentHtmlIframe")[0]["src"]
            news_zoom = get_text(news_zoom)
        else:
            news_zoom = None
            news_time = None
        news_img = complete_img_a(base_url, news_zoom)
        if not news_img and ssoup:
            if ssoup.find_all("img", class_="bpic"):
                news_img = ssoup.find_all("img", class_="bpic")[0]["src"]
                t_zoom = str(ssoup.find_all("img", class_="bpic")[0])
                news_zoom = t_zoom + str(news_zoom)
            else:
                news_img = None
        news_content = str(news_zoom)
        #dict = dict_list(news_title, news_url, news_img, news_content, news_time, news_label)
        #temp_list.append(dict)
        temp_list.append(
            spider.package_data_dict(
                title=news_title, url=news_url, img=news_img,
                content=news_content, date=news_time,
                source='湖南省科学技术协会', label=news_label, tag=1))

    return temp_list


def get_hunankx_nnews(label, url, base_url=r'http://www.hnast.org.cn'):
    temp_list = []
    try:
        soup = get_selenium_head(url)
        if not soup:
            return temp_list

        if label == 3:
            left_click = soup.find_elements_by_class_name("crop")[3]
            ActionChains(soup).click(left_click).perform()
        elif label == 2:
            left_click = soup.find_elements_by_class_name("crop")[4]
            ActionChains(soup).click(left_click).perform()
        try:
            news_list = soup.find_elements_by_id("content_list")[0].find_elements_by_tag_name("div")
        except:
            news_list = []
        for one_news in news_list:
            if one_news.get_attribute("class") == "gg-sure-dongtai detail-fire":
                news_title = one_news.find_elements_by_tag_name("p")[0].text
                contentNo = one_news.get_attribute("onclick")
                contentNo = str(re.search(r"\d{4}", contentNo)[0])
                if label == 3:
                    categoryNo = 14
                elif label == 2:
                    categoryNo = 18
                elif label == 2:
                    categoryNo = 16
                news_url = "/article/detail.action?categoryno=" + str(categoryNo) + "&contentno=" + str(contentNo)
                news_url = str(base_url +  '/portal/'+news_url)
                try:
                    ssoup = get_selenium_head(news_url)
                    try:
                        news_time = ssoup.find_elements_by_class_name("time-font")[0].text.split('：')[-1].split(' ')[0]
                    except:
                        news_time = datetime.date.today()
                    news_label = label
                    news_zoom = ssoup.find_elements_by_id("contentHtmlIframe")[0].get_attribute("src")
                    news_zoom = get_text(news_zoom)
                    news_img = complete_img_a(base_url, news_zoom)
                    news_content = str(news_zoom)
                    if not news_img:
                        news_img = None
                    #dict = dict_list(news_title, news_url, news_img, news_content, news_time, news_label)
                    #temp_list.append(dict)
                    temp_list.append(
                        spider.package_data_dict(
                            title=news_title, url=news_url, img=news_img,
                            content=news_content, date=news_time,
                            source='湖南省科学技术协会', label=news_label, tag=1))
                except Exception as err:
                    pass
                finally:
                    ssoup.quit()

    except Exception as err:
        pass
    finally:
        soup.quit()
        return temp_list


def get_hunankx_nnnews(label, url, base_url=r'http://www.hnast.org.cn'):
    temp_list = []
    soup = get_text(url)
    if not soup:
        return temp_list
    try:
        news_list = soup.find_all("div", class_="gg-sousuozw-1")
    except:
        news_list = []
    for one_news in news_list:
        news_title = str(one_news.select("div>h3>a")[0].text)
        news_url = str(one_news.select("div>h3>a")[0]["href"])
        news_url = re.search(r"/.*", news_url)[0]
        news_url = str(base_url + '/portal/'+ news_url)
        news_time = str(one_news.select("div>p>span")[0])
        news_time = re.search(r"(\d{4}-\d{1,2}-\d{1,2})", news_time)[0]
        news_label = str(label)
        ssoup = get_text(news_url)
        if ssoup:
            news_zoom = ssoup.find_all("iframe", id="contentHtmlIframe")[0]["src"]
            news_zoom = get_text(news_zoom)
        else:
            news_zoom = None
        news_img = complete_img_a(base_url, news_zoom)
        if not news_img:
            news_img = None
        news_content = str(news_zoom)
        #dict = dict_list(news_title, news_url, news_img, news_content, news_time, news_label)
        #temp_list.append(dict)
        temp_list.append(
            spider.package_data_dict(
                title=news_title, url=news_url, img=news_img,
                content=news_content, date=news_time,
                source='湖南省科学技术协会', label=news_label, tag=1))

    return temp_list


def get_hunankx():
    result_list = []
    try:
        result_list.extend(get_hunankx_news(1, r'http://www.hnast.org.cn/portal/index/importantNews.action'))
        result_list.extend(get_hunankx_news(1, r'http://www.hnast.org.cn/portal/work/more.action?categoryno=5'))
        result_list.extend(get_hunankx_nnews(3, r'http://www.hnast.org.cn/portal/comm/index.action'))
        result_list.extend(get_hunankx_nnews(2, r'http://www.hnast.org.cn/portal/comm/index.action'))
        result_list.extend(get_hunankx_nnews(2,
                                             r'http://www.hnast.org.cn/portal/category/categoryIndex.action?parentCategoryNo=13&categoryNo=16'))
        result_list.extend(get_hunankx_news(2, r'http://www.hnast.org.cn/portal/work/more.action?categoryno=6'))
        result_list.extend(get_hunankx_nnnews(1, r'http://www.hnast.org.cn/portal/notice/more.action'))
    except Exception as err:
        pass
    finally:
        #news_to_json(result_list, "hunan.json")
        return result_list


###########################吉林省科学技术协会###########################
def get_jlkx_news(label, url, base_url=r'http://www.jlstnet.net'):
    temp_list = []
    soup = json.loads(str(urllib.request.urlopen(url, timeout=10).read(), encoding="utf-8"))
    news_list = soup["data"]
    for one_news in news_list:
        news_title = str(one_news["title"])
        print(news_title)
        news_url = str(one_news["id"])
        news_url = str("http://www.jlstnet.net/newsdetails.html?newsid=" + news_url)
        news_time = str(one_news["timeymd"])
        news_label = str(label)
        news_zoom = one_news["content"]
        bs = BeautifulSoup(news_zoom, 'lxml')
        news_img = complete_img_a(base_url, bs)
        if not news_img: news_img = None
        news_content = str(news_zoom)
        #dict = dict_list(news_title, news_url, news_img, news_content, news_time, news_label)
        #temp_list.append(dict)
        temp_list.append(
            spider.package_data_dict(
                title=news_title, url=news_url, img=news_img,
                content=news_content, date=news_time,
                source='吉林省科学技术协会', label=news_label, tag=1))

    return temp_list


def get_jlkx():
    result_list = []
    try:
        result_list.extend(get_jlkx_news(1, r'http://achievements.jlskx.org.cn/web/news/pagenews/129/0/15/skx'))
        result_list.extend(get_jlkx_news(1, r'http://achievements.jlskx.org.cn/web/news/pagenews/470/0/15/skx'))
        result_list.extend(get_jlkx_news(1, r'http://achievements.jlskx.org.cn/web/news/pagenews/494/0/15/skx'))
        result_list.extend(get_jlkx_news(3, r'http://achievements.jlskx.org.cn/web/news/pagenews/99/0/15/skx'))
        result_list.extend(get_jlkx_news(2, r'http://achievements.jlskx.org.cn/web/news/pagenews/103/0/15/skx'))
        result_list.extend(get_jlkx_news(3, r'http://achievements.jlskx.org.cn/web/news/pagenews/566/0/15/skx'))
    except Exception as err:
        pass
    finally:
        #news_to_json(result_list, "jlkx.json")
        return result_list


###########################江苏省科学技术协会###########################
def get_jskx_news(label, url, base_url=r'http://www.jskx.org.cn'):
    temp_list = []
    soup = get_text(url)
    if not soup:
        return temp_list
    try:
        news_list = soup.find_all("table", class_="ywkd_more")[0].select("tbody>tr")
    except:
        news_list = []
    # print(news_list)
    for one_news in news_list:
        if one_news.select("tr>td>a"):
            news_title = str(one_news.select("tr>td>a")[0]["title"])
            print(news_title)
            news_url = str(one_news.select("tr>td>a")[0]["href"])
            # news_url = str(base_url + news_url)
            news_time = str(one_news.select("tr>td")[2].text)

            # print(news_time)
            news_label = str(label)
            ssoup = get_text(news_url)
            if ssoup:
                news_zoom = ssoup.find_all("div", id="zoom")[0]
            else:
                news_zoom = None
            news_img = complete_img_a(base_url, news_zoom)
            if not news_img: news_img = None
            news_content = str(news_zoom)
            #dict = dict_list(news_title, news_url, news_img, news_content, news_time, news_label)
            #temp_list.append(dict)
            temp_list.append(
                spider.package_data_dict(
                    title=news_title, url=news_url, img=news_img,
                    content=news_content, date=news_time,
                    source='江苏省科学技术协会', label=news_label, tag=1))

    return temp_list


def get_jskx_nnnnews(label, url, base_url=r'http://www.jskx.org.cn/'):
    temp_list = []
    soup = get_text(url)
    if not soup:
        return temp_list
    try:
        news_list = soup.find_all("table", class_="ywkd_more")
    except:
        news_list = []
    # print(soup.find_all("a", class_="default_pgContainer")[0].select("div>table>tbody>div>table"))
    # print(news_list)
    for one_news in news_list:
        if one_news.select("tbody>tr"):
            news_title = str(one_news.select("table>tbody>tr>td>a")[0]["title"])
            print(news_title)
            news_url = str(one_news.select("table>tbody>tr>td>a")[0]["href"])
            news_time = str(one_news.select("table>tbody>tr>td")[2].text)
            news_label = str(label)
            ssoup = get_text(news_url)
            if ssoup:
                news_zoom = ssoup.find_all("div", id="zoom")[0]
            else:
                news_zoom = None
            news_img = complete_img_a(base_url, news_zoom)
            if not news_img: news_img = None
            news_content = str(news_zoom)
            temp_list.append(
                spider.package_data_dict(
                    title=news_title, url=news_url, img=news_img,
                    content=news_content, date=news_time,
                    source='江苏省科学技术协会', label=news_label, tag=1))

    return temp_list


def get_jskx_nnews(label, url, base_url=r'http://www.jsxhw.org'):
    temp_list = []
    soup = get_text(url)
    if not soup:
        return temp_list
    try:
        news_list = soup.find_all("div", id="s74821126_content")[0].select("div>table>tbody>tr")
    except:
        news_list = []
    for one_news in news_list:
        if one_news.select("tr>td>a"):
            news_title = one_news.select("tr>td>a")[0].text
            print(news_title)
            # print(news_title)
            news_url = one_news.select("tr>td>a")[0]["href"]
            # print(news_url)
            news_url = str(base_url + news_url)
            news_time = str(one_news.select("tr>td")[2].text)
            news_time = re.search(r"(\d{4}-\d{1,2}-\d{1,2})", news_time)[0]
            news_label = str(label)
            ssoup = get_text(news_url)
            if ssoup:
                news_zoom = ssoup.find_all("td", id="article_content")[0]
            else:
                news_zoom = None
            news_img = complete_img_a(base_url, news_zoom)
            if not news_img: news_img = None
            news_content = str(news_zoom)
            temp_list.append(
                spider.package_data_dict(
                    title=news_title, url=news_url, img=news_img,
                    content=news_content, date=news_time,
                    source='江苏省科学技术协会', label=news_label, tag=1))

    return temp_list


def get_jskx_nnnews(label, url, base_url=r'http://www.jsxhw.org'):
    temp_list = []
    soup = get_text(url)
    if not soup:
        return temp_list
    try:
        news_list = soup.find_all("div", id="s63385712_content")[0].select("div>table>tbody>tr")
    except:
        news_list = []
    for one_news in news_list:
        if one_news.select("tr>td>span>span"):
            news_title = str(one_news.select("tr>td>span>span")[0].select("a")[0].text)
            print(news_title)
            # print(news_title)
            news_url = one_news.select("tr>td>span>span>a")[0]["href"]
            # news_url = one_news.select(("tr>td>span>a")[0]["href"])
            news_url = str(base_url + news_url)
            news_time = str(one_news.select("tr>td>span")[1].text)
            news_time = re.search(r"(\d{4}-\d{1,2}-\d{1,2})", news_time)[0]
            news_label = label
            ssoup = get_text(news_url)
            if  ssoup:
                news_zoom = ssoup.find_all("td", id="article_content")[0]
            else:
                news_zoom = None
            news_img = complete_img_a(base_url, news_zoom)
            if not news_img: news_img = None
            news_content = str(news_zoom)
            temp_list.append(
                spider.package_data_dict(
                    title=news_title, url=news_url, img=news_img,
                    content=news_content, date=news_time,
                    source='江苏省科学技术协会', label=news_label, tag=1))
    return temp_list


def get_jskx():
    result_list = []
    try:
        result_list.extend(get_jskx_news(1, r'http://www.jskx.org.cn/web/more/tzgg/1'))
        result_list.extend(get_jskx_news(1, r'http://www.jskx.org.cn/web/more/ywkd/1'))
        result_list.extend(get_jskx_nnnnews(1, r'http://www.jskx.org.cn/web/talents/gzdt/1'))
        result_list.extend(get_jskx_nnews(2, r'http://www.jsxhw.org/default.php?mod=c&s=sse3f5a24'))
        result_list.extend(get_jskx_nnnnews(2, r'http://www.jskx.org.cn/web/sxxh/nj/1'))
        result_list.extend(get_jskx_nnnews(3, r'http://www.jsxhw.org/default.php?mod=article&fid=30'))
        result_list.extend(get_jskx_news(2, r'http://www.jskx.org.cn/web/kepu/gzdt/1'))
    except Exception as err:
        pass
    finally:
        #news_to_json(result_list, "jskx.json")
        return result_list


###########################江西省科学技术协会###########################
def get_jxkx_news(label, url, base_url=r'http://www.jxkx.gov.cn'):
    temp_list = []
    soup = get_text(url)
    if not soup:
        return temp_list
    try:
        news_list = soup.find_all("div", id="liebiao")[0].select("li")
    except :
        news_list = []
    # print(news_list)
    for one_news in news_list:
        news_title = one_news.select("li>span>a")[0].text
        # print(news_title)
        news_url = str(one_news.select("li>span>a")[0]["href"])
        news_url = str(base_url + news_url)
        news_time = str(one_news.select("li>span")[1].text)
        news_label = str(label)
        ssoup = get_text(news_url)
        if ssoup:
            news_zoom = ssoup.find_all("div", id="content")[0]
        else:
            news_zoom =None
        news_img = complete_img_a(base_url, news_zoom)
        if not news_img: news_img = None
        news_content = str(news_zoom)
        temp_list.append(
            spider.package_data_dict(
                title=news_title, url=news_url, img=news_img,
                content=news_content, date=news_time,
                source='江西省科学技术协会', label=news_label, tag=1))

    return temp_list


def get_jxkx():
    result_list = []
    try:
        result_list.extend(get_jxkx_news(1, r'http://www.jxkx.gov.cn/class.asp?id=13'))
        result_list.extend(get_jxkx_news(1, r'http://www.jxkx.gov.cn/class.asp?id=6'))
        result_list.extend(get_jxkx_news(1, r'http://www.jxkx.gov.cn/class.asp?id=7'))
        result_list.extend(get_jxkx_news(2, r'http://www.jxkx.gov.cn/class.asp?id=25'))
        result_list.extend(get_jxkx_news(2, r'http://www.jxkx.gov.cn/class.asp?id=105'))
        result_list.extend(get_jxkx_news(3, r'http://www.jxkx.gov.cn/class.asp?id=8'))
        result_list.extend(get_jxkx_news(2, r'http://www.jxkx.gov.cn/class.asp?id=24'))
    except Exception as err:
        pass
    finally:
        #news_to_json(result_list, "jxkx.json")
        return result_list


###########################辽宁省科学技术协会###########################
def get_lnkx_news(label, url, base_url=r'http://www.lnast.net'):
    temp_list = []
    soup = get_text(url)
    if not soup:
        return temp_list
    try:
        news_list = soup.find_all("table", id="myInfoTb")[0].select("tr")
    except:
        news_list = []
    # print(news_list)
    for one_news in news_list:
        if one_news.select("tr>td>a"):
            news_title = one_news.select("tr>td>a")[0].text
            # print(news_title)
            news_url = str(one_news.select("tr>td>a")[0]["href"])
            news_url = news_url.replace(news_url[:2], "")
            news_url = str(base_url + news_url)
            # print(news_url)
            news_time = str(one_news.select("tr>td")[1].text)
            news_label = str(label)
            ssoup = get_text(news_url)
            if ssoup:
                # print(ssoup)
                news_zoom = ssoup.find_all("div", class_="infotxt")[0]
            else:
                news_zoom = None
            news_img = complete_img_a(base_url, news_zoom)
            if not news_img: news_img = None
            news_content = str(news_zoom)
            temp_list.append(
                spider.package_data_dict(
                    title=news_title, url=news_url, img=news_img,
                    content=news_content, date=news_time,
                    source='辽宁省科学技术协会', label=news_label, tag=1))

    return temp_list


def get_lnkx_nnews(label, url, base_url=r'http://www.lnast.net'):
    temp_list = []
    soup = get_text(url)
    if not soup:
        return  temp_list
    try:
        news_list = soup.find_all("div", id="ContentDv1")[0].select("li")
    except:
        news_list = []
    try:
        news_list1 = soup.find_all("div", id="ContentDv2")[0].select("li")
    except:
        news_list = []
    for one_news in news_list:
        if one_news.select("li>a"):
            news_title = one_news.select("li>a")[0].text
            # print(news_title)
            news_url = str(one_news.select("li>a")[0]["href"])
            news_url = news_url.replace(news_url[:2], "")
            news_url = str(base_url + news_url)
            news_time = str(one_news.select("li>div")[0].text)
            news_label = str(label)
            ssoup = get_text(news_url)
            # print(ssoup)
            if ssoup:
                news_zoom = ssoup.find_all("div", class_="infotxt")[0]
            else:
                news_zoom = None
            news_img = complete_img_a(base_url, news_zoom)
            if not news_img: news_img = None
            news_content = str(news_zoom)
            temp_list.append(
                spider.package_data_dict(
                    title=news_title, url=news_url, img=news_img,
                    content=news_content, date=news_time,
                    source='辽宁省科学技术协会', label=news_label, tag=1))

    for one_news in news_list1:
        if one_news.select("li>a"):
            news_title = one_news.select("li>a")[0].text
            # print(news_title)
            news_url = str(one_news.select("li>a")[0]["href"])
            news_url = news_url.replace(news_url[:2], "")
            news_url = str(base_url + news_url)
            news_time = str(one_news.select("li>div")[0].text)
            news_label = str(label)
            ssoup = get_text(news_url)
            if ssoup:
                # print(ssoup)
                news_zoom = ssoup.find_all("div", class_="infotxt")[0]
            else:
                news_zoom = None

            news_img = complete_img_a(base_url, news_zoom)
            if not news_img: news_img = None
            news_content = str(news_zoom)
            temp_list.append(
                spider.package_data_dict(
                    title=news_title, url=news_url, img=news_img,
                    content=news_content, date=news_time,
                    source='辽宁省科学技术协会', label=news_label, tag=1))

    return temp_list


def get_lnkx_nnnews(label, url, base_url=r'http://www.syast.org.cn'):
    temp_list = []
    soup = get_text(url)
    if  not soup:
        return soup
    try:
        news_list = soup.find_all("ul", class_="subpage-list")[0].select("li")
    except :
        news_list = []
    for one_news in news_list:
        if one_news.select("li>a"):
            news_title = one_news.select("li>a")[0].text
            # print(news_title)
            news_url = str(one_news.select("li>a")[0]["href"])

            news_time = str(one_news.select("li>span")[0].text)
            news_label = str(label)
            ssoup = get_text(news_url)
            # print(ssoup)
            if ssoup:
                news_zoom = ssoup.find_all("div", class_="artical-content")[0]
            else:
                news_zoom = None
            news_img = complete_img_a(base_url, news_zoom)
            if not news_img: news_img = None
            news_content = str(news_zoom)
            temp_list.append(
                spider.package_data_dict(
                    title=news_title, url=news_url, img=news_img,
                    content=news_content, date=news_time,
                    source='辽宁省科学技术协会', label=news_label, tag=1))

    return temp_list


def get_lnkx():
    result_list = []
    try:
        result_list.extend(get_lnkx_news(1, r'http://www.lnast.net/tzhgg/tzhtgao.aspx'))
        result_list.extend(get_lnkx_news(1, r'http://www.lnast.net/news/kexieyw.aspx'))
        result_list.extend(get_lnkx_nnews(1, r'http://www.lnast.net/news/gzdt.aspx?_nCatalogId=41'))
        result_list.extend(get_lnkx_news(3, r'http://www.lnast.net/xshxh/qt.aspx'))
        result_list.extend(get_lnkx_nnnews(2, r'http://www.syast.org.cn/cms/syskxjsxh/gzdt/glist.html'))
        result_list.extend(get_lnkx_news(3, r'http://www.lnast.net/xshxh/xshd.aspx'))
        result_list.extend(get_lnkx_news(2, r'http://www.lnast.net/kxpj/kpxdjh.aspx'))
    except Exception as err:
        pass
    finally:
        #news_to_json(result_list, "lnkx.json")
        return result_list


###########################内蒙古科学技术协会###########################
def get_nmgkx_news(label, url, base_url=r'http://www.imast.org.cn'):
    temp_list = []
    try:
        soup = get_selenium_head(url)
        news_list = soup.find_elements_by_class_name("newslist_detial")[0].find_elements_by_tag_name("li")
        # print(news_list)
        for one_news in news_list:
            news_title = str(one_news.find_elements_by_tag_name("a")[0].text)
            news_url = str(one_news.find_elements_by_tag_name("a")[0].get_attribute("href"))
            news_time = one_news.find_elements_by_tag_name("span")[0].text
            news_label = str(label)
            try:
                ssoup = get_selenium_head(news_url)
                news_zoom = ssoup.find_elements_by_class_name("TRS_Editor")[0]
                news_zoom = ssoup.find_elements_by_id("para")[0]
                bs = BeautifulSoup(news_zoom.get_attribute("outerHTML"), 'lxml')
                base_url_rule = re.compile(r"(.*)/\d{6}/")
                if base_url_rule.search(news_url):
                    base_url = str(base_url_rule.search(news_url)[0])
                # print(base_url)
                news_img = complete_img_a(base_url, bs)
                if not news_img: news_img = None
                news_content = str(bs)
                temp_list.append(
                    spider.package_data_dict(
                        title=news_title, url=news_url, img=news_img,
                        content=news_content, date=news_time,
                        source='内蒙古自治区科学技术协会', label=news_label, tag=1))

            except Exception as err:
                pass
            finally:
                ssoup.quit()
    except Exception as err:
        pass
    finally:
        soup.quit()
        return temp_list


def get_nmgkx():
    result_list = []
    try:
        result_list.extend(get_nmgkx_news(1, r'http://www.imast.org.cn/xxgk/tzgg/kxpj_5101/',
                                          base_url=r"http://www.imast.org.cn/xxgk/tzgg/kxpj_5101/"))
        result_list.extend(get_nmgkx_news(1, r'http://www.imast.org.cn/xwdt/kxyw/'))
        result_list.extend(get_nmgkx_news(1, r'http://www.imast.org.cn/xwdt/lddt/'))
        result_list.extend(get_nmgkx_news(3, r'http://www.imast.org.cn/xwdt/xsxh/stjs/'))
        result_list.extend(get_nmgkx_news(2, r'http://www.imast.org.cn/xwdt/mskx/'))
        result_list.extend(get_nmgkx_news(3, r'http://www.imast.org.cn/xwdt/xsxh/xshd/'))
        result_list.extend(get_nmgkx_news(2, r'http://www.imast.org.cn/xwdt/kxpj/jckp/'))
    except Exception as err:
        pass
    finally:
        #news_to_json(result_list, "nmgkx.json")
        return result_list


###########################宁夏回族自治区科学技术协会###########################
def get_nxkx_news(label, url, base_url=r'http://www.nxkx.org'):
    temp_list = []
    soup = get_text(url)
    if not soup:
        return temp_list
    try:
        news_list = soup.find_all("div", class_="simple_pgContainer")[0].select("li")
    except:
        news_list = []
    # print(news_list)
    for one_news in news_list:
        # news_title = one_news.select("li>a")[0]["title"]
        # print(news_title)
        news_url = str(one_news.select("li>a")[0]["href"])
        news_url = news_url.replace(news_url[:2], "")
        news_url = str(base_url + news_url)
        # print(news_url)
        # news_time = one_news.select("li>a>dl>dd>span")[0].text
        news_time = re.search("\d{4}/\d{1,2}/\d{1,2}", str(one_news))[0]
        news_time = datetime.datetime.strptime(news_time, '%Y/%m/%d').date()
        news_time = str(news_time.strftime("%Y-%m-%d"))
        news_label = str(label)
        try:
            ssoup = get_selenium_head(news_url)
            # print(ssoup.page_source)
            news_title = ssoup.find_elements_by_tag_name("h1")[0].text
            news_zoom = ssoup.find_elements_by_id("zoom")[0]
            bs = BeautifulSoup(news_zoom.get_attribute("outerHTML"), 'lxml')
            news_img = complete_img_a(base_url, bs)
            if not news_img: news_img = None
            news_content = str(bs)
            # dict = dict_list(news_title, news_url, news_img, news_content, news_time, news_label)
            # temp_list.append(dict)
            temp_list.append(
                spider.package_data_dict(
                    title=news_title, url=news_url, img=news_img,
                    content=news_content, date=news_time,
                    source='宁夏回族自治区科学技术协会', label=news_label, tag=1))

            ssoup.quit()
        except Exception as err:
            pass
            #print("can not get  " + news_url)
    return temp_list


def get_nxkx_nnews(label, url, base_url=r'http://www.yckpw.gov.cn/kpdt/gzdt'):
    temp_list = []
    soup = get_text(url)
    if not soup:
        return temp_list
    try:
        news_list = soup.find_all("ul", class_="list2")[0].select("li")
    except:
        news_list = []
    # print(news_list)
    for one_news in news_list:
        news_title = one_news.select("li>a")[0].text
        # print(news_title)
        news_url = str(one_news.select("li>a")[0]["href"])
        # news_url = news_url.replace(news_url[:1], "")
        news_url = str(base_url + news_url)
        # print(news_url)
        news_time = one_news.select("li>span")[0].text
        # print(news_time)
        news_label = str(label)
        try:
            ssoup = get_selenium_head(news_url)
            # print(ssoup.page_source)
            # news_zoom = ssoup.find_all("div", class_="con")[0]
            news_zoom = ssoup.find_elements_by_class_name("con")[0]
            bs = BeautifulSoup(news_zoom.get_attribute("outerHTML"), 'lxml')
            news_img = complete_img_a(base_url, bs)
            if not news_img: news_img = None
            news_content = str(bs)
            temp_list.append(
                spider.package_data_dict(
                    title=news_title, url=news_url, img=news_img,
                    content=news_content, date=news_time,
                    source='宁夏回族自治区科学技术协会', label=news_label, tag=1))

        except Exception as err:
            pass
        finally:
            ssoup.quit()
    return temp_list


def get_nxkx():
    result_list = []
    try:
        result_list.extend(
            get_nxkx_news(1, r'http://www.nxkx.org/kxsz/tzgg/', base_url=r"http://www.nxkx.org/kxsz/tzgg/"))
        result_list.extend(
            get_nxkx_news(1, r'http://www.nxkx.org/kxsz/nxkxyq/', base_url=r"http://www.nxkx.org/kxsz/nxkxyq/"))
        result_list.extend(
            get_nxkx_news(2, r'http://www.nxkx.org/kxpj/kpqj/nckp/', base_url=r"http://www.nxkx.org/kxpj/kpqj/nckp/"))
        result_list.extend(
            get_nxkx_news(3, r'http://www.nxkx.org/xsxh/xhkp/', base_url=r"http://www.nxkx.org/xsxh/xhkp/"))
        result_list.extend(
            get_nxkx_nnews(2, r'http://www.yckpw.gov.cn/kpdt/gzdt/', base_url=r"http://www.yckpw.gov.cn/kpdt/gzdt/"))
        result_list.extend(
            get_nxkx_news(3, r'http://www.nxkx.org/xsxh/xsjl/', base_url=r"http://www.nxkx.org/xsxh/xsjl/"))
        result_list.extend(
            get_nxkx_news(2, r'http://www.nxkx.org/kxsz/jcdt/', base_url=r"http://www.nxkx.org/kxsz/jcdt/"))
    except Exception as err:
        pass
    finally:
        #news_to_json(result_list, "nxkx.json")
        return result_list


###########################青海省科学技术协会###########################
def get_qhkx_news(label, url, base_url=r'http://www.qhkxw.com'):
    temp_list = []
    soup = get_text(url)
    if not soup:
        return temp_list
    # print(soup)
    try:
        news_list = soup.find_all("td", height="25")
    except:
        news_list = []
    # print(news_list)
    for one_news in news_list:
        news_title = one_news.select("td>a")[0].text
        # print(news_title)
        news_url = str(one_news.select("td>a")[0]["href"])
        # news_url = str(base_url + news_url)
        # news_time = str(one_news.select("li>span")[1].text)
        news_label = str(label)
        try:
            ssoup = get_selenium_head(news_url)
            # print(ssoup)
            news_time = re.search("\d{4}-\d{1,2}-\d{1,2}", str(ssoup.page_source))[0]
            news_zoom = ssoup.find_elements_by_class_name("hui13")[0]
            bs = BeautifulSoup(news_zoom.get_attribute("outerHTML"), 'lxml')
            news_img = complete_img_a(base_url, bs)
            if not news_img: news_img = None
            news_content = str(bs)
            # dict = dict_list(news_title, news_url, news_img, news_content, news_time, news_label)
            # temp_list.append(dict)
            temp_list.append(
                spider.package_data_dict(
                    title=news_title, url=news_url, img=news_img,
                    content=news_content, date=news_time,
                    source='青海省科学技术协会', label=news_label, tag=1))
        except Exception as err:
            pass
        finally:
            ssoup.quit()
    return temp_list


def get_qhkx():
    result_list = []
    try:
        result_list.append(get_qhkx_news(1, r'http://www.qhkxw.com/gg/'))
        result_list.append(get_qhkx_news(1, r'http://www.qhkxw.com/xwzx/'))
        result_list.append(get_qhkx_news(1, r'http://www.qhkxw.com/gzdt/'))
        result_list.append(get_qhkx_news(1, r'http://www.qhkxw.com/kxpj/'))
        result_list.append(get_qhkx_news(3, r'http://www.qhkxw.com/xhxs/'))
        result_list.append(get_qhkx_news(2, r'http://www.qhkxw.com/jckx/'))
    except Exception as err:
        pass
    finally:
        #news_to_json(result_list, "qhkx.json")
        return result_list


###########################山东省科学技术协会###########################
def get_sdkx_news(label, url, base_url=r'http://www.qhkxw.com'):
    temp_list = []
    soup = get_selenium_head(url)
    # print(soup)
    # print(soup.find_all("div", id="150727"))
    news_list = soup.find_elements_by_class_name("default_pgContainer")[0].find_elements_by_tag_name("a")
    # print(news_list)
    # print(news_list)
    for one_news in news_list:
        news_title = one_news.get_attribute("title")
        # print(news_title)
        news_url = one_news.get_attribute("href")
        # news_url = str(base_url + news_url)
        # news_time = str(one_news.select("li>span")[1].text)
        news_label = str(label)
        try:
            ssoup = get_selenium_head(news_url)
            # print(ssoup)
            news_time = re.search("\d{4}-\d{1,2}-\d{1,2}", str(ssoup.page_source))[0]
            news_zoom = ssoup.find_elements_by_class_name("con")[0]
            bs = BeautifulSoup(news_zoom.get_attribute("outerHTML"), 'lxml')
            news_img = complete_img_a(base_url, bs)
            if not news_img: news_img = None
            news_content = str(bs)
            # dict = dict_list(news_title, news_url, news_img, news_content, news_time, news_label)
            # temp_list.append(dict)
            temp_list.append(
                spider.package_data_dict(
                    title=news_title, url=news_url, img=news_img,
                    content=news_content, date=news_time,
                    source='山东省科学技术协会', label=news_label, tag=1))
        except Exception as err:
            pass
        finally:
            ssoup.quit()

    return temp_list


def get_sdkx():
    result_list = []
    try:
        result_list.extend(get_sdkx_news(1, r'http://www.sdast.org.cn/col/col60378/index.html'))
        result_list.extend(get_sdkx_news(1, r'http://www.sdast.org.cn/col/col60367/index.html'))
        result_list.extend(get_sdkx_news(1, r'http://www.sdast.org.cn/col/col60371/index.html'))
        result_list.extend(get_sdkx_news(2, r'http://www.sdast.org.cn/col/col60254/index.html'))
        result_list.extend(get_sdkx_news(3, r'http://www.sdast.org.cn/col/col60374/index.html'))
        result_list.extend(get_sdkx_news(2, r'http://www.sdast.org.cn/col/col60707/index.html'))
    except Exception as err:
        pass
    finally:
        #news_to_json(result_list, "sdkx.json")
        return result_list


###########################山西省科学技术协会###########################
def get_sxkx_news(label, url, base_url=r'http://www.sxast.cn'):
    temp_list = []
    soup = get_text(url)
    if not soup:
        return temp_list
    try:
        news_list = soup.find_all("table", width="697")
    except:
        news_list = []
    for one_news in news_list:
        news_title = one_news.select("td>span>a")[0]["title"]
        news_url = one_news.select("td>span>a")[0]["href"]
        news_url = str(base_url + news_url)
        news_time = str(one_news.select("tr>td")[2].text)
        news_label = str(label)
        try:
            ssoup = get_selenium_head(news_url)
            if ssoup:
                news_zoom = ssoup.find_elements_by_class_name("content")[0]
            else:
                news_zoom = None
            bs = BeautifulSoup(news_zoom.get_attribute("outerHTML"), 'lxml')
            news_img = complete_img_a(base_url, bs)
            if not news_img: news_img = None
            news_content = str(bs)
            # dict = dict_list(news_title, news_url, news_img, news_content, news_time, news_label)
            # temp_list.append(dict)
            temp_list.append(
                spider.package_data_dict(
                    title=news_title, url=news_url, img=news_img,
                    content=news_content, date=news_time,
                    source='山西省科学技术协会', label=news_label, tag=1))
        except Exception as err:
            pass
        finally:
            ssoup.quit()
    return temp_list


def get_sxkx():
    result_list = []
    try:
        result_list.extend(get_sxkx_news(1, r'http://www.sxast.cn/html/lm/tzgg/index.html'))
        result_list.extend(get_sxkx_news(1, r'http://www.sxast.cn/html/lm/kxyw/index.html'))
        result_list.extend(get_sxkx_news(1, r'http://www.sxast.cn/html/lm/sygzdt/index.html'))
        result_list.extend(get_sxkx_news(2, r'http://www.sxast.cn/html/lm/jcdt/index.html'))
        result_list.extend(get_sxkx_news(3, r'http://www.sxast.cn/html/lm/syxhdt/index.html'))
        result_list.extend(get_sxkx_news(1, r'http://www.sxast.cn/html/lm/dztt/index.html'))
    except Exception as err:
        pass
    finally:
        #news_to_json(result_list, "sxkx.json")
        return result_list


###########################陕西省科学技术协会###########################
def get_shanxikx_news(label, url, base_url=r'http://www.snast.org.cn'):
    temp_list = []
    soup = get_text(url)
    if not soup:
        return temp_list
    try:
        news_list = soup.find_all("td", class_="f14blue")[0].select("a")
    except:
        news_list = []
    for one_news in news_list:
        news_title = one_news.select("a>font")[0].text
        news_url = one_news["href"]
        # news_url = str(base_url + news_url)
        # news_time = str(one_news.select("tr>td")[2].text)
        news_label = str(label)
        ssoup = get_text(news_url)
        news_time = re.search("\d{4}/\d{1,2}/\d{1,2}", str(ssoup))[0]
        news_time = datetime.datetime.strptime(news_time, '%Y/%m/%d').date()
        news_time = str(news_time.strftime("%Y-%m-%d"))
        news_zoom = ssoup.find_all("div", id="zw")[0]
        # bs = BeautifulSoup(news_zoom.get_attribute("outerHTML"), 'lxml')
        news_img = complete_img_a(base_url, news_zoom)
        if not news_img: news_img = None
        news_content = str(news_zoom)
        # dict = dict_list(news_title, news_url, news_img, news_content, news_time, news_label)
        # temp_list.append(dict)
        temp_list.append(
            spider.package_data_dict(
                title=news_title, url=news_url, img=news_img,
                content=news_content, date=news_time,
                source='陕西省科学技术协会', label=news_label, tag=1))
    return temp_list


def get_shanxikx():
    result_list = []
    try:
        result_list.extend(get_shanxikx_news(1, r'http://www.snast.org.cn/admin/pub_newschannel.asp?chid=100004'))
        result_list.extend(get_shanxikx_news(1, r'http://www.snast.org.cn/admin/pub_newschannel.asp?chid=100036'))
        result_list.extend(get_shanxikx_news(1, r'http://www.snast.org.cn/admin/pub_newschannel.asp?chid=100038'))
        result_list.extend(get_shanxikx_news(2, r'http://www.snast.org.cn/admin/pub_newschannel.asp?chid=100040'))
        result_list.extend(get_shanxikx_news(3, r'http://www.snast.org.cn/admin/pub_newschannel.asp?chid=100058'))
        result_list.extend(get_shanxikx_news(1, r'http://www.snast.org.cn/admin/pub_newschannel.asp?chid=100043'))
    except Exception as err:
        pass
    finally:
        #news_to_json(result_list, "shanxikx.json")
        return result_list


###########################上海市科学技术协会###########################
def get_shkx_news(label, url, base_url=r'http://www.sast.gov.cn'):
    temp_list = []
    try:
        soup = get_selenium_head(url)
        news_list = soup.find_elements_by_class_name("index_toutao_word")
        for one_news in news_list:
            news_title = one_news.find_elements_by_tag_name("img")[0].get_attribute("alt")
            news_url = one_news.find_elements_by_tag_name("a")[0].get_attribute("href")
            news_url = str(base_url + news_url)
            # news_time = str(one_news.select("tr>td")[2].text)
            news_label = str(label)
            try:
                ssoup = get_selenium_head(news_url)
                news_time = re.search("\d{4}年\d{1,2}月\d{1,2}", str(ssoup.page_source))[0]
                news_time = datetime.datetime.strptime(news_time, '%Y年%m月%d').date()
                news_time = str(news_time.strftime("%Y-%m-%d"))
                news_zoom = ssoup.find_elements_by_class_name("word_contentpage")[1]
                bs = BeautifulSoup(news_zoom.get_attribute("outerHTML"), 'lxml')
                news_img = complete_img_a(base_url, bs)
                if not news_img: news_img = None
                news_content = str(bs)
                # dict = dict_list(news_title, news_url, news_img, news_content, news_time, news_label)
                # temp_list.append(dict)
                temp_list.append(
                    spider.package_data_dict(
                        title=news_title, url=news_url, img=news_img,
                        content=news_content, date=news_time,
                        source='上海市科学技术协会', label=news_label, tag=1))

            except Exception as err:
                pass
            finally:
                ssoup.quit()
    except Exception as err:
        pass
    finally:
        soup.quit()
        return temp_list


def get_shkx_nnews(label, url, base_url=r'http://www.sast.gov.cn'):
    temp_list = []
    try:
        soup = get_selenium_head(url)
        news_list = soup.find_elements_by_class_name("vertical")
        for one_news in news_list:
            news_title = one_news.find_elements_by_tag_name("a")[0].text.strip()
            news_url = one_news.find_elements_by_tag_name("a")[0].get_attribute("href")
            news_url = str(base_url + news_url)
            news_time = str(one_news.find_elements_by_tag_name("span")[1].text)
            news_label = str(label)
            try:
                ssoup = get_selenium_head(news_url)
                news_zoom = ssoup.find_elements_by_class_name("word_contentpage")[1]
                bs = BeautifulSoup(news_zoom.get_attribute("outerHTML"), 'lxml')
                news_img = complete_img_a(base_url, bs)
                if not news_img: news_img = None
                news_content = str(bs)
                # dict = dict_list(news_title, news_url, news_img, news_content, news_time, news_label)
                # temp_list.append(dict)
                temp_list.append(
                    spider.package_data_dict(
                        title=news_title, url=news_url, img=news_img,
                        content=news_content, date=news_time,
                        source='上海市科学技术协会', label=news_label, tag=1))

            except Exception as err :
                pass
            finally:
                ssoup.quit()
    except Exception as err:
        pass
    finally:
        soup.quit()
        return temp_list


def get_shkx():
    result_list = []
    try:
        result_list.extend(get_shkx_nnews(1, r'http://www.sast.gov.cn/list/175.html'))
        result_list.extend(get_shkx_news(1, r'http://www.sast.gov.cn/NewsList.html'))
        result_list.extend(get_shkx_nnews(1, r'http://www.sast.gov.cn/list/36.html'))
        result_list.extend(get_shkx_nnews(2, r'http://www.sast.gov.cn/list/37.html'))
        result_list.extend(get_shkx_nnews(3, r'http://www.sast.gov.cn/list/109.html'))
    except Exception as err:
        pass
    finally:
        #news_to_json(result_list, "shkx.json")
        return result_list


###########################四川省科学技术协会###########################
def get_sckx_news(label, url, base_url=r'http://www.sckx.org.cn'):
    temp_list = []
    soup = get_text(url)
    if not soup:
        return temp_list
    try:
        news_list = soup.find_all("div", class_="center-content")[0].select("div")
        print(len(news_list))
    except:
        news_list = []
    for one_news in news_list:
        news_title = one_news.select("a")[0]["title"]
        news_url = one_news.select("a")[0]["href"]
        news_url = str(base_url + news_url)
        news_time = str(one_news.select("span")[0].text)
        news_time = re.search("\d{4}-\d{1,2}-\d{1,2}", news_time)[0]
        news_label = str(label)
        ssoup = get_text(news_url)
        if ssoup:
            news_zoom = ssoup.find_all("div", class_="center-content")[0]
        else:
            news_zoom = None

        # bs = BeautifulSoup(news_zoom.get_attribute("outerHTML"), 'lxml')
        news_img = complete_img_a(base_url, news_zoom)
        if not news_img: news_img = None
        news_content = str(news_zoom)
        # dict = dict_list(news_title, news_url, news_img, news_content, news_time, news_label)
        # temp_list.append(dict)
        temp_list.append(
            spider.package_data_dict(
                title=news_title, url=news_url, img=news_img,
                content=news_content, date=news_time,
                source='四川省科学技术协会', label=news_label, tag=1))
    return temp_list


def get_sckx_nnews(label, url, base_url=r'http://www.sckx.org.cn'):
    temp_list = []
    soup = get_selenium_head(url)
    news_list = soup.find_elements_by_class_name("center-content")[0].find_elements_by_tag_name("div")
    for one_news in news_list:
        news_title = one_news.find_elements_by_tag_name("a")[0].get_attribute("title")
        news_url = one_news.find_elements_by_tag_name("a")[0].get_attribute("href")
        # news_url = str(base_url + news_url)
        news_time = str(one_news.find_elements_by_tag_name("span")[0].text)
        news_time = re.search("\d{4}-\d{1,2}-\d{1,2}", news_time)[0]
        news_label = str(label)
        ssoup = get_selenium_head(news_url)
        try:
            news_zoom = ssoup.find_elements_by_class_name("center-content")[0]
            bs = BeautifulSoup(news_zoom.get_attribute("outerHTML"), 'lxml')
            news_img = complete_img_a(base_url, bs)
            if not news_img: news_img = None
            news_content = str(bs)
            # dict = dict_list(news_title, news_url, news_img, news_content, news_time, news_label)
            # temp_list.append(dict)
            temp_list.append(
                spider.package_data_dict(
                    title=news_title, url=news_url, img=news_img,
                    content=news_content, date=news_time,
                    source='四川省科学技术协会', label=news_label, tag=1))

        except Exception as err:
            pass
            #print("can not get " + news_url)
    return temp_list


def get_sckx():
    result_list = []
    try:
        result_list.extend(
            get_sckx_news(1, r'http://www.sckx.org.cn/views/news/list/f3951b78-4cd6-4b80-b9eb-7ec3bbe78c92/15/1.html'))
        result_list.extend(
            get_sckx_news(1, r'http://www.sckx.org.cn/views/news/list/808b4671-12ca-44a2-aa6a-1735c0c08818/15/1.html'))
        result_list.extend(
            get_sckx_news(1, r'http://www.sckx.org.cn/views/news/list/20d2facb-a3c4-4ad8-a123-78c7ae99f0a6/15/1.html'))
        result_list.extend(
            get_sckx_news(2, r'http://www.sckx.org.cn/views/news/list/889c4b11-feb5-4c5b-b8e8-2a8de65f8b07/15/1.html'))
        result_list.extend(
            get_sckx_news(3, r'http://www.sckx.org.cn/views/news/list/7a0a1f21-c650-4caa-a29f-71af96ede610/15/1.html'))
        result_list.extend(get_sckx_nnews(2,
                                          r'http://www.sckx.org.cn/views/news/list/052ca9ea-2cff-4058-bc3f-8c31c892dc84/15/1.html'))
    except Exception as err:
        pass
    finally:
        #news_to_json(result_list, "sckx.json")
        return result_list


###########################天津市科学技术协会###########################
def get_tjkx_news(label, url, base_url=r'http://www.tast.org.cn'):
    temp_list = []
    soup = get_text(url)
    if not soup:
        return temp_list
    try:
        # print(soup)
        news_list = soup.find_all("td", class_="weiruan16 hanggao35")[0].select("tr")
        print(len(news_list))
    except:
        news_list = []
    for one_news in news_list:
        news_title = one_news.select("td")[1].select("a")[0].text
        print(news_title)
        news_url = one_news.select("td")[1].select("a")[0]["href"]
        # news_url = str(base_url + news_url)
        news_time = str(one_news.select("td")[2].text)
        news_time = re.search("\d{4}/\d{1,2}/\d{1,2}", news_time)[0]
        news_time = datetime.datetime.strptime(news_time, '%Y/%m/%d').date()
        news_time = str(news_time.strftime("%Y-%m-%d"))
        news_label = str(label)
        ssoup = get_text(news_url)
        news_zoom = ssoup.find_all("td", class_="weiruan16 hanggao35")[0]
        # bs = BeautifulSoup(news_zoom.get_attribute("outerHTML"), 'lxml')
        news_img = complete_img_a(base_url, news_zoom)
        print(news_img)
        if not news_img: news_img = None
        news_content = str(news_zoom)
        # dict = dict_list(news_title, news_url, news_img, news_content, news_time, news_label)
        # temp_list.append(dict)
        temp_list.append(
            spider.package_data_dict(
                title=news_title, url=news_url, img=news_img,
                content=news_content, date=news_time,
                source='天津市科学技术协会', label=news_label, tag=1))

    return temp_list


def get_tjkx():
    result_list = []
    try:
        result_list.extend(get_tjkx_news(1, r'http://www.tast.org.cn/tzgg/'))
        result_list.extend(get_tjkx_news(1, r'http://www.tast.org.cn/kxyw/'))
        result_list.extend(get_tjkx_news(1, r'http://www.tast.org.cn/gzdt/'))
        result_list.extend(get_tjkx_news(2, r'http://www.tast.org.cn/qjkx/'))
        result_list.extend(get_tjkx_news(3, r'http://www.tast.org.cn/sjxh/'))
        result_list.extend(get_tjkx_news(2, r'http://www.tast.org.cn/jckx/'))
    except Exception as err:
        pass
    finally:
        #news_to_json(result_list, "tjkx.json")
        return result_list


###########################西藏自治区科学技术协会###########################
def get_xzkx_news(label, url, base_url=r'http://kjg.cdstm.cn'):
    temp_list = []
    soup = get_text(url)
    if not soup:
        return temp_list
    try:
        # print(soup)
        news_list = soup.find_all("div", id="xzkx_cont")[0].select("h3")
    except :
        news_list = []
    for one_news in news_list:
        news_title = one_news.select("a")[0].text
        news_url = one_news.select("a")[0]["href"]
        news_url = str(base_url + news_url)
        news_time = str(one_news.select("span")[0].text)
        news_time = re.search("\d{4}-\d{1,2}-\d{1,2}", news_time)[0]
        news_label = str(label)
        ssoup = get_text(news_url)
        if ssoup:
            news_zoom = ssoup.find_all("div", class_="cont")[0]
        else:
            news_zoom = None
        # bs = BeautifulSoup(news_zoom.get_attribute("outerHTML"), 'lxml')
        news_img = complete_img_a(base_url, news_zoom)
        if not news_img: news_img = None
        news_content = str(news_zoom)
        # dict = dict_list(news_title, news_url, news_img, news_content, news_time, news_label)
        # temp_list.append(dict)
        temp_list.append(
            spider.package_data_dict(
                title=news_title, url=news_url, img=news_img,
                content=news_content, date=news_time,
                source='西藏自治区科学技术协会', label=news_label, tag=1))
    return temp_list


def get_xzkx():
    result_list = []
    try:
        result_list.extend(get_xzkx_news(1,
                                         r'http://kjg.cdstm.cn/index.php?m=Index&a=showpage&wsid=39&pagename=newslist&channel=bull'))
        result_list.extend(get_xzkx_news(1,
                                         r'http://kjg.cdstm.cn/index.php?m=Index&a=showpage&wsid=39&pagename=newslist&channel=kjxw&cid=31'))
        result_list.extend(get_xzkx_news(2,
                                         r'http://kjg.cdstm.cn/index.php?m=Index&a=showpage&wsid=39&pagename=newslist&channel=gzdt&cid=4'))
        result_list.extend(get_xzkx_news(3,
                                         r'http://kjg.cdstm.cn/index.php?m=Index&a=showpage&wsid=39&pagename=newslist&channel=xhxs&cid=23'))
    except Exception as err:
        pass
    finally:
        #news_to_json(result_list, "xzkx.json")
        return result_list


###########################新疆生产建设兵团科学技术协会###########################
def get_xjbtkx_news(label, url, base_url=r'http://kjj.xjbt.gov.cn'):
    temp_list = []
    soup = get_text(url)
    if not soup:
        return temp_list
    try:
        news_list = soup.find_all("div", class_="article")
    except:news_list = []
    for one_news in news_list:
        news_title = one_news.select("a")[0].text
        news_url = one_news.select("a")[0]["href"]
        news_url = str(base_url + news_url)
        news_time = str(one_news.select("div>div")[1].text)
        news_time = re.search("\d{4}-\d{1,2}-\d{1,2}", news_time)[0]
        # news_time = datetime.datetime.strptime(news_time, '%Y/%m/%d').date()
        # news_time = str(news_time.strftime("%Y-%m-%d"))
        news_label = str(label)
        ssoup = get_text(news_url)
        if ssoup:
            news_zoom = ssoup.find_all("div", class_="content")[0]
        else:
            news_zoom = None
        # bs = BeautifulSoup(news_zoom.get_attribute("outerHTML"), 'lxml')
        news_img = complete_img_a(base_url, news_zoom)
        if not news_img: news_img = None
        news_content = str(news_zoom)
        # dict = dict_list(news_title, news_url, news_img, news_content, news_time, news_label)
        # temp_list.append(dict)
        temp_list.append(
            spider.package_data_dict(
                title=news_title, url=news_url, img=news_img,
                content=news_content, date=news_time,
                source='新疆生产建设兵团科学技术协会', label=news_label, tag=1))

    return temp_list


def get_xjbtkx():
    result_list = []
    try:
        result_list.extend(get_xjbtkx_news(1, r'http://kjj.xjbt.gov.cn/xwzx/kjxw/'))
        result_list.extend(get_xjbtkx_news(2, r'http://kjj.xjbt.gov.cn/xxgk/gzdt/'))
        result_list.extend(get_xjbtkx_news(3, r'http://kjj.xjbt.gov.cn/kjgl/kxpj/'))
        result_list.extend(get_xjbtkx_news(1, r'http://kjj.xjbt.gov.cn/xxgk/'))
    except Exception as err:
        pass
    finally:
        #news_to_json(result_list, "xjbtkx.json")
        return result_list


###########################新疆维吾尔自治区科学技术协会###########################
def get_xjkx_news(label, url, base_url=r'https://www.xast.org.cn/'):
    temp_list = []
    soup = get_text(url)
    if not soup:
        return temp_list
    # print(soup)
    try:
        news_list = soup.find_all("div", class_="main-page")[0].select("li")
    except:
        news_list = []
    for one_news in news_list:
        news_title = one_news.select("a")[1]["title"]
        news_url = one_news.select("a")[1]["href"]
        if [news_url][0] == ".":
            news_url = one_news.select("a")[1]["href"][2:]
        # news_url = re.search(r"/.*", news_url)[0]
        news_url = str(base_url + news_url)
        news_time = str(one_news.select("span")[0].text).strip()
        # news_time = datetime.datetime.strptime(news_time, '%Y/%m/%d').date()
        # news_time = str(news_time.strftime("%Y-%m-%d"))
        news_label = str(label)
        try:
            ssoup = get_text(news_url)
            news_zoom = ssoup.find_all("div", id="vsb_content_2")[0]
            # bs = BeautifulSoup(news_zoom.get_attribute("outerHTML"), 'lxml')
            news_img = complete_img_a(base_url, news_zoom)
            if not news_img: news_img = None
            news_content = str(news_zoom)
            # dict = dict_list(news_title, news_url, news_img, news_content, news_time, news_label)
            # temp_list.append(dict)
            temp_list.append(
                spider.package_data_dict(
                    title=news_title, url=news_url, img=news_img,
                    content=news_content, date=news_time,
                    source='新疆维吾尔自治区科学技术协会', label=news_label, tag=1))

        except Exception as err:
            pass
            #print("can not get " + news_url)
    return temp_list


def get_xjkx():
    result_list = []
    try:
        result_list.extend(get_xjkx_news(1, r'https://www.xast.org.cn/xwdt/ywkx.htm'))
        result_list.extend(get_xjkx_news(1, r'https://www.xast.org.cn/xwdt/kxtt.htm'))
        result_list.extend(get_xjkx_news(3, r'https://www.xast.org.cn/xwdt/jzfp.htm'))
        result_list.extend(get_xjkx_news(1, r'https://www.xast.org.cn/tzgg.htm'))
        result_list.extend(get_xjkx_news(2, r'https://www.xast.org.cn/index/dfdt.htm'))
        result_list.extend(get_xjkx_news(2, r'https://www.xast.org.cn/xwdt/jczx.htm'))
    except Exception as err:
        pass
    finally:
        #news_to_json(result_list, "xjkx.json")
        return result_list


###########################云南省科学技术协会###########################
def get_ynkx_news(label, url, base_url=r'http://www.yunast.cn'):
    temp_list = []
    soup = get_text(url)
    if not soup:
        return temp_list
    # print(soup)
    try:
        news_list = soup.find_all("div", class_="content")[0].select("tr")
    except:
        news_list = []
    for one_news in news_list:
        news_title = one_news.select("a")[0]["title"]
        news_url = one_news.select("a")[0]["href"]
        # if[news_url][0] == ".":
        #     news_url = one_news.select("a")[1]["href"][2:]
        # news_url = re.search(r"/.*", news_url)[0]
        news_url = str(base_url + news_url)
        news_time = str(one_news.select("td>span")[0].text).strip()
        news_time = re.search("\d{4}.\d{1,2}.\d{1,2}", news_time)[0]
        news_time = datetime.datetime.strptime(news_time, '%Y.%m.%d').date()
        news_time = str(news_time.strftime("%Y-%m-%d"))
        news_label = str(label)
        # try:
        ssoup = get_text(news_url)
        if ssoup:

            news_zoom = ssoup.find_all("div", class_="content")[0].select("p")
        else:
            news_zoom = []
        t_zoom = ""
        for a_zoom in news_zoom:
            if not a_zoom.select("span"):
                t_zoom = t_zoom + str(a_zoom)
        news_zoom = t_zoom
        bs = BeautifulSoup(news_zoom, 'lxml')
        news_img = complete_img_a(base_url, bs)
        if not news_img: news_img = None
        news_content = str(bs)
        # dict = dict_list(news_title, news_url, news_img, news_content, news_time, news_label)
        # temp_list.append(dict)
        temp_list.append(
            spider.package_data_dict(
                title=news_title, url=news_url, img=news_img,
                content=news_content, date=news_time,
                source='云南省科学技术协会', label=news_label, tag=1))

    return temp_list


def get_ynkx():
    result_list = []
    try:
        result_list.extend(get_ynkx_news(1, r'http://www.yunast.cn/site/yunast/tbbd/index.html'))
        result_list.extend(get_ynkx_news(1, r'http://www.yunast.cn/site/yunast/sjdt/index.html'))
        result_list.extend(get_ynkx_news(3, r'http://www.yunast.cn/site/yunast/xhhd/index.html'))
        result_list.extend(get_ynkx_news(1, r'http://www.yunast.cn/site/yunast/tzgg/index.html'))
        result_list.extend(get_ynkx_news(2, r'http://www.yunast.cn/site/yunast/kxywjczx/index.html'))
        result_list.extend(get_ynkx_news(2, r'http://www.yunast.cn/site/yunast/qsnkp/index.html'))
    except Exception as err:
        pass
    finally:
        #news_to_json(result_list, "ynkx.json")
        return result_list


###########################浙江省科学技术协会###########################
def get_zjkx_news(label, url, base_url=r'http://www.zast.org.cn/'):
    temp_list = []
    try:
        soup = get_selenium_head(url)
        news_list = soup.find_elements_by_class_name("rate-list-text")
        for one_news in news_list:
            news_title = one_news.find_elements_by_class_name("text-title")[0].find_elements_by_tag_name("p")[0].text
            news_url = one_news.find_elements_by_class_name("text-title")[0].get_attribute("href")
            news_label = str(label)
            try:
                ssoup = get_selenium_head(news_url)
                # print(ssoup.page_source)
                news_time = re.search("\d{4}-\d{1,2}-\d{1,2}", str(ssoup.page_source))[0]
                news_zoom = ssoup.find_elements_by_class_name("mian-text")[0]
                bs = BeautifulSoup(news_zoom.get_attribute("outerHTML"), 'lxml')
                news_img = complete_img_a(base_url, bs)
                if not news_img: news_img = None
                news_content = str(bs)
                # dict = dict_list(news_title, news_url, news_img, news_content, news_time, news_label)
                # temp_list.append(dict)
                temp_list.append(
                    spider.package_data_dict(
                        title=news_title, url=news_url, img=news_img,
                        content=news_content, date=news_time,
                        source='浙江省科学技术协会', label=news_label, tag=1))
            except Exception as err:
                pass
            finally:
                ssoup.quit()

    except Exception as err:
        pass
    finally:
        soup.quit()
        return temp_list


def get_zjkx():
    result_list = []
    try:
        result_list.extend(get_zjkx_news(1, r'http://www.zast.org.cn/col/col1673860/index.html'))
        result_list.extend(get_zjkx_news(1, r'http://www.zast.org.cn/col/col1673861/index.html'))
        result_list.extend(get_zjkx_news(1, r'http://www.zast.org.cn/col/col1673857/index.html'))
        result_list.extend(get_zjkx_news(2, r'http://www.zast.org.cn/col/col1674356/index.html'))
        result_list.extend(get_zjkx_news(3, r'http://www.zast.org.cn/col/col1673858/index.html'))
        result_list.extend(get_zjkx_news(2, r'http://www.zast.org.cn/col/col1673839/index.html'))
    except Exception as err:
        pass
    finally:
        #news_to_json(result_list, "zjkx.json")
        return result_list


###########################重庆市科学技术协会###########################
def get_cqkx_news(label, url, base_url=r'http://www.tast.org.cn'):
    temp_list = []
    soup = get_text(url)
    if not soup:
        return temp_list

    # print(soup)
    try:
        news_list = soup.find_all("div", class_="ty_list_1")[0].select("li")
        for one_news in news_list:
            news_title = one_news.select("a")[0].text.strip()
            news_url = one_news.select("a")[0]["href"]
            # news_url = str(base_url + news_url)
            news_time = str(one_news.select("span")[0].text)
            news_label = str(label)
            ssoup = get_text(news_url)
            news_zoom = ssoup.find_all("div", class_="news_text_content")[0]
            # bs = BeautifulSoup(news_zoom.get_attribute("outerHTML"), 'lxml')
            news_img = complete_img_a(base_url, news_zoom)
            if not news_img: news_img = None
            news_content = str(news_zoom)
            temp_list.append(
                spider.package_data_dict(
                    title=news_title, url=news_url, img=news_img,
                    content=news_content, date=news_time,
                    source='重庆市科学技术协会', label=news_label, tag=1))
    except Exception as err:
        pass
       # print("can not get " + url)
    return temp_list


def get_cqkx_nnews(label, url, base_url=r'http://www.tast.org.cn'):
    temp_list = []
    soup = get_text(url)
    if not  soup:
        return temp_list
    try:
        # print(soup)
        news_list = soup.find_all("div", class_="ty_list clearfix")
    except:
        news_list = []
    for one_news in news_list:
        news_title = one_news.select("h1>a")[0]["title"]
        news_url = one_news.select("h1>a")[0]["href"]
        # news_url = str(base_url + news_url)
        news_time = str(one_news.select("div>div")[1].select("div")[0].text)
        news_time = re.search("\d{4}-\d{1,2}-\d{1,2}", news_time)[0]
        news_label = str(label)
        ssoup = get_text(news_url)
        try:
            news_zoom = ssoup.find_all("div", class_="news_text_content")[0]
            # bs = BeautifulSoup(news_zoom.get_attribute("outerHTML"), 'lxml')
            news_img = complete_img_a(base_url, news_zoom)
            if not news_img: news_img = None
            news_content = str(news_zoom)

            temp_list.append(
                spider.package_data_dict(
                    title=news_title, url=news_url, img=news_img,
                    content=news_content, date=news_time,
                    source='重庆市科学技术协会', label=news_label, tag=1))
        except Exception as err:
            pass
            #print("can not get " + news_url)
    return temp_list


def get_cqkx():
    result_list = []
    try:
        result_list.extend(get_cqkx_news(1, r'http://www.cqast.cn/htm/col374603.htm'))  #
        result_list.extend(get_cqkx_news(1, r'http://www.cqast.cn/htm/col374855.htm'))  #
        result_list.extend(get_cqkx_nnews(1, r'http://www.cqast.cn/htm/col374594.htm'))
        result_list.extend(get_cqkx_nnews(2, r'http://www.cqast.cn/htm/col374595.htm'))
        result_list.extend(get_cqkx_nnews(3, r'http://www.cqast.cn/htm/col374596.htm'))
        result_list.extend(get_cqkx_nnews(2, r'http://www.cqast.cn/htm/col374627.htm'))
    except Exception as err:
        pass
    finally:
        #news_to_json(result_list, "cqkx.json")
        return result_list

##############################爬虫数据入库######################################
def spider_data_into_mysql(news_list):
    if news_list:
        for one_news in news_list:
            news = DFKX(**one_news)
            try:
                news.save()
                print('Successful')
            except Exception as e:
                #pass
                print(e)


def start_dfkx_spider():
    try:
        #安徽  测试完毕
        spider_data_into_mysql(get_ahkx())
        #福建  测试完毕
        spider_data_into_mysql(get_fjkx())
        #甘肃   测试完毕
        spider_data_into_mysql(get_gskx())
        #广东   测试完毕
        spider_data_into_mysql(get_gdkx())
        #广西  测试完毕
        spider_data_into_mysql(get_gxkx())
        #贵州  测试完毕
        spider_data_into_mysql(get_gzkx())
        #海南  测试完毕
        spider_data_into_mysql(get_hnkx())
        #河北  测试完毕
        spider_data_into_mysql(get_hbkx())
        #河南   测试完毕
        spider_data_into_mysql(get_henankx())
        #黑龙江  测试完毕
        spider_data_into_mysql(get_hljkx())
        #湖北   测试完毕
        spider_data_into_mysql(get_hubeikx())
        #湖南   测试完毕
        spider_data_into_mysql(get_hunankx())
        #吉林   测试完毕
        spider_data_into_mysql(get_jlkx())
        #江苏 测试完毕
        spider_data_into_mysql(get_jskx())
        #江西 数据库有
        spider_data_into_mysql(get_jxkx())
        #辽宁  数据库有
        spider_data_into_mysql(get_lnkx())
        #内蒙古 数据库有
        spider_data_into_mysql(get_nmgkx())
        #宁夏 数据库有
        spider_data_into_mysql(get_nxkx())
        #青海  出错  数据库无
        spider_data_into_mysql(get_qhkx())
        # 山东  出错  数据库无
        spider_data_into_mysql(get_sdkx())
        # 山西 出错  数据库无
        spider_data_into_mysql(get_sxkx())
        #陕西 出错  地址错误
        spider_data_into_mysql(get_shanxikx())
        #上海 出错  异常出错
        spider_data_into_mysql(get_shkx())
        #四川 出错  数据库无
        spider_data_into_mysql(get_sckx())
        #天津  出错
        spider_data_into_mysql(get_tjkx())
        # #西藏 出错
        spider_data_into_mysql(get_xzkx())
        #新疆 维吾尔  出错
        spider_data_into_mysql(get_xjkx())
        #新疆兵团  出错
        spider_data_into_mysql(get_xjbtkx())
        #云南科协  出错
        spider_data_into_mysql(get_ynkx())
        #浙江  出错
        spider_data_into_mysql(get_zjkx())
        #重庆 出错
        spider_data_into_mysql(get_cqkx())
        # 北京科协
        spider_data_into_mysql(get_bjkx())
    except Exception as e:
        print(e)
