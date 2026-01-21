import numpy as np
import pandas as pd
from datetime import datetime

def df_to_matrix(df):
    """
    numpy returns array in 0-7, whereas writer.py uses range(8) -> 1-8
    so we need to add an empty row at the top.
    Returns:
        dict: np.ndarray: 8x52 array with an empty top row
    """
    arr7 = df.to_numpy()                   # (7, 52)
    empty = np.zeros((1, 52), dtype=int)   # (1, 52)
    return np.vstack([empty, arr7])        # (8, 52)


def dict_to_matrix(date_dict):
    matrix = np.zeros((7, 52), dtype=int)

    for date_str, count in date_dict.items():
        try:
            date = datetime.strptime(date_str, "%Y-%m-%d").date()

            weekday = date.weekday()
            week = date.isocalendar().week - 1

            matrix[weekday, week] = count
        except ValueError:
            continue

    return matrix

def matrix_to_dict(matrix, year):
    contrib_dict = {}
    start = pd.to_datetime(f"{year}-01-01")
    for week in range(52):
        for weekday in range(7):
            day = start + pd.to_timedelta(week*7 + weekday - start.weekday(), "D")
            if matrix[weekday, week] > 0:
                contrib_dict[str(day.date())] = int(matrix[weekday, week]) # force to int for json serialization, is num commits
    return contrib_dict