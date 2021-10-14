from bs4 import BeautifulSoup
import logging
import os
import pickle
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

LOCATION = 'Петропавлівське'
# LOCATION = 'Вишеньки'
# LOCATION = 'Мартусівка'
AREA = 'Бориспільський'

base_url = 'https://www.dtek-krem.com.ua'
check_outage_url = f'{base_url}/ru/outages?' \
                   f'query={LOCATION}' \
                   f'&rem={AREA}' \
                   # '&page=1&type=-1&status=-1&shutdown-date=-1&inclusion-date=-1&create-date=-1&page-limit=50'

# Two main flags here CACHED and PRODUCTION.
# CACHED controls whether we get the site from web or from cache
# PRODUCTION adds selenium parameters to launch browser in headless mode

# PRODUCTION = True
PRODUCTION = False

# CACHED = True
CACHED = False

if PRODUCTION:
    CACHED = False

CACHE_FILE = os.path.join(os.getcwd(), 'cache/page.pkl')
COOKIES_FILE = os.path.join(os.getcwd(), 'cache/cookies.pkl')

folders_to_create = ['cache', 'log']
for folder in folders_to_create:  # creating all standard folders if they don't exist already
    if not os.path.exists(folder):
        os.makedirs(folder)

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[logging.FileHandler(filename='log/operational.log',
                                                  mode='a', encoding='utf-8'), logging.StreamHandler()])


def load_cookies():
    if os.path.isfile(COOKIES_FILE):
        with open(COOKIES_FILE, 'rb') as f:
            cookies = pickle.load(f)
        return cookies
    else:
        print('No cookies found. Accessing the page without cookies.')
        return ''


def main():
    """
    Connect to DTEK site and get all entries with specified LOCATION.
    Selenium gets the page source, and BeautifulSoup further gets us all outage information.
    Every successful iteration we save cookies, which are then loaded next time during the launch.
    """
    if CACHED:
        response_text = pickle.load(open(CACHE_FILE, "rb"))
    else:
        options = Options()
        if PRODUCTION:
            options.headless = True
            options.add_argument("--no-sandbox")

        driver = webdriver.Chrome(executable_path=ChromeDriverManager().install(), options=options)
        driver.implicitly_wait(20)

        # to load cookies we need to be on the same domain. Here we first go to the home page of electrical company:
        driver.get(base_url)
        cookies = load_cookies()
        for cookie in cookies:
            driver.add_cookie(cookie)
        logging.info(f'{len(cookies)} Cookies loaded.')

        logging.info(f'Opening page: {check_outage_url}')

        driver.get(check_outage_url)
        response_text = driver.page_source  # -> string

        if 'data-id' in response_text or 'Проверьте свой адрес в списке отключений' in response_text:
            logging.info('Page opened successfully.')

            # saving cookies to a separate file
            pickle.dump(driver.get_cookies(), open(COOKIES_FILE, "wb"))
            logging.info('Cookies saved.')

            # dumping page into cache file
            pickle.dump(response_text, open("cache/page.pkl", "wb"))
            logging.info('Page saved to cache.')
        
        else:
            logging.info('There was an error opening page. Here is the response text:\n',
                         BeautifulSoup(response_text, "html.parser").prettify())
            return

    soup = BeautifulSoup(response_text, 'html.parser')
    table = soup.find('table')
    rows = table.findAll('tr')

    number_of_entries_found = (len(rows) - 1)

    if number_of_entries_found == 0:
        logging.info(f'Новых записей по населенному пункту {LOCATION} на данный момент нет.')
        return
    elif number_of_entries_found > 50:
        logging.info('Внимание! Более 50 результатов. Начинается Апокалипсис.')

    logging.info(f'Найдено {number_of_entries_found} записей по населенному пункту {LOCATION}')

    for row in rows[1:]:
        row_data_id = row.get('data-id')
        cols = row.findAll('td')

        # todo store all these values in database
        outage_date, turn_on_date, area, all_towns, works_type, posting_date, outage_time, status = \
            [col.text for col in cols]
        all_towns = all_towns.split('\n')
        user_town = ''
        for town in all_towns:
            if LOCATION in town:
                user_town = town
                break
        if not user_town:
            logging.info('Error, no user location in results')
        streets = BeautifulSoup(user_town, 'html.parser').get_text()
        logging.info(f'id: {row_data_id}. По данным ДТЭК {outage_date} {outage_time} будут проводиться: {works_type} '
                     f'в локациях: {streets}. (Размещено {posting_date}) Cтатус: {status}')


if __name__ == '__main__':
    main()
