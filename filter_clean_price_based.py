import datetime
import pickle
from os import listdir
from os.path import isfile, join
from statistics import mean, median, stdev

import pandas as pd

from final_crawler import DATA_PATH

if __name__ == '__main__':
    price_path = f"{DATA_PATH}/values"
    price_files = [f for f in listdir(price_path) if isfile(join(price_path, f))]

    player_data = pd.read_csv(f"{DATA_PATH}/Filter_All_Players_Data.csv", index_col=False)
    player_data.drop(columns=["Unnamed: 0"], inplace=True)
    player_data.set_index('id', inplace=True)

    filter_names = list(player_data['nombre'])
    temporadas = ['2015', '2016', '2017', '2018', '2019']

    quitar_nombres = []

    for i, file in enumerate(price_files):
        filename = f"{price_path}/{file}"
        nombre_canonico = "-".join(filename.split("/")[2].split("-")[:-1])
        id = int(filename.split('/')[2].split("-")[-1].strip(".pickle"))

        # Filtering based on players filtered from performance
        if nombre_canonico not in filter_names:
            continue

        with open(filename, "rb") as f:
            values = pickle.load(f)

        '''for date, value in values.items():
            print(f"{date} : {value['Value']}")'''

        for temporada in temporadas:
            inicio = datetime.date(int(temporada), 7, 1)
            fin = datetime.date(int(temporada) + 1, 6, 30)
            values_temporada = []
            for date, value in values.items():
                date_datetime = datetime.datetime.strptime(date, "%d/%m/%Y")
                if inicio <= date_datetime.date() <= fin:
                    values_temporada.append(value['Value'])
            if len(values_temporada) == 0:
                quitar_nombres.append(nombre_canonico)
                break
            else:
                values_temporada = list(map(int, values_temporada))
                player_dict = dict()
                player_dict["nombre"] = nombre_canonico
                mean_value = mean(values_temporada)
                player_dict[f"{temporada}_mean"] = mean_value
                player_data.loc[player_data["nombre"] == nombre_canonico, f"{temporada}_mean"] = mean_value

                median_value = median(values_temporada)
                player_dict[f"{temporada}_median"] = median_value
                player_data.loc[player_data["nombre"] == nombre_canonico, f"{temporada}_median"] = median_value

                if len(values_temporada) > 1:
                    std_value = stdev(values_temporada)
                else:
                    std_value = 0
                player_dict[f"{temporada}_std"] = std_value
                player_data.loc[player_data["nombre"] == nombre_canonico, f"{temporada}_std"] = std_value

                min_value = min(values_temporada)
                player_dict[f"{temporada}_min"] = min_value
                player_data.loc[player_data["nombre"] == nombre_canonico, f"{temporada}_min"] = min_value

                max_value = max(values_temporada)
                player_dict[f"{temporada}_max"] = max_value
                player_data.loc[player_data["nombre"] == nombre_canonico, f"{temporada}_max"] = max_value

        '''for date in values.keys():
            month = date.split("/")[1]
            months.append(month)'''
        #break

    player_data = player_data[~player_data["nombre"].isin(quitar_nombres)]
    print(player_data)
    print(player_data.describe())
    player_data.to_csv(f"{DATA_PATH}/Second_Filter_All_Players_Data.csv")


    # print(len(quitar_nombres))
    # print(*quitar_nombres, sep="\n")

    '''month_freq = Counter(months)
    print(month_freq)
    hist_data = pd.DataFrame({"month": month_freq.keys(), "count": month_freq.values()})
    hist_data.sort_values(by="month", inplace=True)
    print(hist_data)
    hist_data.plot(x="month", y="count", kind="bar")
    fig = plt.gcf()
    fig.savefig(f"{DATA_PATH}/values_month_hist.png")
    plt.show()'''
