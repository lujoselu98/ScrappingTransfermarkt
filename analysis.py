import pickle
from os import listdir
from os.path import isfile, join

import pandas as pd

from final_crawler import DATA_PATH
datos = ['alineaciones', 'puntos_por_partido', 'minutos_jugados', 'minutos_por_gol', 'minutos_por_asistencia']
temporadas = ['2015', '2016', '2017', '2018', '2019']

def create_dataframe():

    columns = ['id', 'nombre']

    for temporada in temporadas:
        for dato in datos:
            columns.append(f"{temporada}_{dato}")
    performance_path = f"{DATA_PATH}/performace"
    performance_files = [f for f in listdir(performance_path) if isfile(join(performance_path, f))]

    dataframe = pd.DataFrame(columns=columns, index=[i for i in range(len(performance_files))])
    for i, file in enumerate(performance_files):
        filename = f"{performance_path}/{file}"

        player_dict = dict()
        nombre_canonico = "-".join(filename.split("/")[2].split("-")[:-1])
        id = int(filename.split('/')[2].split("-")[-1].strip(".pickle"))

        player_dict['nombre'] = nombre_canonico
        player_dict['id'] = id

        with open(filename, "rb") as f:
            rendimiento = pickle.load(f)
        for key in rendimiento:
            for dato, valor in rendimiento[key].items():
                player_dict[f"{key}_{dato}"] = valor
        dataframe.loc[i, :] = player_dict

    return dataframe


if __name__ == '__main__':
    dataframe = create_dataframe()

    nombres_quitar = []
    for i in range(len(dataframe)):
        for temporada in temporadas:
            jugador_terminado = False
            for dato in datos:
                column = f"{temporada}_{dato}"
                if dataframe.loc[i, column] == 0:
                    nombres_quitar.append(dataframe.loc[i, "nombre"])
                    jugador_terminado = True
                    break
            if jugador_terminado:
                break

    dataframe = dataframe[~dataframe['nombre'].isin(nombres_quitar)]
    dataframe.to_csv(f"{DATA_PATH}\Filter_All_Players_Data.csv")
