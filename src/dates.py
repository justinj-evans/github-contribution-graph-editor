from datetime import datetime, timedelta

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
