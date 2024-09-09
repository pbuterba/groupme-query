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
from typing import List

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

    # Create variables for tracking year
    curr_year = int(messages[0].time.split(' ')[0].split('/')[2])
    year_list.append_child(Node('li', content=str(curr_year)))

    # Create variables for tracking month
    curr_month = int(messages[0].time.split(' ')[0].split('/')[0])
    month_list = Node('ul', attributes={'class': 'month-list'})
    month_list.append_child(Node('li', content=MONTH_NAMES[curr_month - 1]))

    # Create variables for tracking day
    curr_day = int(messages[0].time.split(' ')[0].split('/')[1])
    curr_month_segment = calculate_month_segment(curr_day)
    month_segment_list = Node('ul', attributes={'class': 'start-date-list'})
    month_segment = Node('li', content=f'{MONTH_NAMES[curr_month - 1]} {curr_day}{day_suffix(curr_day)}')
    month_segment_link = Node('a')
    month_segment_link.href(f'{curr_year}/{str(curr_month).zfill(2)}-{MONTH_NAMES[curr_month - 1]}/{curr_month}-{curr_day}.html')
    month_segment_link.append_child(month_segment)
    month_segment_list.append_child(month_segment_link)
    day_page = new_day_page(messages[0].time.split(' ')[0], user.name, start_date=messages[0].time.split(' ')[0])

    # Create variables for tracking group
    curr_group = messages[0].group
    chat_div = Node('div', attributes={'class': 'chat'})

    for message in messages:
        # Check if new group
        pass

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


def new_day_page(date: str, username: str, start_date: str = '') -> Document:
    """
    @brief  Creates a new HTML page for a day's results
    @param  date       (str): The date for which the page is being created, formatted as MM/dd/yyyy
    @param  username   (str): The user's name
    @param  start_date (str): If the segment is partial, and should start on a non-standard date, this specifies what
                              date it should start on. If unspecified, starts at normal beginning of month segment
    @return (Document) An HTML document containing the page with all boilerplate code in place
    """
    curr_month = int(date.split('/')[0])
    curr_day = int(date.split('/')[1])
    curr_year = int(date.split('/')[2])
    if not start_date:
        start_date = month_segment_start(curr_month, curr_day, curr_year)
    page = Document(f'Messages {start_date}-{month_segment_end(curr_month, curr_day, curr_year)}', css=['style.css'])
    header = Node('div', attributes={'class': 'header'})
    title = Node('h1', content=f'{username}\'s GroupMe messages between {start_date} and {month_segment_end(curr_month, curr_day, curr_year)}')
    header.append_child(title)
    segment_days = get_segment_days(start_date)
    for day in segment_days:
        month = day.split('-')[0]
        day_num = day.split('-')[1]
        nav_div = Node('div', attributes={'class': 'nav'}, content=f'{MONTH_NAMES[month - 1]} {day_num}{day_suffix(day_num)}')
        nav_link = Node('a', attributes={'href': f'{day}.html'})
        nav_link.append_child(nav_div)
        header.append_child(nav_link)
    page.append_child(header)
    container = Node('div', attributes={'class': 'container'})
    page.append_child(container)
    return page


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


def month_segment_start(month: int, day: int, year: int) -> str:
    """
    @brief  Gives the string format of the first day of the month segment for a given day
    @param  month (int): The month of the date to check
    @param  day   (int): The day within the month of the date to check
    @param  year  (int): The year of the date to check
    @return (str) The date that is the start of the month segment of the input date, formatted as MM/dd/yyyy
    """
    if day < 11:
        return f'{month}/1/{year}'
    elif day < 21:
        return f'{month}/11/{year}'
    else:
        return f'{month}/21/{year}'


def month_segment_end(month: int, day: int, year: int) -> str:
    """
    @brief  Gives the string format of the last day of the month segment for a given day
    @param  month (int): The month of the date to check
    @param  day   (int): The day within the month of the date to check
    @param  year  (int): The year of the date to check
    @return (str) The date that is the end of the month segment of the input date, formatted as MM/dd/yyyy
    """
    if day < 11:
        return f'{month}/10/{year}'
    elif day < 21:
        return f'{month}/20/{year}'
    elif month in [4, 6, 9, 11]:
        return f'{month}/30/{year}'
    elif month != 2:
        return f'{month}/31/{year}'
    elif year % 4 == 0 and (year % 100 != 0 or year % 400 == 0):
        return f'{month}/29/{year}'
    else:
        return f'{month}/28/{year}'


def get_segment_days(start_date: str) -> List:
    """
    @brief  Returns a list of days from the given start date to the end of its month segment
    @param  start_date (str): The date at which to start the list
    @return (List) A list of days, as strings formatted as "MM-dd"
    """
    start_month = int(start_date.split('/')[0])
    start_day = int(start_date.split('/')[1])
    start_year = int(start_date.split('/')[2])

    end_day = int(month_segment_end(start_month, start_day, start_year).split('/')[1])
    day_list = []
    for day in range(start_day, end_day + 1):
        day_list.append(f'{start_month}-{day}')
    return day_list


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
