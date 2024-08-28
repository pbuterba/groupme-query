"""
@package querier
@brief   A script which allows the user to query GroupMe messages from different groups and times

@date    6/1/2024
@updated 8/27/2024

@author  Preston Buterbaugh
"""
# Imports
from argparse import ArgumentParser
import sys

from groupme import GroupMe, GroupMeException


def main(token: str) -> int:
    """
    @brief  Main entrypoint of the function
    @param  token (str): The users access token for the GroupMe API
    @return (int)
        - 0 if completed with no errors
        - 1 otherwise
    """
    # Log user in
    try:
        user = GroupMe(token)
    except GroupMeException:
        print(f'Invalid GroupMe access token {token}')
        return 1

    # Print user's name
    print(f'Successfully logged in {user.name}')
    messages = user.get_messages(sent_before='7/1/2024', sent_after='7/1/2024', verbose=True)
    for message in messages:
        print(f'{message.author} to {message.chat} at {message.time}: {message.text}')

    return 0


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument(dest='token', help='GroupMe API access token')
    parser.add_argument(dest='group', default=None, help='The name of a group to search')
    parser.add_argument(dest='start', default=None, help='The start of the message date range')
    parser.add_argument(dest='end', default=None, help='The end of the message date range')
    parser.add_argument(dest='keyword', default=None, help='A keyword to search for')
    parser.add_argument(dest='before', default=0, help='The number of messages before each matching message to retrieve')
    parser.add_argument(dest='after', default=0, help='The number of messages after each matching message to retrieve')
    args = parser.parse_args()
    sys.exit(main(args.token))
