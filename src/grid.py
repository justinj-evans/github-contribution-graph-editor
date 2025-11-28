import numpy as np

def df_to_8x52(df):
    """
    numpy returns array in 0-7, whereas writer.py uses range(8) -> 1-8
    so we need to add an empty row at the top.
    Returns:
        dict: np.ndarray: 8x52 array with an empty top row
    """
    arr7 = df.to_numpy()                   # (7, 52)
    empty = np.zeros((1, 52), dtype=int)   # (1, 52)
    return np.vstack([empty, arr7])        # (8, 52)