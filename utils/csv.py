import pandas as pd


def save_data_to_csv(dataframe, filename='etf_data.csv'):
    """
    Save the DataFrame to a CSV file.
    """
    dataframe.to_csv(filename, index=False)
    print(f"Data saved to {filename}")

def load_data_from_csv(filename='etf_data.csv'):
    """
    Load the DataFrame from a CSV file.
    """
    try:
        dataframe = pd.read_csv(filename)
        print(f"Data loaded from {filename}")
        return dataframe
    except FileNotFoundError:
        print(f"File {filename} not found.")
        return pd.DataFrame()