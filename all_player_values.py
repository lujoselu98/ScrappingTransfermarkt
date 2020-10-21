import json

import requests
from bs4 import BeautifulSoup as bs
import datetime

def extract_market_value(link, no_before=datetime.datetime(2015,1,1)):
    headers = {'User-Agent': 'Custom'}
    res = requests.get(link, headers=headers)
    soup = bs(res.content, 'lxml')
    scripts = soup.select('script[type="text/javascript"]')
    scripts = [str(script) for script in scripts]
    script = [script for script in scripts if 'CDATA' in script]

    value_dict = dict()

    if len(script) > 0:
        s = script[1].split("'series':")[1].split(",'credits'")[0].replace("'", '"')
        data = json.loads(s.replace('\\x', '\\u00'))
        for item in data[0]['data']:

            date_splitted = str(item['datum_mw']).split('/')
            date_splitted = [int(x) for x in date_splitted]
            date_datetime = datetime.datetime(date_splitted[2], date_splitted[1], date_splitted[0])
            if date_datetime < no_before:
                continue

            single_value = dict()
            single_value['Team'] = item['verein']
            single_value['Age'] = str(item['age'])
            single_value['Value'] = str(item['y'])
            value_dict[str(item['datum_mw'])] = single_value

            # print('Team: ' + item['verein'])
            # print('Age: ' + str(item['age']))
            # print('Date: ' + str(item['datum_mw']))
            # print('Value: ' + str(item['y']))
    return value_dict


if __name__ == '__main__':
    f = open('Raw_All_Players_Data_Links.txt', 'r')
    lines = f.readlines()
    links = [line.strip().split('->')[1].strip().replace('profil', 'marktwertverlauf') for line in lines]
    links = list(dict.fromkeys(links))
    # print(*links, sep='\n')
    for link in links:
        print(link)
        extracted_data = extract_market_value(link)
        print(extracted_data)
    '''
    a_file = open("data.pkl", "wb")
    pickle.dump(extracted_data, a_file)
    a_file.close()

    a_file = open("data.pkl", "rb")
    output = pickle.load(a_file)
    print(output)'''
