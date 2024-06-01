"""
@package groupme
@brief   A Python object implementation of the GroupMe API

@date    6/1/2024
@updated 6/1/2024

@author  Preston Buterbaugh
@credit  GroupMe API info: https://dev.groupme.com/docs/v3
"""
# Imports
import json
import requests

# Global variables
BASE_URL = 'https://api.groupme.com/v3'
TOKEN_POSTFIX = '?token='


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


class GroupMeException(Exception):
    """
    @brief Exception to be thrown by the classes for the GroupMe API
    """
    pass
