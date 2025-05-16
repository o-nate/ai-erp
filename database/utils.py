"""Database utilities"""

from datetime import datetime, time


def validate_date(date_to_validate):
    if isinstance(date_to_validate, datetime):
        return date_to_validate

    for day in ["%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%SZ"]:
        try:
            return datetime.strptime(date_to_validate, day)
        except ValueError:
            pass

    raise ValueError("Invalid date format")


def validate_time(time_to_validate):
    if isinstance(time_to_validate, time):
        return time_to_validate

    if isinstance(time_to_validate, str):
        try:
            return time.fromisoformat(time_to_validate)
        except ValueError:
            raise ValueError("Invalid time format")


def numeric_validator(value_to_validate):
    if isinstance(value_to_validate, int):
        return float(value_to_validate)
    if isinstance(value_to_validate, float):
        return value_to_validate
    raise ValueError("Value must be a number")
