from dtek_parser.spiders.dtek_parser import DTEKSpider
import os
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from scrapy.utils.project import get_project_settings

settings = get_project_settings()

process = CrawlerProcess(settings)
process.crawl(DTEKSpider)
# process.crawl(MySpider2)
process.start()
