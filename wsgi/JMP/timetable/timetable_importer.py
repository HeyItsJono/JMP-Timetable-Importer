# myUNSW to Google Calendar Timetable Importer
# More or less written by Chris Lam

try:
    from xml.etree import ElementTree  # for Python 2.5 users
except ImportError:
    from elementtree import ElementTree

from apiclient.discovery import build
from oauth2client.file import Storage
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.tools import run

import httplib2
from BeautifulSoup import BeautifulSoup
import re
import urllib2
import cookielib
import re
import urllib

import datetime

unsw_start_dates = {
    '11s1': '28/2/2011',
    '11s2': '18/7/2011',
    '12s1': '27/2/2012',
    '12s2': '16/7/2012',
    '13s1': '4/3/2013',
    '13s2': '29/7/2013',
    '14s1': '3/3/2014',
    '14s2': '28/7/2014',
    '15s1': '2/3/2015',
    '15s2': '27/7/2015',
    '16s1': '29/2/2016',
    '16s2': '25/7/2016'
}

days = {"Mon": 0, "Tue": 1, "Wed": 2, "Thu": 3, "Fri": 4}

login_url = 'https://ssologin.unsw.edu.au/cas/login?service=https%3A%2F%2Fmy.unsw.edu.au%2Famserver%2FUI%2FLogin%3Fmodule%3DISISWSSO%26IDToken1%3D'

timetable_url = 'https://my.unsw.edu.au/active/studentTimetable/timetable.xml'


def getFlow(full_path):
    return OAuth2WebServerFlow(client_id='743560754649-tvjckmfhgpfaa6g7k2bmt0dkugh41nlp.apps.googleusercontent.com',
                               client_secret='oXyBWz44n79FBnc9ulkwwEi5',
                               scope='https://www.googleapis.com/auth/calendar',
                               redirect_uri=full_path)


def getGoogleRedirect(full_path):
    return getFlow(full_path).step1_get_authorize_url()


def getTimetable(zUser, zPass, semester):
    jar = cookielib.CookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(jar))
    # CSRF Token or something. We need to steal it from SSO
    # into our cookie jar to go open the timetable page
    stupid_thing = re.findall(r'_cNoOpConversation.*?"', opener.open(login_url).read())[0].replace('"', '')
    data = {'username': zUser, 'password': zPass, '_eventId': 'submit', 'lt': stupid_thing}
    opener.open(login_url, urllib.urlencode(data))
    data = {}
    if semester:
        source = opener.open(timetable_url).read().replace('\n', '')
        if "sectionHeading" not in source:
            return ''
        s = BeautifulSoup(source)
        bsds = s.find('input', {'name': 'bsdsSequence'})['value']
        data = {'term': semester, 'bsdsSubmit-commit': 'Get Timetable', 'bsdsSequence': bsds}
    return opener.open(timetable_url, urllib.urlencode(data)).read()


def CreateClassEvent(title, content, where, start_time, end_time):
    event = {
        'summary': title,
        'description': content,
        'location': where,
        'start': {
            'dateTime': start_time,
            'timeZone': 'Australia/Sydney',
        },
        'end': {
            'dateTime': end_time,
            'timeZone': 'Australia/Sydney',
        }
    }
    return event


def getSemester(zu, zp):
    source = getTimetable(zu, zp, None)
    if "sectionHeading" not in source:
        return (
        "Bad timetable source, possibly incorrect login details or myunsw daily dose of downtime (12am-2am or whatever)",
        {})

    # parsing shit
    s = BeautifulSoup(source.replace("\n", ""))
    select_html = s.find("select", {'name': 'term'})
    select_html['style'] = 'width: 400px;'
    return (None,
            {
                'semester_select_html': select_html.prettify(),
                'source': source
            })


def export(source, code, full_path):
    f = source.replace('\r', '')

    if "sectionHeading" not in f:
        return "Bad timetable source, possibly incorrect login details or myunsw daily dose of downtime (12am-2am or whatever)"

    # parsing shit
    s = BeautifulSoup(f.replace("\n", ""))
    sem = re.sub(r'.*Semester (\d+) \S\S(\d+).*', u'\\2s\\1', s.find("option", {'selected': 'true'}).text)
    title = sem + " Timetable"

    if not re.match(r'\d\ds\d', sem):
        current_time = datetime.datetime.now()
        sem = '%ds%d' % (current_time.year % 100, 1 if current_time.month < 7 else 2)

    credentials = getFlow(full_path).step2_exchange(code)
    http = httplib2.Http()
    http = credentials.authorize(http)

    service = build('calendar', 'v3', http=http)

    ####################################################
    #  LOOK EVERYONE, I'M THROWING YOUR PASSWORDS AWAY #
    ####################################################
    zp = ''



    # make gcal calendar
    calendar = {
        'summary': title,
        'timeZone': 'Australia/Sydney',
    }

    created_calendar = service.calendars().insert(body=calendar).execute()
    print created_calendar['id']

    # Summer courses have N1 and N2 right after each other
    if s.find(text="N1").findNext("table").findNext("td").text == "N2":
        week_after_midsem_break = int(s.find(text="N2").findNext("table").findNext("td").text)
    else:
        week_after_midsem_break = int(s.find(text="N1").findNext("table").findNext("td").text)

    courses = [x.contents[0] for x in s.findAll("td", {"class": "sectionHeading"})]

    print "Parsing calendar to make events"

    for course in courses:
        # FINGERS CROSSED THAT THE TIMETABLE PAGE NEVER CHANGES
        classes = s.find(text=course).findNext("table").findAll("tr", {"class": re.compile("data")})
        ctype, code, day, tim, weeks, place, t = ['' for x in xrange(7)]
        for c in classes:
            a = [(x.contents[0] if x.contents else "") for x in c.findAll("td", recursive=False)]
            g = (t for t in a)

            t = g.next()

            if t.strip() != "&nbsp;":
                ctype = t

            t = g.next()
            if t.strip() not in days:
                code = t
                day = g.next().strip()
            else:
                day = t.strip()
            tim = g.next()
            weeks = g.next()
            place = g.next()
            t = ' '.join(g.next().findAll(text=True))

            if tim.find(" - ") == -1:
                continue
            start, end = tim.split(" - ")
            start = datetime.datetime.strptime(unsw_start_dates[sem] + ' ' + start, "%d/%m/%Y %I:%M%p")
            end = datetime.datetime.strptime(unsw_start_dates[sem] + ' ' + end, "%d/%m/%Y %I:%M%p")

            course = course.split()[0]

            w = []
            for r in weeks.split(","):
                if "N" in r:
                    print "Did not process %s %s %s because of non-integer week"
                    continue
                if "-" in r:
                    w += range(int(r.split("-")[0]), int(r.split("-")[1]) + 1)
                else:
                    w += [int(r)]

            weeks = w

            for w in weeks:
                if w < week_after_midsem_break:
                    w -= 1
                thisStart = start + datetime.timedelta(7 * w + days[day])
                thisEnd = end + datetime.timedelta(7 * w + days[day])

                thisEvent = CreateClassEvent('%s %s' % (course, ctype),
                                             "Instructor: %s Code:%s" % (t.strip(), code),
                                             place,
                                             thisStart.strftime('%Y-%m-%dT%H:%M:%S.000'),
                                             thisEnd.strftime('%Y-%m-%dT%H:%M:%S.000'))
                service.events().insert(calendarId=created_calendar['id'], body=thisEvent).execute()

    print "Probably success!"


def exportByScraping(zu, zp, semester, code, full_path):
    source = getTimetable(zu, zp, semester)
    return export(source, code, full_path)
