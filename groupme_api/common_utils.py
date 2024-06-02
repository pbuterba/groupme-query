"""
@package groupme_api
@brief   General purpose utilities for the GroupMe API

@date    6/1/2024
@updated 6/1/2024

@author Preston Buterbaugh
"""

# Global variables
BASE_URL = 'https://api.groupme.com/v3'
TOKEN_POSTFIX = '?token='


class GroupMeException(Exception):
    """
    @brief Exception to be thrown by the classes for the GroupMe API
    """
    pass
