import datetime
import json
import os
import pickle
import time
from os import listdir
from os.path import isfile, join

import pandas as pd
import requests
from bs4 import BeautifulSoup as bs
from scrapy import Selector


def is_alpha_and_spaces(string):
    return string.replace(' ', '') \
        .replace('-', '') \
        .replace('\'', '') \
        .isalpha()


def onlyfiles(path, extension=""):
    return [f.replace(extension, "") for f in listdir(path) if isfile(join(path, f))]


DATA_PATH = "data"
# Cambiar por uno mas identificativo
HEADERS = {'User-Agent': 'Custom / crawler para proyecto academico jose.lavado@estudiante.uam.es'}


def request_robusto(link, max_retries=5, time_between_retries=1):
    success = False
    retries = 1
    request = None
    while not success:
        try:
            request = requests.get(link, headers=HEADERS)
            success = True
        except Exception as e:
            wait = retries * time_between_retries
            time_between_retries *= 2
            print(f"Error with {link} retrinying (retries)")
            time.sleep(wait)
            retries += 1
        finally:
            if retries == max_retries:
                success = True
    return request


def extract_market_value(link, no_before=datetime.datetime(2015, 1, 1)):
    res = request_robusto(link)
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

    return value_dict


def extract_cups(link, no_before="15"):
    res = request_robusto(link)
    sel = Selector(text=res.content)
    parent = sel.css('div.large-4 > div.box  tbody tr')
    titulos_dict = dict()
    for element in parent:
        element_classes = element.css('::attr(class)').extract()
        if 'bg_Sturm' in element_classes:
            titulo = element.css('td::text')[0].extract()
            titulo = titulo.split('x')[1].strip()
            titulos_dict[titulo] = []
        else:
            ano = element.css('td:nth-of-type(1) ::text')[0].extract()
            if '/' in ano:
                ano_splits = [int(x) for x in ano.split('/')]
                no_before_int = int(no_before)
                if any(ano_split < no_before_int for ano_split in ano_splits):
                    continue
            else:
                no_before_int = int('20' + no_before)
                if int(ano) < no_before_int:
                    continue
            texts = element.css('td:nth-of-type(3) ::text').extract()
            texts = [text for text in texts if '\n' not in text]
            texts = [text.strip() for text in texts if len(text.strip()) > 0]
            if len(texts) > 1:
                extra_info = texts[1:]
            else:
                extra_info = None
            if len(texts) > 0:
                equipo_o_liga = texts[0]
            else:
                equipo_o_liga = None
            single_cup = {'anno': ano, 'equipo_o_liga': equipo_o_liga, 'extra_info': extra_info}
            titulos_dict[titulo].append(single_cup)

    for key in titulos_dict.copy().keys():
        if len(titulos_dict[key]) == 0:
            del titulos_dict[key]
    return titulos_dict


if __name__ == '__main__':
    prefix = 'https://www.transfermarkt.es'

    # Main dataframe
    df = pd.DataFrame(columns=['Id', 'Name', 'Edad', 'Precio'])

    # Semilla
    most_valuable_players_url = prefix + "/spieler-statistik/wertvollstespieler/marktwertetop"

    response = request_robusto(most_valuable_players_url)
    sel = Selector(text=response.content)

    selector_siguiente = sel.css('li.naechste-seite > a')
    while True:
        parent = sel.css('td > a.spielprofil_tooltip')

        nombres = [nombre for nombre in parent.css('::text').extract() if is_alpha_and_spaces(nombre)]
        links = [prefix + link for link in parent.css(' ::attr(href)').extract() if '#' not in link]

        parent = sel.xpath('//*[@id="yw1"]/table/tbody/tr/td[3]')
        edades = [edad for edad in parent.css(' ::text').extract()]

        parent = sel.css('td.hauptlink  b')
        precios = [precio for precio in parent.css(' ::text').extract()]

        for nombre, link, edad, precio in zip(nombres, links, edades, precios):
            response = request_robusto(link)
            player_sel = Selector(text=response.content)
            nombre_check = ' '.join([x.strip() for x in player_sel.css('div.dataName > h1 ::text').extract()])
            id = int(link.split("/")[-1])

            if nombre != nombre_check:
                print("ERROR")
                break
            nombre_canonico = link.split('/')[3]

            df.loc[len(df.index)] = [id, nombre_canonico, edad, precio]

            nombre_fichero = nombre_canonico + "-" + str(id)

            os.makedirs(f"{DATA_PATH}/htmls/", exist_ok=True)

            filename = f"{DATA_PATH}/htmls/{nombre_fichero}.html"

            with open(filename, "wb") as f:
                f.write(response.content)

            print(f"Finish {nombre_fichero} html y dataframe")

            link_value = link.replace('profil', 'marktwertverlauf')
            value_dict = extract_market_value(link_value)

            os.makedirs(f"{DATA_PATH}/values/", exist_ok=True)

            filename = f"{DATA_PATH}/values/{nombre_fichero}.pickle"

            with open(filename, "wb") as f:
                pickle.dump(value_dict, f)

            print(f"Finish {nombre_fichero} value")

            link_cups= link.replace('profil', 'erfolge')
            cups_dict = extract_cups(link_cups)

            os.makedirs(f"{DATA_PATH}/cups/", exist_ok=True)

            filename = f"{DATA_PATH}/cups/{nombre_fichero}.pickle"

            with open(filename, "wb") as f:
                pickle.dump(cups_dict, f)

            print(f"Finish {nombre_fichero} cups")

        selector_siguiente = sel.css('li.naechste-seite > a')

        if len(selector_siguiente) == 0:
            break

        siguiente_link = prefix + selector_siguiente.css('::attr(href)').extract()[0]
        response = request_robusto(siguiente_link)
        sel = Selector(text=response.content)
