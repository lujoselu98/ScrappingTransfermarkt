import os
import pickle

from scrapy.selector import Selector
from tqdm import tqdm

from final_crawler import DATA_PATH
from final_crawler import request_robusto


def extract_performace(link, temporadas=None):
    if temporadas is None:
        temporadas = ['2015', '2016', '2017', '2018', '2019']

    rendimiento = dict((t, dict()) for t in temporadas)

    for temporada in temporadas:
        actual_link = link + f'/saison/{temporada}/verein/0/liga/0/wettbewerb//pos/0/trainer_id/0/plus/1='

        res = request_robusto(actual_link)
        sel = Selector(text=res.content)

        info = sel.css("#yw1 > table > tfoot > tr > td ::text").extract()
        info = [i.strip("\'").replace('.', '').replace(',', '.') for i in info if 'Total' not in i and '\xa0' not in i]
        info = [i if i != '-' else 0 for i in info]

        if len(info) == 0:
            rendimiento[temporada] = {
                'alineaciones': 0,
                'puntos_por_partido': 0,
                'minutos_jugados': 0,
                'minutos_por_asistencia': 0
            }
        else:
            alineaciones = int(info[1])
            puntos_por_partido = float(info[2])
            asistencias = int(info[4])
            minutos_por_gol = int(info[-2])
            minutos_jugados = int(info[-1])
            if asistencias == 0:
                minutos_por_asistencia = 0
            else:
                minutos_por_asistencia = round(minutos_jugados / asistencias)

            rendimiento[temporada] = {
                'alineaciones': alineaciones,
                'puntos_por_partido': puntos_por_partido,
                'minutos_jugados': minutos_jugados,
                'minutos_por_gol': minutos_por_gol,
                'minutos_por_asistencia': minutos_por_asistencia
            }
    return rendimiento


if __name__ == '__main__':
    f = open('data/urls.txt', 'r')
    lines = f.readlines()
    links = [line.strip().replace('profil', 'leistungsdatendetails') for line in lines]
    # links = [links[0]] + [link for link in links if 'joelinton' in link]
    # print(*links[:10], sep="\n")
    os.makedirs(f"{DATA_PATH}/performance/", exist_ok=True)
    for link in tqdm(links):
        nombre_canonico = link.split("/")[3]
        id = link.split("/")[-1]
        nombre_fichero = nombre_canonico + "-" + str(id)
        filename = f"{DATA_PATH}/performance/{nombre_fichero}.pickle"
        rendimiento = extract_performace(link)
        with open(filename, "wb") as f:
            pickle.dump(rendimiento, f)
