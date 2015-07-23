__author__ = 'Jono'

import re
import csv
from string import ascii_uppercase
from collections import OrderedDict

import httplib2
from oauth2client.client import OAuth2WebServerFlow
from apiclient.discovery import build
import os

lettnum = {'A': 1, 'C': 3, 'B': 2, 'E': 5, 'D': 4, 'G': 7, 'F': 6, 'I': 9, 'H': 8, 'K': 11, 'J': 10, 'M': 13, 'L': 12,
           'O': 15, 'N': 14, 'Q': 17, 'P': 16, 'S': 19, 'R': 18, 'U': 21, 'T': 20, 'W': 23, 'V': 22, 'Y': 25, 'X': 24,
           'Z': 26}

alphabet = ascii_uppercase


def get_flow(redir_url):
    return OAuth2WebServerFlow(
        client_id="1073328760463-khhs9gjebu8b390hkev8cgl9ht21kujt.apps.googleusercontent.com",
                        client_secret="VARRxnxF8UP6i5rSggSAYhzG",
                        scope="https://www.googleapis.com/auth/calendar",
                        redirect_uri=redir_url
    )


def get_google_redirect(redir_url):
    return get_flow(redir_url).step1_get_authorize_url()


def hasNumbers(inputString):
    return any(char.isdigit() for char in inputString)


def alphabet_range(x):
    x = x.split('-')
    start = lettnum[x[0]]
    end = lettnum[x[1]]
    rangelist = []
    for letter in alphabet:
        if start <= lettnum[letter] <= end:
            rangelist.append(letter)
    return rangelist

def create_timetable(PBL, PBLNUM):
    tt_temp = []
    tt_parsed = []
    PBL_combined = PBL + PBLNUM

#    with open('timetable/static/timetable/JMP Sem 2 Base.csv', mode='rb') as infile:
    try:
        with open('JMP Sem 2 Base.csv', mode='rb') as infile:
            reader = csv.reader(infile)
            for row in reader:
                tt_temp.append({'Wk': row[0], 'Day': row[1], 'Date': row[2], 'Time': row[3], 'Duration': row[4],
                                'Group': row[5], 'Venue': row[6], 'Session': row[7], 'Presenter': row[8], 'Course': row[9]})
            del tt_temp[0]
    except:
        files = [f for f in os.listdir('.') if os.path.isfile(f)]
        raise Exception(str(files))

    for event in tt_temp:
        if event['Group'] == 'All':
            tt_parsed.append(event)
            continue
        else:
            group = event['Group'].replace(" ", "").split("+")
            for item in group:
                # If the full PBL group is present, add the event
                if item == PBL:
                    tt_parsed.append(event)
                    continue
                # If the user's specific Group number is present, add event
                elif item == PBL_combined:
                    tt_parsed.append(event)
                    continue
                # Check if part of the PBL group is present
                elif PBL in item:
                    if '-' in item:
                        if hasNumbers(item):
                            # Item includes numbers so it'll look something like "B2-B6"
                            item = re.sub("[A-Z]", "", item)
                            item_range = item.split('-')
                            # After stripping letters and making a list with the lower and upper bounds, check if PBL number
                            # exists somewhere in the range specified by the item
                            if int(PBLNUM) in xrange(int(item_range[0]), int(item_range[1])):
                                tt_parsed.append(event)
                                continue
                        else:
                            if PBL in alphabet_range(item):
                                tt_parsed.append(event)
                                continue
                    else:
                        # In this case, the PBL Group is matching but the item specifies a single student number which
                        # doesn't match the PBL number given. In other words we pass, not append.
                        pass
                elif '-' in item and not hasNumbers(item):
                    if PBL in alphabet_range(item):
                        tt_parsed.append(event)
                        continue

    tt_temp = tt_parsed
    tt_parsed = []
    start_time = None
    end_time = None

    for event in tt_temp:
        time = event['Time'].split('-')
        if 'am' in time[0]:
            start_time = time[0].strip().strip('am') + ' AM'
        elif 'pm' in time[0]:
            start_time = time[0].strip().strip('pm') + ' PM'
        if 'am' in time[1]:
            end_time = time[1].strip().strip('am') + ' AM'
        elif 'pm' in time[1]:
            end_time = time[1].strip().strip('pm') + ' PM'
        start_time = start_time.replace('.', ':')
        end_time = end_time.replace('.', ':')
        description = event['Course'] + ' - ' + event['Presenter'] + ' - ' + 'Week ' + event['Wk'] + ' - ' + event['Duration'] + ' hour(s) long.'
        event.update({'Start Time': start_time})
        event.update({'End Time': end_time})
        event.update({'Description': description})
        start_time = None
        end_time = None

    for event in tt_temp:
        ordered_dictionary = OrderedDict((('Subject', event['Session'].strip('\n')),
                                                      ('Start Date', event['Date'].strip('\n')),
                                                      ('Start Time', event['Start Time'].strip('\n')),
                                                      ('End Date', event['Date'].strip('\n')),
                                                      ('End Time', event['End Time'].strip('\n')),
                                                      ('All Day Event', ''.strip('\n')),
                                                      ('Description', event['Description'].strip('\n')),
                                                      ('Location', event['Venue'].strip('\n')),
                                                      ('Private', ''.strip('\n'))
                                                      ))
        tt_parsed.append(ordered_dictionary)

    return tt_parsed


def convert_date_time(date, time):
    ampm = time.split()[1]
    time = time.split()[0]
    try:
        mins = time.split(':')[1]
    except IndexError:
        time = time.replace('.', ':')
        mins = time.split(':')[1]
    hour = time.split(':')[0]
    day = date.split('/')[0]
    month = date.split('/')[1]
    year = date.split('/')[2]
    if ampm == "PM" and hour != "12":
        # Convert to 24hr time
        hour = str(int(hour)+12)
        return '{year}-{month}-{day}T{hour}:{mins}:00.000'.format(year=year, month=month, day=day, hour=hour, mins=mins)
    elif ampm == "PM" and hour == "12":
        # Already in 24hr time, don't touch
        hour = hour
        return '{year}-{month}-{day}T{hour}:{mins}:00.000'.format(year=year, month=month, day=day, hour=hour, mins=mins)
    elif ampm == "AM" and hour != "12":
        # Already in 24hr time, though make sure that numbers less than 10 are prefixed with a zero.
        if int(hour) < 10 and '0' not in hour:
            hour = '0' + hour
            assert (len(hour) == 2), "Hours not in correct format, length is {0} which is greater than 2.".format(
                str(len(hour))
            )
        return '{year}-{month}-{day}T{hour}:{mins}:00.000'.format(year=year, month=month, day=day, hour=hour, mins=mins)
    elif ampm == "AM" and hour == "12":
        # Convert to 24hr time
        hour = str(int(hour)+12)
        return '{year}-{month}-{day}T{hour}:{mins}:00.000'.format(year=year, month=month, day=day, hour=hour, mins=mins)
    else:
        raise Exception('Something\'s broken with the date-time parsing again...')







def convert_to_google_format(event):
    event_dictionary = {
        'summary': event['Subject'],
        'location': event['Location'],
        'description': event['Description'],
        'start': {
            'dateTime': convert_date_time(event['Start Date'], event['Start Time']),
            'timeZone': 'Australia/Sydney',
        },
        'end': {
            'dateTime': convert_date_time(event['End Date'], event['End Time']),
            'timeZone': 'Australia/Sydney',
        },
    }
    print event_dictionary['start']['dateTime']
    print event_dictionary['end']['dateTime']
    return event_dictionary


def export_calendar(auth_code, calendar_dict, redir_url, calendar_title):
    print redir_url
    creds = get_flow(redir_url).step2_exchange(auth_code)
    http = httplib2.Http()
    http = creds.authorize(http)
    service = build('calendar', 'v3', http=http)
    calendar = {
        'summary': calendar_title,
        'timezone': 'Australia/Sydney',
    }
    created_calendar = service.calendars().insert(body=calendar).execute()
    created_calendar_id = str(created_calendar['id'])
    print 'Calendar ID: {0}'.format(created_calendar_id)
    for event in calendar_dict:
        service.events().insert(calendarId=created_calendar_id, body=convert_to_google_format(event)).execute()


def make_csv(calendar_dict):
    keys = calendar_dict[0].keys()
    with open('static/media/timetable.csv', 'wb') as outfile:
        dict_writer = csv.DictWriter(outfile, keys)
        dict_writer.writeheader()
        dict_writer.writerows(calendar_dict)

def main():
    PBL = raw_input("PBL?\n")
    PBLNUM = raw_input("PBL Number?\n")
    assert (PBL in list(alphabet)), "Please input an uppercase letter for your PBL group."
    assert (PBLNUM in ['1', '2', '3', '4', '5', '6', '7', '8', '9']), "Please input an integer from 1-9 for your group number."

    tt_finished = create_timetable(PBL, PBLNUM)
    keys = tt_finished[0].keys()
    with open('timetable.csv', 'wb') as outfile:
        dict_writer = csv.DictWriter(outfile, keys)
        dict_writer.writeheader()
        dict_writer.writerows(tt_finished)
