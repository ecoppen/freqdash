from datetime import datetime, timedelta


def start_datetime_ago(days: int) -> str:
    start_datetime = datetime.combine(
        datetime.now() - timedelta(days=days), datetime.min.time()
    )
    return start_datetime.strftime("%Y-%m-%d %H:%M:%S")


def end_datetime_ago(days: int) -> str:
    start_datetime = datetime.combine(
        datetime.now() - timedelta(days=days), datetime.max.time()
    )
    return start_datetime.strftime("%Y-%m-%d %H:%M:%S")
