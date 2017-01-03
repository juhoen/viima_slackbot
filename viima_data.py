from urllib.request import urlopen
import json
import datetime
from slackbot_settings import *


def get_votes(json_file):
    """
    Returns json_files votes
    @param: json_file - given json file
    """
    try:
        return int(json_file['vote_count'])
    except KeyError:
        return 0


def get_points(json_file):
    """
    Returns json_files points
    @param: json_file - given json file
    """
    try:
        return int(json_file['points'])
    except KeyError:
        return 0


def get_top_ideas_by_votes(ideas, top=None):
    """
    Returns most voted ideas from given JSON string.
    @param: ideas - List of ideas in JSON format
    @param: top - How many top ideas are wanted. If top is None, function returns all ideas sorted.
    """
    if top is None:
        top = len(ideas)
        ideas.sort(key=get_votes, reverse=True)
    if len(ideas) > top:
        ideas = ideas[:top]
    return ideas


def get_top_people_by_points(people, top=None):
    """
    Returns people with most points.
    @param: People - List of people in JSON format
    @param: top - How many top people are wanted. If top is None, function returns all people sorted.
    """
    if top is None:
        top = len(people)
    people.sort(key=get_points, reverse=True)
    if len(people) > top:
        people = people[:top]
    return people


def get_data_from_server(url):
    """
    Function gets and returns data from selected site.
    @param: url - Selected sites address in string format.
    """
    # TODO: Handle exceptions e.g. no connection to server
    data = urlopen(url).read()
    json_data = json.loads(data.decode('utf-8'))
    return json_data


def format_string_to_date(string):
    """
    Returns string formatted to datetime object.
    @param: string - Date in string format.
    """
    # NOTE: Demo version this program cuts time zone off and uses GMT.
    return datetime.datetime.strptime(string[:-6], "%Y-%m-%dT%H:%M:%S.%f")


def get_last_ideas(json_data, d=1):
    """
    Returns last ideas.
    @param: json_data - List of ideas in JSON format.
    @param: d - History length in days.
    """
    selected_items = []
    for item in json_data:
        date = format_string_to_date(item['created'])
        if date > datetime.datetime.now() - datetime.timedelta(days=d):
            selected_items.append(item)
    return selected_items


def get_comments_url(idea):
    """
    Returns url to specific ideas comments.
    @param: idea - Selected idea
    """
    idea_id = idea['id']
    return IDEAS_URL + str(idea_id) + "/comments/"
