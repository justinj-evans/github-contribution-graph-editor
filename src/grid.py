import numpy as np
import pandas as pd
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def df_to_matrix(df):
    """
    numpy returns array in 0-7, whereas writer.py uses range(8) -> 1-8
    so we need to add an empty row at the top.
    Returns:
        dict: np.ndarray: 8x52 array with an empty top row
    """
    arr7 = df.to_numpy()                   # (7, 52)
    empty = np.zeros((1, 52), dtype=int)   # (1, 52)
    return np.vstack([empty,arr7])        # (8, 52)


def dict_to_matrix(date_dict):
    matrix = np.zeros((7, 52), dtype=int)
    clamped_weeks = 0
    failed_dates = 0

    for date_str, count in date_dict.items():
        try:
            date = datetime.strptime(date_str, "%Y-%m-%d").date()

            weekday = date.weekday()
            iso_week = date.isocalendar().week
            
            # Clamp week to valid range [0, 51] to handle week 53 at year boundary
            week = min(iso_week - 1, 51)
            if week != iso_week - 1:
                clamped_weeks += 1
                logger.debug(f"Clamped week 53 date {date_str} to week {week}")

            matrix[weekday, week] = count
        except (ValueError, IndexError) as e:
            failed_dates += 1
            logger.warning(f"Failed to process date {date_str}: {e}")
            continue

    if clamped_weeks > 0:
        logger.info(f"Clamped {clamped_weeks} week 53 boundary dates to week 51")
    if failed_dates > 0:
        logger.warning(f"Failed to process {failed_dates} dates")
    
    return matrix

def matrix_to_dict(matrix, year):
    contrib_dict = {}
    start = pd.to_datetime(f"{year}-01-01")
    total_entries = 0
    zero_entries = 0
    
    for week in range(52):
        for weekday in range(0, 7):
            day = start + pd.to_timedelta(week*7 + weekday - start.weekday(), "D")
            # Include all days, even zero values, to preserve weekend data
            value = int(matrix[weekday, week])
            contrib_dict[str(day.date())] = value
            total_entries += 1
            if value == 0:
                zero_entries += 1
    
    logger.debug(f"Converted matrix to dict: {total_entries} total entries, {zero_entries} zeros, {total_entries - zero_entries} non-zero")
    assert total_entries == 364, f"matrix_to_dict should produce 364 entries, got {total_entries}"
    return contrib_dict