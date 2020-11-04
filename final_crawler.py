import datetime
import json
import os
import pickle
import time

import pandas as pd
import requests
from bs4 import BeautifulSoup as bs
from scrapy import Selector


# Remove not alpha characters and no-spaces
def is_alpha_and_spaces(string):
    return string.replace(' ', '') \
        .replace('-', '') \
        .replace('\'', '') \
        .isalpha()


# Path donde guardar los datos (csv, htmls, y pickle)
DATA_PATH = "data"

# Crawler ettiquette
HEADERS = {'User-Agent': 'Custom / crawler para proyecto academico jose.lavado@estudiante.uam.es'}


# Funcion para hacer request robustos
# Reintenta un maximo de max_retries intentos (default 5)
# Entre intento e intento expera time_between_retries * intentos_que_lleva (default 1, -> 1,2,4,8,16)
# Devuelve la respuesta (commpleta) o None en caso de no conseguirlo en el numero de intentos especificados
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


# Scrapping (manual) de la pagina de valores para guardar toda la evoluvcion del jugador posterior a no_before
def extract_market_value(link, no_before=datetime.datetime(2015, 1, 1)):
    res = request_robusto(link)

    # Usamos beautiful soup 4 por que al ser una grafica (svg) que carga en dinamico necesitamos hacer scrapping
    # al codigo javascript que la genera que es donde estan los datos realmente

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


# Scrapping (manual) de la tabla con todos los titulos del jugador que sean no anteriores a la temporada 15/16 o el 2015
def extract_cups(link, no_before="15"):
    res = request_robusto(link)
    sel = Selector(text=res.content)
    # Cogemos todas la filas de la tabla de titulos
    parent = sel.css('div.large-4 > div.box  tbody tr')
    titulos_dict = dict()
    for element in parent:
        element_classes = element.css('::attr(class)').extract()
        if 'bg_Sturm' in element_classes:
            # Nombre del titulo
            titulo = element.css('td::text')[0].extract()
            titulo = titulo.split('x')[1].strip()
            titulos_dict[titulo] = []
        else:
            # Info hay que tener en cuenta que hay muchos tipos diferentes de titulos.
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

    # Filtrado de tiulos vacios (por que no se ganaron despues de la fecha indicada)
    for key in titulos_dict.copy().keys():
        if len(titulos_dict[key]) == 0:
            del titulos_dict[key]
    return titulos_dict


if __name__ == '__main__':
    prefix = 'https://www.transfermarkt.es'

    # Main dataframe
    df = pd.DataFrame(columns=['Id', 'Name', 'Edad', 'Precio'])

    # Semilla
    most_valuable_players_url = prefix + "/spieler-statistik/wertvollstespieler/marktwertetop" + \
                                "/plus/0/galerie/0?ausrichtung=Sturm&spielerposition_id=alle" \
                                "&altersklasse=23-30&jahrgang=0&land_id=0&kontinent_id=0&yt0=Mostrar"

    response = request_robusto(most_valuable_players_url)
    sel = Selector(text=response.content)

    # Mirar a ver si hay link a la siguiente pagina
    selector_siguiente = sel.css('li.naechste-seite > a')

    while True:  # Mientras haya siguiente
        # Coger todas las primeras celdas (el link dentro)
        parent = sel.css('td > a.spielprofil_tooltip')

        # Cogemos de cada jugador de la pagina su nombre (sin caracteres extranos),
        # el link a su perfil (para sacar luego sus titulos y su evoluvcion), su valor y su edad

        nombres = [nombre for nombre in parent.css('::text').extract() if is_alpha_and_spaces(nombre)]
        links = [prefix + link for link in parent.css(' ::attr(href)').extract() if '#' not in link]

        parent = sel.xpath('//*[@id="yw1"]/table/tbody/tr/td[3]')
        edades = [edad for edad in parent.css(' ::text').extract()]

        parent = sel.css('td.hauptlink  b')
        precios = [precio for precio in parent.css(' ::text').extract()]

        filename = f"{DATA_PATH}/urls.txt"
        with open(filename, 'a') as f:
            f.writelines("\n".join(links))
        with open(filename, 'a') as f:
            f.write("\n")

        for nombre, link, edad, precio in zip(nombres, links, edades, precios):
            # Por cada jugador en la pagina
            response = request_robusto(link)
            player_sel = Selector(text=response.content)
            nombre_check = ' '.join([x.strip() for x in player_sel.css('div.dataName > h1 ::text').extract()])
            id = int(link.split("/")[-1])

            # Comprobamos que el el link es correcto yendo a su perfil y viendo que los nombres coinciden
            if nombre != nombre_check:
                print("ERROR")
                break
            nombre_canonico = link.split('/')[3]

            # Guardamos datos identificativos en un data frame (que luego salvamos en .csv)
            df.loc[len(df.index)] = [id, nombre_canonico, edad, precio]

            nombre_fichero = nombre_canonico + "-" + str(id)

            os.makedirs(f"{DATA_PATH}/htmls/", exist_ok=True)

            filename = f"{DATA_PATH}/htmls/{nombre_fichero}.html"

            # Guardamos el html completo de su pagina de perfil
            with open(filename, "wb") as f:
                f.write(response.content)

            print(f"Finish {nombre_fichero} html y dataframe")

            # Funcion para extraer el valor a partir del link (modificado) del perfil
            link_value = link.replace('profil', 'marktwertverlauf')
            value_dict = extract_market_value(link_value)

            os.makedirs(f"{DATA_PATH}/values/", exist_ok=True)

            filename = f"{DATA_PATH}/values/{nombre_fichero}.pickle"

            # Salvamos diciconario con la evolucion del valor (formato pickle)
            with open(filename, "wb") as f:
                pickle.dump(value_dict, f)

            print(f"Finish {nombre_fichero} value")

            # Funcion para extraer los titulos a partir del link (modificado) del perfil
            link_cups = link.replace('profil', 'erfolge')
            cups_dict = extract_cups(link_cups)

            os.makedirs(f"{DATA_PATH}/cups/", exist_ok=True)

            filename = f"{DATA_PATH}/cups/{nombre_fichero}.pickle"

            # Salvamos diciconario con todos los titulos (formato pickle)
            with open(filename, "wb") as f:
                pickle.dump(cups_dict, f)

            print(f"Finish {nombre_fichero} cups")

        selector_siguiente = sel.css('li.naechste-seite > a')

        # Si no  hay siguiente pagina hemos terminado 25 jugadores x 20 paginas = 500 jugadores
        if len(selector_siguiente) == 0:
            break

        # Link pagina siguiente
        siguiente_link = prefix + selector_siguiente.css('::attr(href)').extract()[0]

        # Cargamos pagina siguiente (y volvemos a empezar) -> seria equivalente a ampliar la frontera
        response = request_robusto(siguiente_link)
        sel = Selector(text=response.content)

    # Save pandas dataframe to csv
    df.to_csv(f'{DATA_PATH}/Raw_All_Players_Data.csv')
