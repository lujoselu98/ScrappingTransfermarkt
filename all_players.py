import string

import pandas as pd
import requests
from scrapy.selector import Selector

from utils import is_alpha_and_spaces
from utils import onlyfiles

if __name__ == '__main__':
    prefix = 'https://www.transfermarkt.es'
    headers = {'User-Agent': 'Custom'}

    df = pd.DataFrame(columns=['Name', 'Edad', 'Precio'])

    most_valuable_players_url = prefix + "/spieler-statistik/wertvollstespieler/marktwertetop"
    print(most_valuable_players_url)
    response = requests.get(most_valuable_players_url, headers=headers)
    response.raise_for_status()
    sel = Selector(text=response.content)

    selector_siguiente = sel.css('li.naechste-seite > a')
    i = 1
    while True:

        parent = sel.css('td > a.spielprofil_tooltip')
        nombres = [nombre for nombre in parent.css('::text').extract() if is_alpha_and_spaces(nombre)]
        links = [prefix + link for link in parent.css(' ::attr(href)').extract() if '#' not in link]

        parent = sel.xpath('//*[@id="yw1"]/table/tbody/tr/td[3]')
        edades = [edad for edad in parent.css(' ::text').extract()]

        parent = sel.css('td.hauptlink  b')
        precios = [precio for precio in parent.css(' ::text').extract()]

        for nombre, link, edad, precio in zip(nombres, links, edades, precios):
            # print(f"{i} {nombre} -> {link}")
            # print(f"Edad: {edad}")
            # print(f"Precio: {precio}")
            response = requests.get(link, headers=headers)
            response.raise_for_status()
            player_sel = Selector(text=response.content)
            nombre_check = ' '.join([x.strip() for x in player_sel.css('div.dataName > h1 ::text').extract()])
            # print(nombre_check)
            if nombre != nombre_check:
                print("ERROR")
                break
            df.loc[len(df.index)] = [nombre, edad, precio]

            with open("Raw_All_Players_Data_Links.txt", "a") as f:
                f.write(f"{nombre} -> {link}\n")
            i += 1

            nombre_para_fichero = ''.join([str(char) for char in nombre if char in string.printable])
            filename = f"htmls/{nombre_para_fichero}"

            archivos_existentes = onlyfiles("htmls", ".html")

            if nombre_para_fichero in archivos_existentes:
                filename += f"{(archivos_existentes.count(nombre_para_fichero))}"
            filename += ".html"

            with open(filename, "wb") as f:
                f.write(response.content)

        selector_siguiente = sel.css('li.naechste-seite > a')

        if len(selector_siguiente) == 0:
            break

        siguiente_link = prefix + selector_siguiente.css('::attr(href)').extract()[0]
        print(siguiente_link)
        response = requests.get(siguiente_link, headers=headers)
        response.raise_for_status()
        sel = Selector(text=response.content)

    # df.to_csv('Raw_All_Players_Data.csv')
