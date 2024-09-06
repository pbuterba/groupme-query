"""
@package querier
@brief   A script which allows the user to query GroupMe messages from different groups and times

@date    6/1/2024
@updated 9/5/2024

@author  Preston Buterbaugh
"""
# Imports
from argparse import ArgumentParser
import sys

from groupme import GroupMe, GroupMeException


def main(token: str, chat_name: str | None, start: str | None, end: str | None, keyword: str | None, before: int, after: int) -> int:
    """
    @brief  Main entrypoint of the function
    @param  token        (str): The users access token for the GroupMe API
    @param  chat_name    (str): The name of the group or direct message to search. If none, all groups are searched
    @param  start        (str): A date specified as a string, which determines the start of the time window to search
                                if None, all messages back to the beginning of the user's history are searched
    @param  end          (str): A date specified as a string, which determines the end of the time window to search
                                If None, all messages up to the present date are searched
    @param  keyword      (str): A string to search for, such that only messages with this string of text are returned
                                If None, all messages within the time window are returned
    @param  before       (int): The number of messages to fetch immediately proceeding each message matching search criteria
    @param  after        (int): The number of messages to fetch immediately after each message matching search criteria
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

    # Check if chat was specified
    if chat_name:
        try:
            chat = user.get_chat(chat_name)
        except GroupMeException:
            print(f'{user.name} has no chat called "{chat_name}"')
            return 1
        messages = chat.get_messages(sent_before=end, sent_after=start, keyword=keyword, before=before, after=after, verbose=True)
    else:
        messages = user.get_messages(sent_before=end, sent_after=start, keyword=keyword, before=before, after=after, verbose=True)
    for message in messages:
        print(f'{message.author} to {message.chat} at {message.time}: {message.text}')

    return 0


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument(dest='token', help='GroupMe API access token')
    parser.add_argument('-g', dest='group', default=None, help='The name of a group to search')
    parser.add_argument('--start', dest='start', default='', help='The start of the message date range')
    parser.add_argument('--end', dest='end', default='', help='The end of the message date range')
    parser.add_argument('--keyword', dest='keyword', default='', help='A keyword to search for')
    parser.add_argument('--before', dest='before', default=0, help='The number of messages before each matching message to retrieve')
    parser.add_argument('--after', dest='after', default=0, help='The number of messages after each matching message to retrieve')
    args = parser.parse_args()
    sys.exit(main(args.token, args.group, args.start, args.end, args.keyword, args.before, args.after))
