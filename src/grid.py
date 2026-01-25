import numpy as np
import pandas as pd
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def df_to_matrix(df):
    # convert a DataFrame to a numpy matrix
    matrix = df.values
    print(f"df to matrix shape: {matrix.shape}")
    return matrix


def dict_to_matrix(date_dict):
    # generate an 7x52 matrix from a date:count dict
    end_date = pd.Timestamp.today().normalize()
    end_date -= pd.Timedelta(days=(end_date.weekday() + 1) % 7)  # last Saturday
    start_date = end_date - pd.Timedelta(weeks=52) + pd.Timedelta(days=1)

    # build date index
    all_dates = pd.date_range(start_date, end_date, freq="D")

    # build empty matrix
    matrix = np.zeros((7, 52), dtype=int)

    # fill empty matrix with dictionary values
    for d in all_dates:
        week = (d - start_date).days // 7
        weekday = (d.weekday() + 1) % 7  # Sunday = 0
        matrix[weekday, week] = date_dict.get(d.date().strftime("%Y-%m-%d"), 0) # althrough this is a datetime dict, everything stored as string
    
    print(f"dict to matrix shape: {matrix.shape}")
    return matrix

def matrix_to_dict(matrix):
    end_date = pd.Timestamp.today().normalize()
    end_date -= pd.Timedelta(days=(end_date.weekday() + 1) % 7)  # last Saturday
    start_date = end_date - pd.Timedelta(weeks=52) + pd.Timedelta(days=1)
    reconstructed_dict = {}

    for week in range(52):
        for weekday in range(7):
            d = start_date + pd.Timedelta(days=week * 7 + weekday)
            reconstructed_dict[d.date().strftime("%Y-%m-%d")] = int(matrix[weekday, week]) # althrough this is a datetime dict, everything stored as string

    return reconstructed_dict
  