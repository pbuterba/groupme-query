"""
@package querier
@brief   A script which allows the user to query GroupMe messages from different groups and times

@date    6/1/2024
@updated 12/20/2024

@author  Preston Buterbaugh
"""
# Imports
from argparse import ArgumentParser
import os
import sys
from typing import List

from groupme import GroupMe, Message, GroupMeException
from htmlwriter import Document, Node

# List of month names
MONTH_NAMES = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

# Create dictionary to cache group avatars
group_avatars = {}


def main(token: str, chat_name: str | None, start: str | None, end: str | None, keyword: str | None, before: int, after: int, output_directory: str | None) -> int:
    """
    @brief  Main entrypoint of the function
    @param  token            (str): The users access token for the GroupMe API
    @param  chat_name        (str): The name of the group or direct message to search. If none, all groups are searched
    @param  start            (str): A date specified as a string, which determines the start of the time window to search
                                    if None, all messages back to the beginning of the user's history are searched
    @param  end              (str): A date specified as a string, which determines the end of the time window to search
                                    If None, all messages up to the present date are searched
    @param  keyword          (str): A string to search for, such that only messages with this string of text are returned
                                    If None, all messages within the time window are returned
    @param  before           (int): The number of messages to fetch immediately proceeding each message matching search criteria
    @param  after            (int): The number of messages to fetch immediately after each message matching search criteria
    @param  output_directory (str): The directory to which to write output files. If None, the current directory is used
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

    # Read stylesheets
    style_file = open('cover_style.css')
    cover_style = style_file.readlines()
    style_file.close()

    style_file = open('page_style.css')
    page_style = style_file.readlines()
    style_file.close()

    # Change directory
    if output_directory is not None:
        os.chdir(output_directory)

    # Create cover stylesheet
    style_file = open('style.css', 'w')
    style_file.writelines(cover_style)
    style_file.close()

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

    cover_title.text_content(cover_title_text)
    header.append_child(cover_title)
    cover_page.append_child(header)

    # Create body
    cover_container = Node('div', attributes={'class': 'container'})
    year_list = Node('ul', attributes={'class': 'year-list'})

    # Create variables for tracking year
    curr_year = int(messages[0].time.split(' ')[0].split('/')[2])
    try:
        os.mkdir(str(curr_year))
    except FileExistsError:
        input(f'Output directory already contains a file or directory called {curr_year}. Delete existing folder and press ENTER to continue')
        os.mkdir(str(curr_year))
    year_list.append_child(Node('li', content=str(curr_year)))

    # Create variables for tracking month
    curr_month = int(messages[0].time.split(' ')[0].split('/')[0])
    month_list = Node('ul', attributes={'class': 'month-list'})
    month_list.append_child(Node('li', content=MONTH_NAMES[curr_month - 1]))

    # Create month directory and stylesheet
    os.mkdir(f'{curr_year}/{str(curr_month).zfill(2)}-{MONTH_NAMES[curr_month - 1]}')
    style_file = open(f'{curr_year}/{str(curr_month).zfill(2)}-{MONTH_NAMES[curr_month - 1]}/style.css', 'w')
    style_file.writelines(page_style)
    style_file.close()

    # Create variables for tracking day
    curr_day = int(messages[0].time.split(' ')[0].split('/')[1])
    print(f'\rProcessing {MONTH_NAMES[curr_month - 1]} {curr_day}{day_suffix(curr_day)}, {curr_year}...', end='')
    day_page = new_day_page(messages[0].time.split(' ')[0], user.name, start_date=messages[0].time.split(' ')[0])

    # Create variables for tracking month segments
    curr_month_segment = calculate_month_segment(curr_day)
    segment_pages = []

    # Initialize month segment list on cover page
    month_segment_list = Node('ul', attributes={'class': 'start-date-list'})
    month_segment = Node('li', content=f'{MONTH_NAMES[curr_month - 1]} {curr_day}{day_suffix(curr_day)}')
    month_segment_link = Node('a')
    month_segment_link.href(f'{curr_year}/{str(curr_month).zfill(2)}-{MONTH_NAMES[curr_month - 1]}/{curr_month}-{str(curr_day).zfill(2)}.html')
    month_segment_link.append_child(month_segment)
    month_segment_list.append_child(month_segment_link)

    # Create variables for tracking chat
    curr_chat = messages[0].chat
    chat_div = Node('div', attributes={'class': 'chat'})

    # Create chat header
    chat_header = create_chat_header(user, messages[0])
    chat_div.append_child(chat_header)

    # Create message container
    message_container = Node('div', attributes={'class': 'messages'})
    
    for message in messages:
        # Check if new chat or new day
        if message.chat != curr_chat or int(message.time.split(' ')[0].split('/')[1]) != curr_day:
            # End current chat
            chat_div.append_child(message_container)
            container = day_page.get_by_class_name('container')[0]
            container.append_child(chat_div)

            # Check if new day
            if int(message.time.split(' ')[0].split('/')[1]) != curr_day:
                # Add current day page to list
                segment_pages.append((curr_day, day_page))

                # Check if new month segment
                if calculate_month_segment(int(message.time.split(' ')[0].split('/')[1])) != curr_month_segment:
                    # Process current month segment day pages
                    for day, page in segment_pages:
                        header = page.get_by_class_name('header')[0]
                        for nav_day, _ in segment_pages:
                            tab = Node('div', attributes={'class': 'nav'}, content=f'{MONTH_NAMES[curr_month - 1]} {nav_day}{day_suffix(nav_day)}')
                            if nav_day == day:
                                tab.id('selected')
                            tab_link = Node('a', attributes={'href': f'{curr_month}-{str(nav_day).zfill(2)}.html'})
                            tab_link.append_child(tab)
                            header.append_child(tab_link)
                        page.export(f'{curr_year}/{str(curr_month).zfill(2)}-{MONTH_NAMES[curr_month - 1]}/{curr_month}-{str(day).zfill(2)}.html')

                    # Check if new month
                    if int(message.time.split(' ')[0].split('/')[0]) != curr_month:
                        # End current month segment list
                        month_list.append_child(month_segment_list)

                        # Check if new year
                        if int(message.time.split(' ')[0].split('/')[2]) != curr_year:
                            # End current month list
                            year_list.append_child(month_list)

                            # Update current year
                            curr_year = int(message.time.split(' ')[0].split('/')[2])

                            # Create new year directory
                            try:
                                os.mkdir(str(curr_year))
                            except FileExistsError:
                                input(f'Output directory already contains a file or directory called {curr_year}. Delete existing folder and press ENTER to continue')
                                os.mkdir(str(curr_year))

                            # Create new month list
                            year_list.append_child(Node('li', content=str(curr_year)))
                            month_list = Node('ul', attributes={'class': 'month-list'})

                        # Update current month
                        curr_month = int(message.time.split(' ')[0].split('/')[0])

                        # Create new month directory and stylesheet
                        os.mkdir(f'{curr_year}/{str(curr_month).zfill(2)}-{MONTH_NAMES[curr_month - 1]}')
                        style_file = open(f'{curr_year}/{str(curr_month).zfill(2)}-{MONTH_NAMES[curr_month - 1]}/style.css', 'w')
                        style_file.writelines(page_style)
                        style_file.close()

                        # Create new month segment list
                        month_list.append_child(Node('li', content=MONTH_NAMES[curr_month - 1]))
                        month_segment_list = Node('ul', attributes={'class': 'start-date-list'})

                    # Update current month segment
                    curr_month_segment = calculate_month_segment(int(message.time.split(' ')[0].split('/')[1]))

                    # Create new month segment
                    curr_day = int(message.time.split(' ')[0].split('/')[1])
                    month_segment = Node('li', content=f'{MONTH_NAMES[curr_month - 1]} {curr_day}{day_suffix(curr_day)}')
                    month_segment_link = Node('a')
                    month_segment_link.href(f'{curr_year}/{str(curr_month).zfill(2)}-{MONTH_NAMES[curr_month - 1]}/{curr_month}-{str(curr_day).zfill(2)}.html')
                    month_segment_link.append_child(month_segment)
                    month_segment_list.append_child(month_segment_link)
                    segment_pages = []

                # Update current day
                curr_day = int(message.time.split(' ')[0].split('/')[1])
                print(f'\rProcessing {MONTH_NAMES[curr_month - 1]} {curr_day}{day_suffix(curr_day)}, {curr_year}...', end='')

                # Create new day
                day_page = new_day_page(message.time.split(' ')[0], user.name)

            # Update current chat
            curr_chat = message.chat

            # Create new chat
            chat_div = Node('div', attributes={'class': 'chat'})
            chat_header = create_chat_header(user, message)
            chat_div.append_child(chat_header)
            message_container = Node('div', attributes={'class': 'messages'})

        # Process message
        message_node = Node('div', attributes={'class': 'message'})
        metadata = Node('div', attributes={'class': 'message-metadata'})

        # Create author info
        author_info = Node('div', attributes={'class': 'author-info'})
        if message.author_profile_picture_url:
            author_profile = Node('img', attributes={'src': message.author_profile_picture_url})
        else:
            author_profile = Node('div', attributes={'class': 'no-pic'}, content='No profile picture')
        author_name = Node('h3', content=message.author)
        author_info.append_child(author_profile)
        author_info.append_child(author_name)
        metadata.append_child(author_info)

        # Create timestamp
        timestamp = Node('div', attributes={'class': 'timestamp'}, content=''.join(message.time.split(' ')[1:]))
        metadata.append_child(timestamp)

        message_node.append_child(metadata)

        # Process message text
        if message.text is not None:
            message_text = filter_text(message.text)
            message_node.append_child(Node('p', content=message_text))

        message_container.append_child(message_node)

    print('\rMessage processing complete')

    # Finish appending and exporting all files

    # Add chat onto end of day
    chat_div.append_child(message_container)
    container = day_page.get_by_class_name('container')[0]
    container.append_child(chat_div)

    # Add day to segment pages list
    segment_pages.append((curr_day, day_page))

    # Process segment pages
    for day, page in segment_pages:
        header = page.get_by_class_name('header')[0]
        for nav_day, _ in segment_pages:
            tab = Node('div', attributes={'class': 'nav'},
                       content=f'{MONTH_NAMES[curr_month - 1]} {nav_day}{day_suffix(nav_day)}')
            if nav_day == day:
                tab.id('selected')
            tab_link = Node('a', attributes={'href': f'{curr_month}-{str(nav_day).zfill(2)}.html'})
            tab_link.append_child(tab)
            header.append_child(tab_link)
        page.export(f'{curr_year}/{str(curr_month).zfill(2)}-{MONTH_NAMES[curr_month - 1]}/{curr_month}-{str(day).zfill(2)}.html')

    # Finish updating cover
    month_list.append_child(month_segment_list)
    year_list.append_child(month_list)

    cover_container.append_child(year_list)
    cover_page.append_child(cover_container)

    cover_page.export('cover.html')

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
    page.append_child(header)
    container = Node('div', attributes={'class': 'container'})
    page.append_child(container)
    return page


def create_chat_header(user: GroupMe, message_data: Message) -> Node:
    """
    @brief  Creates a new chat header node based on the data contained in a message sent to that chat
    @param  user         (GroupMe) The GroupMe object representing the user whose messages are being processed
    @param  message_data (str)     The message data being used to create the chat header
    @return (Node) The div node representing the chat header
    """
    chat_header = Node('div', attributes={'class': 'chat-header'})
    global group_avatars
    if message_data.chat in group_avatars.keys():
        chat_avatar = group_avatars[message_data.chat]
    else:
        if message_data.is_group:
            chat_data = user.get_chat(message_data.chat)
        else:
            chat_data = user.get_chat(message_data.chat, is_dm=True)
        chat_avatar = chat_data.image_url
        group_avatars[message_data.chat] = chat_avatar

    if chat_avatar:
        chat_img = Node('img', attributes={'src': chat_avatar})
    else:
        chat_img = Node('div', attributes={'class': 'no-pic'}, content='No picture')

    if not message_data.is_group:
        chat_img.add_class('dm-img')
    chat_header.append_child(chat_img)
    chat_header.append_child(Node('h2', content=message_data.chat))
    return chat_header


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


def filter_text(text: str) -> str:
    """
    @brief  Replaces unicode encodings in the form of \\uXXXX with appropriate HTML characters
    @param  text (str): The text as received from the GroupMe API
    @return (str) The text prepared for presentation in HTML
    """
    replacements = {
        '\u2014': '-',
        '\u2019': '&rsquo;',
        '\u201c': '&ldquo;',
        '\u201d': '&rdquo;',
        '\u2026': '...'
    }
    for unicode_char in replacements.keys():
        text = text.replace(f'{unicode_char}', replacements[unicode_char])
    # for i in range(len(text) - 1):
    #     if text[i:i + 2] == '\\u':
    #         print(f'Uncaught unicode character: {text[i + 2:i + 6]}')
    return text


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument(dest='token', help='GroupMe API access token')
    parser.add_argument('-g', dest='group', default=None, help='The name of a group to search')
    parser.add_argument('--start', dest='start', default='', help='The start of the message date range')
    parser.add_argument('--end', dest='end', default='', help='The end of the message date range')
    parser.add_argument('--keyword', dest='keyword', default='', help='A keyword to search for')
    parser.add_argument('--before', dest='before', default=0, help='The number of messages before each matching message to retrieve')
    parser.add_argument('--after', dest='after', default=0, help='The number of messages after each matching message to retrieve')
    parser.add_argument('-o', dest='output_directory', default=None, help='The directory to which to write all output files from the query')
    args = parser.parse_args()
    sys.exit(main(args.token, args.group, args.start, args.end, args.keyword, args.before, args.after, args.output_directory))
