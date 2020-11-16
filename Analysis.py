import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn import metrics
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import PolynomialFeatures

from final_crawler import DATA_PATH

PLOT_PATH = "./plots"


def save_univariate_histograms(data_numeric, temporadas=None, show=True):
    if temporadas is None:
        temporadas = ['2014', '2015', '2016', '2017', '2018', '2019']
    os.makedirs(f"{PLOT_PATH}/uni_variable_hist/", exist_ok=True)
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
            fig.savefig(f"{PLOT_PATH}/uni_variable_hist/{filename}.png")
            if show:
                plt.show()


def save_regresions(data_numeric, temporadas=None, show=True, ):
    if temporadas is None:
        temporadas = ['2014', '2015', '2016', '2017', '2018']

    model = LinearRegression()
    os.makedirs(f"{PLOT_PATH}/simple_regression/", exist_ok=True)
    for temporada in temporadas:
        temporada_columns_predictors = [column for column in list(data_numeric.columns) if temporada in column]
        temporada_columns_response = [column for column in list(data_numeric.columns) if
                                      str(int(temporada) + 1) in column]
        predictor_columns = [column for column in temporada_columns_predictors if
                             'gol' in column or 'asistencia' in column or 'puntos' in column]
        for predictor in predictor_columns:
            predictor_values = data_numeric.loc[:, predictor].to_numpy()
            predictor_name = ' '.join(predictor.split('_')[1:])
            response_columns = [column for column in temporada_columns_response if 'value' in column]
            for response in response_columns:
                response_values = data_numeric.loc[:, response].to_numpy()
                response_name = ' '.join(response.split('_')[:])

                X, y = predictor_values.reshape((-1, 1)), response_values

                fit_model = model.fit(X, y)

                y_hat = fit_model.predict(X)
                MSE = round(metrics.mean_squared_error(y, y_hat), 4)
                R_2 = round(metrics.r2_score(y, y_hat), 4)
                title = f"{temporada} {predictor_name} vs {response_name}"
                fig = plt.figure()
                ax = fig.add_subplot(111)
                plt.title(title)
                plt.ylabel("Precio medio")
                plt.xlabel("Puntos por partido")
                plt.scatter(x=X, y=y)
                plt.plot(X, y_hat, 'r--', label='Least Square Regression Line')
                plt.legend()
                plt.text(0.74, 0.82, f'R2: {R_2}\n MSE: {MSE}', horizontalalignment='center',
                         verticalalignment='center',
                         transform=ax.transAxes, style='italic', fontsize=11,
                         bbox={'facecolor': 'grey', 'alpha': 0.5, 'pad': 9})
                filename = title.replace(" ", "_")
                fig.savefig(f"{PLOT_PATH}/simple_regression/{filename}.png")
                if show:
                    plt.show()

def print_multiple_and_polynomial_regression(temporadas = None):
    if temporadas is None:
        temporadas = ['2014', '2015', '2016', '2017', '2018']

    os.makedirs(f"{PLOT_PATH}/multiple_regression/", exist_ok=True)
    linear_model = LinearRegression()
    degrees = [i for i in range(2, 9)]

    for temporada in temporadas:
        temporada_columns_predictors = [column for column in list(data_numeric.columns) if temporada in column]
        temporada_columns_response = [column for column in list(data_numeric.columns) if
                                      str(int(temporada) + 1) in column]
        predictor_columns = [column for column in temporada_columns_predictors if
                             'gol' in column or 'asistencia' in column or 'puntos' in column]
        X = []
        for predictor in predictor_columns:
            predictor_values = data_numeric.loc[:, predictor].to_numpy()
            predictor_name = ' '.join(predictor.split('_')[1:])
            response_columns = [column for column in temporada_columns_response if 'value' in column]
            X.append(predictor_values)
        X = np.array(X).T

        response_columns = [column for column in temporada_columns_response if 'value' in column]
        for response in response_columns:
            response_values = data_numeric.loc[:, response].to_numpy()
            response_name = ' '.join(response.split('_')[:])

            y = response_values
            fit_model = linear_model.fit(X, y)

            y_hat = fit_model.predict(X)
            MSE = round(metrics.mean_squared_error(y, y_hat), 4)
            R_2 = round(metrics.r2_score(y, y_hat), 4)
            print(f"{response_name} (linear) \nMSE:\t{MSE}\nR^2:\t{R_2}\n")

            for degree in degrees:
                polynomial_model = make_pipeline(PolynomialFeatures(degree), LinearRegression())
                fit_model = polynomial_model.fit(X, y)
                y = response_values

                y_hat = fit_model.predict(X)
                MSE = round(metrics.mean_squared_error(y, y_hat), 4)
                R_2 = round(metrics.r2_score(y, y_hat), 4)
                print(f"{response_name} (polynomial [{degree}])\nMSE:\t{MSE}\nR^2:\t{R_2}\n")

        print("*" * 10 + "\n")


if __name__ == '__main__':
    data = pd.read_csv(f"{DATA_PATH}/Second_Filter_All_Players_Data.csv", index_col="id")

    data_numeric = data.drop(
        columns=['nombre', '2015_std_value', '2016_std_value', '2017_std_value', '2018_std_value', '2019_std_value'])

    os.makedirs(f"{PLOT_PATH}", exist_ok=True)

    # save_univariate_histograms(data_numeric)

    # save_regresions(data_numeric)

    print_multiple_and_polynomial_regression()
