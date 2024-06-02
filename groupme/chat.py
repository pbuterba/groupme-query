"""
@package groupme_api
@brief   Classes to represent different kinds of GroupMe chats

@date    6/1/2024
@updated 6/1/2024

@author Preston Buterbaugh
@credit  GroupMe API info: https://dev.groupme.com/docs/v3
"""
# Imports
import time
from typing import Dict

# noinspection PyUnresolvedReferences
from groupme.time_functions import to_twelve_hour_time


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
