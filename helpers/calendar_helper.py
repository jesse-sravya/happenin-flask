import os
import requests
import json
from urllib.parse import urljoin

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_CALENDAR_ID = os.getenv("GOOGLE_CALENDAR_ID")

GOOGLE_API_ENDPOINT = 'https://www.googleapis.com'


GET_EVENTS_API = '/calendar/v3/calendars/:calendar_id/events'
CREATE_EVENT_API = '/calendar/v3/calendars/:calendar_id/events'
GET_USER_PROFILE_API = '/oauth2/v3/tokeninfo'
ATTEND_EVENT_API = '/calendar/v3/calendars/:calendar_id/events/:event_id'
GET_EVENT_API = '/calendar/v3/calendars/:calendar_id/events/:event_id'


def process_request(url, method='GET', data=None, params=None, headers={}):
    headers['Content-Type'] = 'application/json'
    headers['key'] = GOOGLE_API_KEY


    url = url.replace(':calendar_id', GOOGLE_CALENDAR_ID)


    if method == 'POST':
        response = requests.post(urljoin(GOOGLE_API_ENDPOINT, url), headers=headers, data=data)
    else:
        response = requests.get(urljoin(GOOGLE_API_ENDPOINT, url), headers=headers, params=params)

    if response.status_code != 200:
        print("Request to '%s' resulted in:\n%s - %s" % (response.url, response.status_code,
                                                                 response.text))

    return response



def get_public_events():
    response = process_request(GET_EVENTS_API, method='GET', data=None, params={ 'key': GOOGLE_API_KEY })
    if response.status_code != 200:
        return False, "Couldn't fetch events."
        
    return True, format_events(response.json().get('items', []), "public")


def get_private_events(auth_header):
    response = process_request(GET_EVENTS_API, method='GET', data=None, params={ 'key': GOOGLE_API_KEY }, headers={ 'Authorization': auth_header })

    if response.status_code != 200:
        return False, "Couldn't fetch events."
        
    return True, format_events(response.json().get('items', []), "private")


def format_events(events, event_visibility):
    output = []

    for event in events:
        if (event.get("visibility") == event_visibility) and event.get("summary"):
            output.append({
                "id": event.get("id"),
                "event_name": event.get("summary"),
                "start_date": event.get("start", {}).get("dateTime"),
                "location": event.get("conferenceData", {}).get("conferenceSolution", {}).get("name") or event.get("location") or "(not set)",
                "creator": event.get("creator", {}).get("email", "").split("@")[0],
            })
    
    return output


def create_event(event, auth_header):
    event_visibility = 'public' if event.get("visibility") else 'private'

    event_body = {
        "end": {
            "dateTime": event.get("end_date"),
            "timeZone": "UTC"
        },
        "start": {
            "dateTime": event.get("start_date"),
            "timeZone": "UTC"
        },
        "location": event.get("location"),
        "summary": event.get("event_name", "New event"),
        "visibility": event_visibility
    }
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': auth_header,
        'key': GOOGLE_API_KEY
    }

    response = process_request(CREATE_EVENT_API, method='POST', data=json.dumps(event_body), params=None, headers={ 'Authorization': auth_header })


    if response.status_code != 200:
        return False, "Couldn't fetch events."
        
    return True, format_events(response.json().get('items', []), event_visibility)


def get_event(auth_header, event_id):
    response = process_request(GET_EVENT_API.replace(':event_id', event_id), method='GET', data=None, params=None, headers={ 'Authorization': auth_header })
    if response.status_code != 200:
        return False, "Couldn't fetch user details."

    return True, response.json()


def attend_event(auth_header, event_id):
    headers = {
        'Authorization': auth_header,
    }

    access_token = auth_header.split(" ")[1]
    response = process_request(GET_USER_PROFILE_API, method='GET', data=None, params={'access_token': access_token}, headers=headers)

    if response.status_code != 200:
        return False, "Couldn't fetch user details."
    
    user_profile = response.json()
    user_email = user_profile.get("email")

    success, event = get_event(auth_header, event_id)
    if not success:
        return False, "Couldn't fetch event details."

    event_attendees = event.get('attendees', [])
    event_attendees.append({ 'email': user_email })

    response = process_request(ATTEND_EVENT_API.replace(':event_id', event_id), method='PUT', data=None, params=None, headers=headers)

    if response.status_code != 200:
        return False, "Couldn't add to event."

    return True, "Added successfully"


    
