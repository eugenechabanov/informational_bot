# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from dataclasses import dataclass


@dataclass
class DtekParserItem:
    outage_date: str
    turn_on_date: str
    area: str
    all_towns_and_streets: str
    works_type: str
    posting_date: str
    outage_schedule: str
    status: str
    #     outage_date = scrapy.Field()
    #     turn_on_date = scrapy.Field()
    #     area = scrapy.Field()
    #     all_towns_and_streets = scrapy.Field()
    #     works_type = scrapy.Field()
    #     posting_date = scrapy.Field()
    #     outage_schedule = scrapy.Field()
    #     status = scrapy.Field()
