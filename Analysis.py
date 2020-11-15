import os

import matplotlib.pyplot as plt
import pandas as pd

from final_crawler import DATA_PATH

PLOT_PATH = "./plots"

if __name__ == '__main__':

    data = pd.read_csv(f"{DATA_PATH}/Second_Filter_All_Players_Data.csv", index_col="id")

    data_numeric = data.drop(
        columns=['nombre', '2015_std_value', '2016_std_value', '2017_std_value', '2018_std_value', '2019_std_value'])

    temporadas = ['2015', '2016', '2017', '2018', '2019']
    for temporada in temporadas:
        columns = [column for column in list(data_numeric.columns) if temporada in column]
        for column in columns:
            serie_data = list(data.loc[:, column])
            value = ' '.join(column.split('_')[1:])
            plt.hist(serie_data, density=True, bins=50)
            title = f"{temporada} {value}"
            plt.title(title)
            plt.ylabel("Count")
            plt.xlabel(value)
            fig = plt.gcf()
            filename = title.replace(" ", "_")
            print(filename)
            os.makedirs(f"{PLOT_PATH}/uni_variable_hist/", exist_ok=True)
            fig.savefig(f"{PLOT_PATH}/uni_variable_hist/{filename}.png")
            plt.show()

