"""
@package groupme
@brief   A Python object implementation of the GroupMe API

@date    6/1/2024
@updated 6/1/2024

@author  Preston Buterbaugh
@credit  GroupMe API info: https://dev.groupme.com/docs/v3
"""
# Imports
from datetime import datetime
import json
import requests
from typing import List, Dict
import time

# Global variables
BASE_URL = 'https://api.groupme.com/v3'
TOKEN_POSTFIX = '?token='


class Chat:
    """
    @brief Represents a GroupMe chat
    """
    pass


class GroupMe:
    def __init__(self, token: str):
        """
        @brief Constructor
        @param token (str): The user's GroupMe API access token
        """
        url = f'{BASE_URL}/users/me{TOKEN_POSTFIX}{token}'
        response = requests.get(url)
        if response.status_code != 200:
            raise GroupMeException('Invalid access token')
        user_info = json.loads(response.text)['response']
        self.token = token
        self.name = user_info['name']
        self.email = user_info['email']
        self.phone_number = user_info['phone_number']

    def get_chat(self, chat_name: str) -> Chat:
        """
        @brief Returns an object for a chat
        @param chat_name (str): The name of the chat to return
        @return (Chat) A GroupMe chat object
        """
        pass

    def get_chats(self, last_used: str = '', verbose: bool = False) -> List:
        """
        @brief Returns a list of all the user's chats
        @param last_used (str): String specifying how recently the chat should have been used. If empty, all groups are fetched
        @param verbose (bool): If output should be printed showing progress
        @return (List) A list of GroupMe Chat objects
        """
        groups = []
        direct_messages = []

        # Determine cutoff (if applicable)
        cutoff = get_cutoff(last_used)

        # Get groups
        url = f'{BASE_URL}/groups{TOKEN_POSTFIX}{self.token}'
        params = {
            'page': 1,
            'per_page': 10,
            'omit': 'memberships'
        }

        # Loop through all group pages
        group_page = call_api(url, params=params, except_message='Unexpected error fetching groups')
        in_range = True
        while len(group_page) > 0 and in_range:
            # Loop over page
            for i, group in enumerate(group_page):
                # Check last sent message
                if cutoff:
                    last_sent_message = group['messages']['last_message_created_at']
                    if last_sent_message < cutoff:
                        in_range = False
                        break

                # Output progress if requested
                if verbose:
                    print(f'\rFetching groups ({(params["page"] - 1) * params["per_page"] + i + 1} retrieved)...', end='')

                # Add to list of groups
                groups.append(group)

            # Get next page
            params['page'] = params['page'] + 1
            group_page = call_api(url, params=params, except_message='Unexpected error fetching groups')

        if verbose:
            print()
        return groups


class GroupMeException(Exception):
    """
    @brief Exception to be thrown by the classes for the GroupMe API
    """
    pass


def call_api(url: str, params: Dict | None = None, except_message: str | None = None) -> List | Dict:
    """
    @brief Makes a get call to the API, handles errors, and returns extracted data
    @param url (str): The URL for the endpoint to which to make the API request
    @param params (Dict): Parameters to pass into the request
    @param except_message:
    @return:
    """
    # Handle optional parameter
    if params is None:
        params = {}
    if except_message is None:
        except_message = 'Unspecified error occurred'

    # Make API call
    response = requests.get(url, params=params)
    if response.status_code != 200:
        raise GroupMeException(except_message)
    return json.loads(response.text)['response']


def get_cutoff(last_used: str) -> int | None:
    if last_used == '':
        return None

    date_components = last_used.split('/')
    if len(date_components) == 1:
        # If specified as duration
        number = last_used[0:len(last_used) - 1]
        unit = last_used[len(last_used) - 1]
        try:
            number = int(number)
        except ValueError:
            raise GroupMeException('Invalid argument for argument "last_used"')
        timespan = to_seconds(number, unit)
    elif len(date_components) == 3:
        # If specified as date
        try:
            month = int(date_components[0])
            day = int(date_components[1])
            year = int(date_components[2])
        except ValueError:
            raise GroupMeException('Invalid argument for argument "last_used"')
        timespan = time.time() - float(datetime(year, month, day).timestamp())
    else:
        raise GroupMeException('Invalid argument for argument "last_used"')
    return int(time.time() - timespan)


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