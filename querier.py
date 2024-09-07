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
from htmlwriter import Document, Node

# List of month names
MONTH_NAMES = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']


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

    # Check that there is at least one message
    if len(messages) == 0:
        print('No messages found')
        return 0

    # Create cover page
    cover_page = Document('GroupMe Query Results', css=['style.css'])

    # Create cover header
    header = Node('div', attributes={'class': 'header'})
    cover_title = Node('h1')
    cover_title_text = f'{user.name}\'s GroupMe messages'
    if start and end:
        cover_title_text = f'{cover_title_text} between {start} and {end}'
    elif start:
        cover_title_text = f'{cover_title_text} since {start}'
    elif end:
        cover_title_text = f'{cover_title_text} before {end}'

    if keyword:
        cover_title_text = f'{cover_title_text} containing "{keyword}"'

    cover_title.text_content = cover_title_text
    header.append_child(cover_title)
    cover_page.append_child(header)

    # Create body
    cover_container = Node('div', attributes={'class': 'container'})
    year_list = Node('ul', attributes={'class': 'year-list'})

    # Create starting variables for message time tracking
    curr_year = int(messages[0].time.split(' ')[0].split('/')[2])
    year_list.append_child(Node('li', content=str(curr_year)))

    curr_month = int(messages[0].time.split(' ')[0].split('/')[0])
    month_list = Node('ul', attributes={'class': 'month-list'})
    month_list.append_child(Node('li', content=MONTH_NAMES[curr_month - 1]))

    curr_day = int(messages[0].time.split(' ')[0].split('/')[1])
    curr_month_segment = calculate_month_segment(curr_day)
    month_segment_list = Node('ul', attributes={'class': 'start-date-list'})
    month_segment = Node('li', content=f'{MONTH_NAMES[curr_month - 1]} {curr_day}{day_suffix(curr_day)}')
    month_segment_link = Node('a')
    month_segment_link.href(f'{curr_year}/{str(curr_month).zfill(2)}-{MONTH_NAMES[curr_month - 1]}/{curr_month}-{curr_day}.html')
    month_segment_link.append_child(month_segment)
    month_segment_list.append_child(month_segment_link)

    for message in messages:
        # Check if new day
        pass

        # Check if new month segment
        pass

        # Check if new month
        pass

        # Check if new year
        if int(message.time.split(' ')[0].split('/')[2]) != curr_year:
            year_list.append_child(month_list)
            curr_year = int(message.time.split(' ')[0].split('/')[2])
            month_list = Node('ul', attributes={'class': 'month-list'})

    for message in messages:
        print(f'{message.author} to {message.chat} at {message.time}: {message.text}')

    return 0


def calculate_month_segment(day: int) -> int:
    """
    @brief  Gets the month segment that a day falls in
    @param  day (int): The day of the month
    @return (int) 1 if day is 1-10, 2 if day is 11-20, or 3 otherwise
    """
    if day < 11:
        return 1
    if day < 21:
        return 2
    return 3


def day_suffix(day: int) -> str:
    """
    @brief  Gets the two letter suffix to apply to a day of a month (st, nd, rd, th)
    @param  day (int): The day of the month
    @return (str) The appropriate suffix for the given day of the month
    """
    if str(day).endswith('1') and not str(day).endswith('11'):
        return 'st'
    if str(day).endswith('2') and not str(day).endswith('12'):
        return 'nd'
    if str(day).endswith('3') and not str(day).endswith('13'):
        return 'rd'
    return 'th'


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
