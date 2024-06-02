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
    @brief Interface representing a GroupMe chat
    """
    def __init__(self):
        """
        @brief Constructor. Defaults all fields to None, since generic Chat objects are not created
        """
        self.name = None
        self.description = None
        self.last_used = None

    def last_used_time(self) -> str:
        """
        @brief Returns the last time the chat was used, formatted as a string
        @return (str) The timestamp formatted MM/dd/yyyy hh:mm:ss
        """
        obj = time.localtime(self.last_used)
        return f'{obj.tm_mon}/{obj.tm_mday}/{obj.tm_year} {to_twelve_hour_time(obj.tm_hour, obj.tm_min, obj.tm_sec)}'


class Group(Chat):
    """
    @brief Represents a GroupMe group
    """
    def __init__(self, data: Dict):
        """
        @brief Constructor
        @param data (Dict): Dictionary of data representing the group as returned from a query
        """
        super().__init__()
        self.name = data['name']
        self.description = data['description']
        self.last_used = data['messages']['last_message_created_at']


class DirectMessage(Chat):
    """
    @brief Represents a GroupMe direct message thread
    """
    def __init__(self, data: Dict):
        """
        @brief Constructor
        @param data (Dict): Dictionary of data representing the direct message chat as returned from a query
        """
        super().__init__()
        self.name = data['other_user']['name']
        self.last_used = data['last_message']['created_at']


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
        chats = []

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
                groups.append(Group(group))

            # Get next page
            params['page'] = params['page'] + 1
            group_page = call_api(url, params=params, except_message='Unexpected error fetching groups')

        if verbose:
            print()

        # Get direct messages
        url = f'{BASE_URL}/chats{TOKEN_POSTFIX}{self.token}'
        params = {
            'page': 1,
            'per_page': 10
        }

        # Loop through all direct message pages
        dm_page = call_api(url, params=params, except_message='Unexpected error fetching direct messages')
        in_range = True
        num_chats = 0
        while len(dm_page) > 0 and in_range:
            # Loop over page
            for i, dm in enumerate(dm_page):
                # Check last sent message
                if cutoff:
                    last_sent_message = dm['last_message']['created_at']
                    if last_sent_message < cutoff:
                        in_range = False
                        break

                # Output progress if requested
                if verbose:
                    num_chats = num_chats + 1
                    print(f'\rFetching direct messages ({num_chats} retrieved)...', end='')

                # Add to list of groups
                direct_messages.append(DirectMessage(dm))

            # Get next page
            params['page'] = params['page'] + 1
            dm_page = call_api(url, params=params, except_message='Unexpected error fetching direct messages')

        if verbose:
            print()

        # Merge lists
        group_index = 0
        dm_index = 0
        while group_index < len(groups) and dm_index < len(direct_messages):
            if groups[group_index].last_used > direct_messages[dm_index].last_used:
                chats.append(groups[group_index])
                group_index = group_index + 1
            else:
                chats.append(direct_messages[dm_index])
                dm_index = dm_index + 1
        if group_index == len(groups):
            while dm_index < len(direct_messages):
                chats.append(direct_messages[dm_index])
                dm_index = dm_index + 1
        else:
            while group_index < len(groups):
                chats.append(groups[group_index])
                group_index = group_index + 1

        return chats


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
