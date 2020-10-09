import pandas as pd
if __name__ == '__main__':
    df = pd.DataFrame(columns=['Name', 'Edad', 'Price', 'Sell'])
    df.loc[len(df.index)] = ["Apple", 1.50, 3, 2]
    df.loc[len(df.index)] = ["Banana", 0.75, -8, 4]
    df.loc[len(df.index)] = ["Carrot", 2.00, -6, -3]
    df.loc[len(df.index)] = ["Blueberry", 0.05, 5, 6]

    print(df)
