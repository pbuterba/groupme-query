"""
@package groupme_api
@brief   Helper functions to manipulate time objects

@date    6/1/2024
@updated 6/1/2024

@author Preston Buterbaugh
"""
# Imports
from datetime import datetime
import time

# noinspection PyUnresolvedReferences
from groupme.common_utils import GroupMeException


def to_seconds(number: int, units: str) -> int:
    """
    @brief Converts a given number with given units to seconds
    @param number (int): The number to convert to seconds
    @param units (str): The units
        - "min" - Minutes
        - "h" - Hours
        - "d" - Days
        - "w" - Weeks
        - "m" - Months
        - "y" - Days
    @return (int) The number of seconds
    """
    if units == 'min':
        return number * 60
    elif units == 'h':
        return number * 3600
    elif units == 'd':
        return number * 3600 * 24
    elif units == 'w':
        return number * 3600 * 24 * 7
    elif units == 'm':
        curr_time = time.localtime(time.time())
        month = curr_time.tm_mon
        year = curr_time.tm_year
        months_to_subtract = number % 12
        years_to_subtract = number // 12
        cutoff_date = datetime(year - years_to_subtract, month - months_to_subtract, curr_time.tm_mday, curr_time.tm_hour, curr_time.tm_min, curr_time.tm_sec)
        return int(time.time() - cutoff_date.timestamp())
    elif units == 'y':
        curr_time = time.localtime(time.time())
        year = curr_time.tm_year
        cutoff_date = datetime(year - number, curr_time.tm_mon, curr_time.tm_mday, curr_time.tm_hour, curr_time.tm_min, curr_time.tm_sec)
        return int(time.time() - cutoff_date.timestamp())
    else:
        raise GroupMeException('Invalid units specified for last_used duration')


def to_twelve_hour_time(hour: int, minute: int, second: int) -> str:
    """
    @brief Converts 24 hour time to 12 hour time
    @param hour    (int): The hour in 24-hour time
    @param minute  (int): The minute
    @param second  (int): The second
    @return (str) The time in 12-hour time formatted as hh:mm:ss a
    """
    # Normalize hour
    if hour > 23:
        hour = hour % 24

    if hour == 0:
        return f'12:{str(minute).zfill(2)}:{str(second).zfill(2)} AM'
    elif hour < 12:
        return f'{hour}:{str(minute).zfill(2)}:{str(second).zfill(2)} AM'
    elif hour == 12:
        return f'12:{str(minute).zfill(2)}:{str(second).zfill(2)} PM'
    else:
        return f'{hour - 12}:{str(minute).zfill(2)}:{str(second).zfill(2)} PM'
