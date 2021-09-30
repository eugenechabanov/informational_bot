from bs4 import BeautifulSoup
import os
import pickle
import requests

LOCATION = 'Петропавлівське'
# LOCATION = 'Вишеньки'
# LOCATION = 'Мартусівка'
AREA = 'Бориспільський'

base_url = 'https://www.dtek-krem.com.ua/ru/outages?query=' \
           f'{LOCATION}' \
           '&page=1' \
           f'&rem={AREA}' \
           '&type=-1&status=-1&shutdown-date=-1&inclusion-date=-1&create-date=-1'
headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'ru,en-US;q=0.7,en;q=0.3',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    'Host': 'www.dtek-krem.com.ua',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:92.0) Gecko/20100101 Firefox/92.0',
    'Cookie': 'Domain=dtek-krem.com.ua; _language=dce82c8ef3164aeef3d02d2ed972658f236cee1dc55549d5c7561f1084ab96e1a%3A2%3A%7Bi%3A0%3Bs%3A9%3A%22_language%22%3Bi%3A1%3Bs%3A2%3A%22ru%22%3B%7D; _csrf-dtek-krem=a14d6090ca68135b2dd4870f1bfa9688c827ebb09830e57a48b635cfab82a1b1a%3A2%3A%7Bi%3A0%3Bs%3A15%3A%22_csrf-dtek-krem%22%3Bi%3A1%3Bs%3A32%3A%221G3QMpfv-xmG4-R9ptJSmPFFHDXJ20mC%22%3B%7D; visid_incap_2398465=9QpsQEtISqe6bE+EkPyBHnp4VWEAAAAAQUIPAAAAAAD/sdQ8JKYctMsF6ZQ3jIvg; nlbi_2398465=B0KIQvoLGVRaJ71RReYW8gAAAADBhvGUD9kXu9ceGyPx93rC; incap_ses_324_2398465=6c3MaJxRnw9MuPniWBR/BDa0VWEAAAAAwWwz0n53+5ntM4uRnRRS8g==; _ga=GA1.3.727579112.1632991366; _gid=GA1.3.857456105.1632991366; Domain=dtek-krem.com.ua; dtek-krem=p98nk3171gsamakn171hf5scga; _gat_gtag_UA_180679529_1=1'
}

CACHED = True
# CACHED = False
CACHE_FILE = os.path.join(os.getcwd(), 'cache/page.pkl')

# creating all required folders
folders = ['cache']
for folder in folders:
    if not os.path.exists(folder):
        os.makedirs(folder)


def main():
    """
    Connect to DTEK site and get all entries with specified LOCATION
    """
    if CACHED:
        response = pickle.load(open(CACHE_FILE, "rb"))
    else:
        response = requests.get(base_url, headers=headers)
        pickle.dump(response, open("cache/page.pkl", "wb"))
    soup = BeautifulSoup(response.text, 'html.parser')

    if 'data-id' not in response.text:   # something wrong with request
        print(response.text)
        return
    table = soup.find('table')
    rows = table.findAll('tr')

    number_of_entries_found = (len(rows) - 1)
    if number_of_entries_found == 0:
        print(f'Новых записей по населенному пункту {LOCATION} на данный момент нет.')
        return
    elif number_of_entries_found > 10:
        print('Более 10 результатов. Пора делать захват результатов на следующих страницах.')
    print(f'Найдено {number_of_entries_found} записей по населенному пункту {LOCATION}')

    for row in rows[1:]:
        row_data_id = row.get('data-id')
        cols = row.findAll('td')
        # print('vvvvvvvvvv')
        # print(row)
        # print(cols)
        # print('^^^^^^^^^^')
        outage_date, turn_on_date, area, all_towns, works_type, posting_date, outage_time, status = \
            [col.text for col in cols]
        all_towns = all_towns.split('\n')
        user_town = ''
        for town in all_towns:
            if LOCATION in town:
                user_town = town
                break
        if not user_town:
            print('error, no user location in results')
        streets = BeautifulSoup(user_town, 'html.parser').get_text()
        print(f'id: {row_data_id}. По данным ДТЭК {outage_date} {outage_time} будут проводиться: {works_type} '
              f'в локациях: {streets}. Информация была размещена {posting_date}, статус: {status}')


if __name__ == '__main__':
    main()
