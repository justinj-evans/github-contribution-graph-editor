from datetime import datetime, timedelta
import requests
import pandas as pd

def year_dict() -> dict:
    """
    GitHub-accurate date dictionary:
    - 364 days = 52 weeks × 7 days
    - Ends today
    - Starts on the same weekday as today
    """
    today = datetime.now().date()

    # 364 days before today
    days_back = 364
    target_day = today - timedelta(days=days_back)

    # Align to the start of that ISO week (Monday = 0)
    start_of_week = target_day - timedelta(days=target_day.weekday())

    date_dict = {}
    for i in range(364):
        day = start_of_week + timedelta(days=i)
        date_dict[day.strftime("%Y-%m-%d")] = 0

    return date_dict

def github_contribution_api(username: str, year: str = "last") -> dict:
    """API for pulling Github Usernames
     Source repo: https://github.com/grubersjoe/github-contributions-api

    Args:
        username (str): Github Username
        year (str, optional): One year of github contributions to pull. Defaults to "last".

    Returns:
        dict: date : contribution count
    """
    # extract data from the GitHub Contributions API
    try:
        url = f"https://github-contributions-api.jogruber.de/v4/{username}?y={year}"
        resp = requests.get(url, timeout=30)
        return resp.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from GitHub Contributions API: {e}")
        return {}

def convert_api_response_to_dict(resp: dict) -> dict:
    # convert API data from response dict -> DataFrame -> formatted dict
    df = pd.DataFrame(resp['contributions'])
    date_dict = {}
    for index, row in df.iterrows():
        date_dict[row['date']] = row['count']

    return date_dict

def safe_date_dict_merge(source_dict:dict, supplied_dict: dict):
    # we don't assume API will return all keys/dates correctly, so we update only from the supplied dict
    # missing API dates will simply remain as 0 in the source dict
    [source_dict.update({k:v}) for k,v in supplied_dict.items()]
    return source_dict