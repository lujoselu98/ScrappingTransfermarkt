import pickle
from collections import Counter
from os import listdir
from os.path import isfile, join

import matplotlib.pyplot as plt
import pandas as pd

from final_crawler import DATA_PATH

if __name__ == '__main__':
    price_path = f"{DATA_PATH}/values"
    price_files = [f for f in listdir(price_path) if isfile(join(price_path, f))]

    filter_names = list(pd.read_csv(f"{DATA_PATH}/Filter_All_Players_Data.csv")['nombre'])
    months = []

    for i, file in enumerate(price_files):
        filename = f"{price_path}/{file}"
        nombre_canonico = "-".join(filename.split("/")[2].split("-")[:-1])
        id = int(filename.split('/')[2].split("-")[-1].strip(".pickle"))

        # Filtering based on players filtered from performance
        if nombre_canonico not in filter_names:
            continue

        with open(filename, "rb") as f:
            values = pickle.load(f)

        for date in values.keys():
            month = date.split("/")[1]
            months.append(month)

    month_freq = Counter(months)
    print(month_freq)
    hist_data = pd.DataFrame({"month": month_freq.keys(), "count": month_freq.values()})
    hist_data.sort_values(by="month", inplace=True)
    print(hist_data)
    hist_data.plot(x="month", y="count", kind="bar")
    fig = plt.gcf()
    fig.savefig(f"{DATA_PATH}/values_month_hist.png")
    plt.show()
