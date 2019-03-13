# -*- coding: utf-8 -*-
import re
import scrapy
from scrapy.http import Request
from urllib import parse
from scrapy.xlib.pydispatch import dispatcher
from scrapy import signals
from items import JobBoleArticleItem, ArticleItem, ArticleItemLoader
from utils.common import get_md5
import json
import os


class JobboleSpider(scrapy.Spider):
    name = 'jobbole'
    dir_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    INPUT = os.path.join(dir_path, 'input.json')
    with open(INPUT) as f:
        data = json.load(f)
    allowed_domains = ['blog.jobbole.com']
    start_urls = data['urls']

    def __init__(self, **kwargs):
        object.__init__(self)
        self.fail_urls = []
        dispatcher.connect(self.handle_spider_closed, signals.spider_closed)

    def handle_spider_closed(self, spider, reason):
        self.crawler.stats.set_value("failed_urls", ",".join(self.fail_urls))


    # get urls from index page
    def parse(self, response):
        """
        1. get the urls from index page, callback parse details
        2. get the url of next index page and callback parse
        """
        # 1.
        # handle invalid status
        if response.status == 404:
            self.fail_urls.append(response.url)
            self.crawler.stats.inc_value("failed_url")

        # get the node
        post_nodes = response.css("#archive .floated-thumb .post-thumb a")
        for post_node in post_nodes:
            # get url of img, in src attribute
            image_url = post_node.css("img::attr(src)").extract_first("")
            # get url of article, in href attribute
            post_url = post_node.css("::attr(href)").extract_first("")
            # combine the domain and url, pass the Response to parse_detail, it is an asynchronous function
            # meta is an attribute in Response
            request = None
            dir_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
            INPUT = os.path.join(dir_path, 'input.json')
            with open(INPUT) as f:
                data = json.load(f)
            include_rules = data["rules"]["include"]
            for rule in include_rules:
                matchObj = re.match(rule, post_url)
                if matchObj:
                    request = True
            exclude_rules = data["rules"]["exclude"]
            for rule in exclude_rules:
                if re.match(rule, post_url):
                    request = False
            if request is None:
                print("parse wrong")
                return
            if request == True:
                yield Request(url=parse.urljoin(response.url, post_url), meta={"front_image_url":image_url}, callback=self.parse_detail)

        # 2.get the url of next page
        next_url = response.css(".next.page-numbers::attr(href)").extract_first("")
        # if it has next page, callback parse
        if next_url:
            yield Request(url=parse.urljoin(response.url, next_url), callback=self.parse)

    # get key information from article
    def parse_detail(self, response):
        article_item = ArticleItem()

        # put items in itemloader
        front_image_url = response.meta.get("front_image_url", "")  # image url
        item_loader = ArticleItemLoader(item=JobBoleArticleItem(), response=response)
        item_loader.add_css("title", ".entry-header h1::text")
        item_loader.add_value("url", response.url)
        item_loader.add_value("url_object_id", get_md5(response.url))
        item_loader.add_css("create_date", "p.entry-meta-hide-on-mobile::text")
        item_loader.add_value("front_image_url", [front_image_url])
        item_loader.add_css("praise_nums", ".vote-post-up h10::text")
        item_loader.add_css("comment_nums", "a[href='#article-comment'] span::text")
        item_loader.add_css("fav_nums", ".bookmark-btn::text")
        item_loader.add_css("tags", "p.entry-meta-hide-on-mobile a::text")
        item_loader.add_css("content", "div.entry")
        # item_loader.add_value("textExtraction", ["hahaha"])

        dir_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        INPUT = os.path.join(dir_path, 'input.json')
        with open(INPUT) as f:
            data = json.load(f)
        # Selects all elements in the document
        content = response.xpath("//*").extract()[0]
        regex_str = "<[^>]+>"
        # keep the content, get rid of tags
        text = re.sub(regex_str, '', content)
        # break into lines and remove leading and trailing space on each (with multiple blank lines now)
        lines = (line.strip() for line in text.splitlines())
        # break multi-headlines into a line each
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        # remove blank lines
        textNoSpace = '\n'.join(chunk for chunk in chunks if chunk)

        # for "textextraction" requirement
        textextraction = data["rules"]["textextraction"]
        textExtraction = []
        for rule in textextraction:
            # concatenate results if fit regular expression rules
            textExtraction += re.findall(rule, textNoSpace)
        # join the result with ','
        item_loader.add_value("textExtraction", [','.join(textExtraction)])
        article_item = item_loader.load_item()
        yield article_item