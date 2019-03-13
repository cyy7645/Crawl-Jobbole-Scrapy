# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

# avoid spelling mistake, and pass items to pipeline automatically
import scrapy
import re
import datetime
from scrapy.loader.processors import MapCompose, TakeFirst, Join
from scrapy.loader import ItemLoader



# crete fields for attributes
class ArticleItem(scrapy.Item):
    title = scrapy.Field()
    create_date = scrapy.Field()
    url = scrapy.Field()
    front_image_url = scrapy.Field()
    # front_image_path = scrapy.Field()
    praise_nums = scrapy.Field()
    comment_nums = scrapy.Field()
    tags = scrapy.Field()
    url_object_id = scrapy.Field()
    fav_nums = scrapy.Field()
    content = scrapy.Field()
    textExtraction = scrapy.Field()

# convert the form of datatime
def date_convert(value):
    try:
        create_date = datetime.datetime.strptime(value, "%Y/%m/%d").date()
    # get current date
    except Exception as e:
        create_date = datetime.datetime.now().date()

    return create_date


# get numbers from string
def get_nums(value):
    match_re = re.match(".*?(\d+).*", value)
    if match_re:
        nums = int(match_re.group(1))
    else:
        nums = 0

    return nums


# remove 评论 from tag
def remove_comment_tags(value):
    if "评论" in value:
        return ""
    else:
        return value


def return_value(value):
    return value


class ArticleItemLoader(ItemLoader):
    # define itemloader by myself
    default_output_processor = TakeFirst()


# define the fields for my items, process them
class JobBoleArticleItem(scrapy.Item):
    title = scrapy.Field()
    create_date = scrapy.Field(
        # input_processor for preprocessing item
        input_processor=MapCompose(date_convert),
    )
    url = scrapy.Field()
    url_object_id = scrapy.Field()
    front_image_url = scrapy.Field(
        output_processor=MapCompose(return_value)
    )
    front_image_path = scrapy.Field()
    praise_nums = scrapy.Field(
        input_processor=MapCompose(get_nums)
    )
    comment_nums = scrapy.Field(
        input_processor=MapCompose(get_nums)
    )
    fav_nums = scrapy.Field(
        input_processor=MapCompose(get_nums)
    )
    tags = scrapy.Field(
        input_processor=MapCompose(remove_comment_tags),
        # output_processor for processing items, concatenate
        output_processor=Join(",")
    )
    content = scrapy.Field()
    textExtraction = scrapy.Field(
        output_processor=MapCompose(return_value)
    )


    # define insert process, will be called in pipeline
    def get_insert_sql(self):
        insert_sql = """
            insert into jobbole_article(title, url, create_date, fav_nums, front_image_url, praise_nums, comment_nums, tags, url_object_id, content, textExtraction)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE content=VALUES(fav_nums)
        """
        params = (self["title"], self["url"], self["create_date"], self["fav_nums"],  self["front_image_url"], self["praise_nums"], self["comment_nums"], self["tags"], self["url_object_id"], self["content"], self["textExtraction"])

        return insert_sql, params