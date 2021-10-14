import logging
from logging import FileHandler
from logging import Formatter
import os
import scrapy
import w3lib.html


folders_to_create = ['log']
for folder in folders_to_create:  # creating all standard folders if they don't exist already
    if not os.path.exists(folder):
        os.makedirs(folder)

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[logging.FileHandler(filename='log/operational.log',
                                                  mode='a', encoding='utf-8')])

parsing_logger = logging.getLogger("parser")
parsing_logger.setLevel(logging.DEBUG)
parsing_logger_file_handler = FileHandler('log/parsed_output.log', encoding='utf-8')
parsing_logger_file_handler.setLevel(logging.DEBUG)
parsing_logger_file_handler.setFormatter(Formatter('%(asctime)s - %(levelname)s - %(message)s'))
parsing_logger.addHandler(parsing_logger_file_handler)


class DTEKSpider(scrapy.Spider):
    """Scrapy class that parses DTEK site"""

    name = 'dtek_parser'
    base_url = 'https://www.dtek-krem.com.ua'

    AREAS = ['Бориспільський']          # todo fill with all areas ["Район1", "Район2", ...]
    LOCATIONS = ['Петропавлівське']     # todo fill with all locations

    # url_tails = [
    #     '/ru/outages?query=%D0%BF%D0%B5%D1%82%D1%80%D0%BE%D0%BF%D0%B0%D0%B2%D0%BB%D1%96%D0%B2%D1%81%D1%8C%D0%BA%D0%B5&page=1&rem=%D0%91%D0%BE%D1%80%D0%B8%D1%81%D0%BF%D1%96%D0%BB%D1%8C%D1%81%D1%8C%D0%BA%D0%B8%D0%B9&type=-1&status=-1&shutdown-date=-1&inclusion-date=-1&create-date=-1'
    # ]
    start_urls = [
        f'{base_url}/ru/outages?'
        f'query={LOCATIONS[0]}'
        f'&rem={AREAS[0]}',

        # f'{base_url}/...',
        # f'{base_url}/...',
    ]

    @classmethod
    def get_user_streets(cls, all_towns_and_streets, user_town):
        all_towns_and_streets = all_towns_and_streets.split('\n')
        found_town_and_streets = ''
        for town in all_towns_and_streets:
            if user_town in town:
                found_town_and_streets = town.strip()
                break
        if not found_town_and_streets:
            logging.info('Error, no user location in results')
        return found_town_and_streets

    def parse(self, response):
        user_town = self.LOCATIONS[0]
        user_area = self.AREAS[0]
        rows = response.xpath("//tr['data-id'][position()>1]")
        for row in rows:
            towns = row.xpath('td//b/text()')        # type -> Selector
            list_of_towns = [loc.get() for loc in towns]
            if user_town not in list_of_towns:
                logging.info('Error, no user location in results')

            cols = row.xpath('td')

            outage_date, turn_on_date, area, all_towns_and_streets, works_type, posting_date, outage_time, status = \
                [w3lib.html.remove_tags(col.get()).strip() for col in cols]

            streets = self.get_user_streets(all_towns_and_streets, user_town)

            output_string = f'По данным ДТЭК {outage_date} {outage_time} будут проводиться: {works_type} ' \
                            f'в локациях: {streets}. (Размещено {posting_date}) Cтатус: {status}'
            parsing_logger.info(output_string)
            # with open('log/parsed_output.log', 'a', encoding='utf-8') as f:
            #     f.write(output_string + "\n")
