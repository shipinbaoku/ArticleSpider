import base64
import datetime
import json
import re
import time
from urllib import parse

import scrapy
from PIL import Image
from mouse import move, click
from scrapy.loader import ItemLoader
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys

from ArticleSpider.items import ZhihuQuestionItem, ZhihuAnswerItem
from utils.user_login_info import ZhihuLogin, ttshitu


class ZhihuSpider(scrapy.Spider):
    name = 'zhihu'
    allowed_domains = ['www.zhihu.com']
    start_urls = ['https://www.zhihu.com/']
    login_success = False
    headers = {
        "HOST": "www.zhihu.com",
        "Referer": "https://www.zhizhu.com",
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.75 Safari/537.36"
    }
    custom_settings = {
        "COOKIES_ENABLED": True,
        'REDIRECT_ENABLED': False,
        "DOWNLOAD_DELAY": 5
    }

    # question的第一页answer的请求url
    start_answer_url = "https://www.zhihu.com/api/v4/questions/{0}/answers?include=data%5B%2A%5D.is_normal%2Cadmin_closed_comment%2Creward_info%2Cis_collapsed%2Cannotation_action%2Cannotation_detail%2Ccollapse_reason%2Cis_sticky%2Ccollapsed_by%2Csuggest_edit%2Ccomment_count%2Ccan_comment%2Ccontent%2Ceditable_content%2Cvoteup_count%2Creshipment_settings%2Ccomment_permission%2Ccreated_time%2Cupdated_time%2Creview_info%2Crelevant_info%2Cquestion%2Cexcerpt%2Crelationship.is_authorized%2Cis_author%2Cvoting%2Cis_thanked%2Cis_nothelp%2Cis_labeled%2Cis_recognized%2Cpaid_info%2Cpaid_info_content%3Bdata%5B%2A%5D.mark_infos%5B%2A%5D.url%3Bdata%5B%2A%5D.author.follower_count%2Cbadge%5B%2A%5D.topics&limit={1}&offset={2}&platform=desktop&sort_by=default"

    def parse(self, response):
        """
        提取出html页面中的所有url，并跟踪这些url进一步爬取
        如果提取出的url中格式为/question/xxx 就下载，之后进入解析函数
        :param response:
        :return:
        """
        all_urls = response.css("#TopstoryContent  h2 div a::attr(href)").extract()
        all_urls = [parse.urljoin(response.url, url) for url in all_urls]
        all_urls = filter(lambda x: True if x.startswith("https") else False, all_urls)
        for url in all_urls:
            match_obj = re.match("(.*zhihu.com/question/(\d+))(/|$).*", url)
            if match_obj:
                # 如果提取到question相关的页面则下载后交由提取函数进行提取
                request_url = match_obj.group(1)
                question_id = match_obj.group(2)
                yield scrapy.Request(request_url, headers=self.headers, callback=self.parse_question)
            else:
                # 如果不是question页面则直接进一步跟踪
                yield scrapy.Request(url, headers=self.headers, callback=self.parse)

    def parse_question(self, response):
        """
        处理question页面，提取出具体的question item
        :param response:
        :return:
        """
        match_obj = re.match("(.*zhihu.com/question/(\d+))(/|$).*", response.url)
        if match_obj:
            question_id = int(match_obj.group(2))

        item_loader = ItemLoader(item=ZhihuQuestionItem(), response=response)
        item_loader.add_css('title', "h1.QuestionHeader-title::text")
        item_loader.add_css("content", ".QuestionHeader-detail")
        item_loader.add_value("url", response.url)
        item_loader.add_value("zhihu_id", question_id)
        item_loader.add_css("answer_num", '.List-headerText span::text')
        item_loader.add_css("comments_num", ".QuestionHeader-Comment button::text")
        # 以下提取的是关注者和浏览数两个数据，后续入库前处理
        item_loader.add_css("watch_user_num", 'button.NumberBoard-item strong::text')
        item_loader.add_css("topics", ".QuestionHeader-topics .Popover div::text")
        question_item = item_loader.load_item()
        yield scrapy.Request(self.start_answer_url.format(question_id, 20, 0), headers=self.headers,
                             callback=self.parse_answer)
        yield question_item
        pass

    def parse_answer(self, reponse):
        # 处理question的answer
        ans_json = json.loads(reponse.text)
        is_end = ans_json["paging"]["is_end"]
        next_url = ans_json["paging"]["next"]

        # 提取answer的具体字段
        for answer in ans_json["data"]:
            answer_item = ZhihuAnswerItem()
            answer_item["zhihu_id"] = answer["id"]
            answer_item["url"] = answer["url"]
            answer_item["question_id"] = answer["question"]["id"]
            answer_item["author_id"] = answer["author"]["id"] if "id" in answer["author"] else None
            answer_item["content"] = answer["content"] if "content" in answer else None
            answer_item["parise_num"] = answer["voteup_count"]
            answer_item["comments_num"] = answer["comment_count"]
            answer_item["create_time"] = answer["created_time"]
            answer_item["update_time"] = answer["updated_time"]
            answer_item["crawl_time"] = datetime.datetime.now()

            yield answer_item

        if not is_end:
            yield scrapy.Request(next_url, headers=self.headers, callback=self.parse_answer)

    def start_requests(self):

        chrome_option = Options()
        chrome_option.add_experimental_option('debuggerAddress', '127.0.0.1:9222')
        browser = webdriver.Chrome(executable_path="E:/pythonProject/seleniumdriver/chromedriver.exe",
                                   options=chrome_option)
        browser.fullscreen_window()
        browser.get("https://www.zhihu.com/signin")
        time.sleep(5)
        try:
            browser.find_element_by_xpath('//*[@id="root"]/div/main/div/div/div[2]/div/div/div[2]/a/div[1]/div/div/div')
            self.login_success = True
            Cookies = browser.get_cookies()
            # print(Cookies)
            cookie_dict = {}
            import pickle
            for cookie in Cookies:
                # 写入文件
                # 此处大家修改一下自己文件的所在路径
                # f = open('E:/pythonProject/ArticleSpider/ArticleSpider/cookies' + cookie['name'] + '.zhihu',
                #          'wb')
                f = open('E:/pythonProject/ArticleSpider/ArticleSpider/cookies/zhihu.cookies',
                         'wb')
                pickle.dump(cookie, f)
                f.close()
                cookie_dict[cookie['name']] = cookie['value']
            # browser.close()
            # print(cookie_dict)
            return [scrapy.Request(url=self.start_urls[0], dont_filter=True, headers=self.headers, cookies=cookie_dict)]
        except:
            pass
        try:
            pass_login = browser.find_element_by_xpath(
                '//*[@id="root"]/div/main/div/div/div/div[1]/div/form/div[1]/div[2]')
            if pass_login.text == "密码登录":
                pass_login.click()
                time.sleep(5)
                browser.find_element_by_css_selector(".SignFlow-accountInput.Input-wrapper input").send_keys(
                    Keys.CONTROL + "a")
                browser.find_element_by_css_selector(".SignFlow-accountInput.Input-wrapper input").send_keys(
                    ZhihuLogin.email)
                browser.find_element_by_xpath(
                    '//*[@id="root"]/div/main/div/div/div/div[1]/div/form/div[3]/div/label/input').send_keys(
                    Keys.CONTROL + "a")
                browser.find_element_by_xpath(
                    '//*[@id="root"]/div/main/div/div/div/div[1]/div/form/div[3]/div/label/input').send_keys(
                    ZhihuLogin.psw)
                browser.find_element_by_css_selector(
                    ".Button.SignFlow-submitButton.Button--primary.Button--blue").click()
                time.sleep(3)
                while not self.login_success:
                    try:
                        browser.find_element_by_xpath(
                            '//*[@id="root"]/div/main/div/div/div[2]/div/div/div[2]/a/div[1]/div/div/div')
                        self.login_success = True
                    except:
                        pass
                    try:
                        eng_captcha_ele = browser.find_element_by_xpath(
                            '//*[@id="root"]/div/main/div/div/div/div[1]/div/form/div[4]/div/span/div/img')
                    except:
                        eng_captcha_ele = None
                    try:
                        chs_captcha_ele = browser.find_element_by_xpath(
                            '//*[@id="root"]/div/main/div/div/div/div[1]/div/form/div[4]/div/div[2]/img')
                    except:
                        chs_captcha_ele = None

                    if chs_captcha_ele:
                        chs_captcha_ele_position = chs_captcha_ele.location
                        x_relative = chs_captcha_ele_position["x"]
                        y_relative = chs_captcha_ele_position["y"]
                        base64_text = chs_captcha_ele.get_attribute("src")
                        print(base64_text)
                        # code = base64_text.replace('data:image/jpg;base64,', '')
                        code = base64_text.replace('data:image/jpg;base64,', '').replace("%0A", "")
                        fh = open("yzm_chs.jpg", "wb")
                        fh.write(base64.b64decode(code))
                        fh.close()
                        from zheye import zheye

                        zheye = zheye()
                        positions = zheye.Recognize("yzm_chs.jpg")

                        last_position = []
                        if len(positions) == 2:
                            if positions[0][1] > positions[1][1]:
                                last_position.append([positions[1][1], positions[1][0]])
                                last_position.append([positions[0][1], positions[0][0]])
                            else:
                                last_position.append([positions[0][1], positions[0][0]])
                                last_position.append([positions[1][1], positions[1][0]])
                            first_point = [int(last_position[0][0] / 2), int(last_position[0][1] / 2)]
                            second_point = [int(last_position[1][0] / 2), int(last_position[1][1] / 2)]
                            move((x_relative + first_point[0]), y_relative + first_point[1])
                            click()
                            move((x_relative + second_point[0]), y_relative + second_point[1])
                            click()
                        else:
                            last_position.append([positions[0][1], positions[0][0]])
                            first_point = [int(last_position[0][0] / 2), int(last_position[0][1] / 2)]

                            move((x_relative + first_point[0]), y_relative + first_point[1])
                            click()

                    if eng_captcha_ele:
                        # 2. 通过crop方法
                        # from pil import Image
                        # image = Image.open(path)
                        # image = image.crop((locations["x"], locations["y"], locations["x"] + image_size["width"],
                        #                     locations["y"] + image_size["height"]))  # defines crop points
                        #
                        # rgb_im = image.convert('RGB')
                        # rgb_im.save("D:/ImoocProjects/python_scrapy/coding-92/ArticleSpider/tools/image/yzm.jpeg",
                        #             'jpeg')  # saves new cropped image
                        # # 1. 通过保存base64编码
                        base64_text = eng_captcha_ele.get_attribute("src")
                        code = base64_text.replace('data:image/jpg;base64,', '').replace("%0A", "")
                        fh = open("yzm_en.jpeg", "wb")
                        fh.write(base64.b64decode(code))
                        fh.close()

                        # from tools.yundama_requests import YDMHttp
                        # yundama = YDMHttp("da_ge_da1", "dageda", 3129, "40d5ad41c047179fc797631e3b9c3025")
                        # code = yundama.decode("yzm_en.jpeg", 5000, 60)

                        from utils.common import base64_api
                        img_path = "yzm_en.jpeg"
                        img = Image.open(img_path)
                        code = base64_api(uname=ttshitu.uname, pwd=ttshitu.pwd, img=img)
                        print(code)

                        while True:
                            if code == "":
                                code = base64_api(uname='lovelilili', pwd='880125love', img=img)
                            else:
                                break
                        browser.find_element_by_xpath(
                            '//*[@id="root"]/div/main/div/div/div/div[1]/div/form/div[4]/div/div/label/input').send_keys(
                            Keys.CONTROL + "a")
                        browser.find_element_by_xpath(
                            '//*[@id="root"]/div/main/div/div/div/div[1]/div/form/div[4]/div/div/label/input').send_keys(
                            code)

                    # 输入账号密码
                    browser.find_element_by_css_selector(".SignFlow-accountInput.Input-wrapper input").send_keys(
                        Keys.CONTROL + "a")
                    browser.find_element_by_css_selector(".SignFlow-accountInput.Input-wrapper input").send_keys(
                        ZhihuLogin.email)
                    browser.find_element_by_xpath(
                        '//*[@id="root"]/div/main/div/div/div/div[1]/div/form/div[3]/div/label/input').send_keys(
                        Keys.CONTROL + "a")
                    browser.find_element_by_xpath(
                        '//*[@id="root"]/div/main/div/div/div/div[1]/div/form/div[3]/div/label/input').send_keys(
                        ZhihuLogin.psw)
                    browser.find_element_by_css_selector(
                        ".Button.SignFlow-submitButton.Button--primary.Button--blue").click()
                    time.sleep(3)
                    try:
                        browser.find_element_by_xpath(
                            '//*[@id="root"]/div/main/div/div/div[2]/div/div/div[2]/a/div[1]/div/div/div')
                        self.login_success = True
                        Cookies = browser.get_cookies()
                        print(Cookies)
                        cookie_dict = {}
                        import pickle
                        for cookie in Cookies:
                            # 写入文件
                            # 此处大家修改一下自己文件的所在路径
                            f = open('E:/pythonProject/ArticleSpider/ArticleSpider/cookies/zhihu.cookies',
                                     'wb')
                            pickle.dump(cookie, f)
                            f.close()
                            cookie_dict[cookie['name']] = cookie['value']
                        # browser.close()
                        return [scrapy.Request(url=self.start_urls[0], dont_filter=True, headers=self.headers,
                                               cookies=cookie_dict)]
                    except:
                        pass
        except:
            pass
