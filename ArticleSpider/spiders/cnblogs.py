import json
import re
from urllib import parse

import scrapy
from scrapy import Request


class CnblogsSpider(scrapy.Spider):
    name = 'cnblogs'
    allowed_domains = ['news.cnblogs.com']
    start_urls = ['https://news.cnblogs.com/']

    def parse(self, response):
        """
        1,获取列表页中详情页url并交给scrapy进行下载后调用相应的解析方法
        2，获取下一页url并交给scrapy进行下载，下载完后交给parse继续跟进
        :param response:
        :return:
        """
        # urls = response.css("div#news_list h2 a::attr(href)").extract()
        # 获取post块，以便爬取详情页中无法获取的元素，另外可以使用css选择器或者xpath从post块中获取url
        post_nodes = response.css("div#news_list .news_block")[:1]
        for post_node in post_nodes:
            image_url = post_node.css(".entry_summary a img::attr(src)").extract_first("")
            post_url = post_node.css("h2 a::attr(href)").extract_first("")
            yield Request(url=parse.urljoin(response.url, post_url), meta={"front_image_url": image_url},
                          callback=self.parse_detail)

        # 提取下一页url并交给parse继续处理
        """
        next_text = response.css(".pager a:last-child::text").extract_first("")
        if next_text == "Next >":
            next_url = response.css(".pager a:last-child::attr(href)").extract_first("")
            yield Request(url=parse.urljoin(response.url, next_url), callback=self.parse)
        """
        # 获取下一页列表(调试的时候注释掉)
        # next_url = response.xpath("//a[contains(text(),'Next >')]/@href").extract_first("")
        # yield Request(url=parse.urljoin(response.url, next_url), callback=self.parse)
        pass

    def parse_detail(self, response):
        """
        解析详情页
        :param response:
        :return:
        """

        match_re = re.match(".*?(\d+)", response.url)
        # 为了防止列表页url出现不符合规范url格式出错，所以将元素的提取全部放入if中
        if match_re:
            title = response.css("#news_title a::text").extract_first("")
            create_data = response.css("#news_info .time::text").extract_first("")
            content = response.css("#news_body").extract()[0]
            tag_list = response.css(".news_tags a::text").extract()
            tags = ','.join(tag_list)
            post_id = match_re.group(1)
            # html = requests.get(
            #     url=parse.urljoin(response.url, "/NewsAjax/GetAjaxNewsInfo?contentId={}".format(post_id)))
            # j_data = json.loads(html.text)
            # praise_nums = j_data["DiggCount"]
            # view_nums = j_data["TotalView"]
            # comment_nums = j_data["CommentCount"]
            yield Request(url=parse.urljoin(response.url, "/NewsAjax/GetAjaxNewsInfo?contentId={}".format(post_id)),
                          callback=self.parse_num)

    pass

    def parse_num(self, response):
        j_data = json.loads(response.text)
        praise_nums = j_data["DiggCount"]
        view_nums = j_data["TotalView"]
        comment_nums = j_data["CommentCount"]

    pass