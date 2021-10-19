import logging
import os
import scrapy
import w3lib.html

from ..items import DtekParserItem

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
parsing_logger_file_handler = logging.FileHandler('log/parsed_output.log', encoding='utf-8')
parsing_logger_file_handler.setLevel(logging.DEBUG)
parsing_logger_file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
parsing_logger.addHandler(parsing_logger_file_handler)


class DTEKSpider(scrapy.Spider):
    """Scrapy class that parses DTEK site"""

    name = 'dtek_parser'
    base_url = 'https://www.dtek-krem.com.ua'

    AREAS = ['Бориспільський']          # todo fill with all areas ["Район1", "Район2", ...]
    LOCATIONS = ['Петропавлівське']     # todo fill with all locations

    start_urls = [
        f'{base_url}/ru/outages?'
        f'query={LOCATIONS[0]}'
        f'&rem={AREAS[0]}',

        # f'{base_url}/...',
        # f'{base_url}/...',
    ]

    @classmethod
    def get_user_streets(cls, all_towns_and_streets, user_town):
        """Getting found_town_and_streets from a complicated string from parsed html"""

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
        """Parsing DTEK page and yielding an item to pipelines"""

        user_town = self.LOCATIONS[0]
        # user_area = self.AREAS[0]
        rows = response.xpath("//tr['data-id'][position()>1]")
        for row in rows:
            towns = row.xpath('td//b/text()')        # type -> Selector
            list_of_towns = [loc.get() for loc in towns]
            if user_town not in list_of_towns:
                logging.info('Error, no user location in results')

            cols = row.xpath('td')

            list_of_cols = [w3lib.html.remove_tags(col.get()).strip() for col in cols]
            outage_date, turn_on_date, area, all_towns_and_streets, works_type, posting_date, \
                outage_schedule, status = list_of_cols

            streets = self.get_user_streets(all_towns_and_streets, user_town)

            output_string = f'По данным ДТЭК {outage_date} {outage_schedule} будут проводиться: {works_type} ' \
                            f'в локациях: {streets}. (Размещено {posting_date}) Cтатус: {status}'
            parsing_logger.info(output_string)

            # with open('log/parsed_output.log', 'a', encoding='utf-8') as f:
            #     f.write(output_string + "\n")

            item = DtekParserItem(
                outage_date=outage_date,
                turn_on_date=turn_on_date,
                area=area,
                all_towns_and_streets=all_towns_and_streets,
                works_type=works_type,
                posting_date=posting_date,
                outage_schedule=outage_schedule,
                status=status
            )
            yield item
