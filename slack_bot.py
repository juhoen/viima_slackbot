# coding: utf-8
#
# Copyright © 2016 Juho Enala

import os
from slackclient import SlackClient
from slackbot.bot import respond_to
from slackbot.bot import listen_to
from slackbot.bot import Bot
import re
from slackbot_settings import *
from viima_data import *
import time
from _thread import *
from pytz import timezone
import datetime


def notification_engine():
    sc = SlackClient(API_TOKEN)
    sc.rtm_connect()
    print("Notification engine started successfully!")

    last_activities = []
    # Notification loop. At the moment server doesn't notify client, so program
    # needs to manually check changes every NOTIFY_INTERVAL seconds.
    while True:
        data = get_data_from_server(ACTIVITY_URL)['results']  # Get user specific data from server
        current_activities = []
        for item in data:
            current_activities.append(item['id'])

        # Normally last_activities contains last loops list of activities.
        # At first round it's empty, so lets declare it to current_activities
        if not last_activities:
            last_activities = current_activities

        last_set = set(last_activities)
        activities_to_notify = []

        # Lets check if current_activities contains activities that last_activities
        # does not contain -> That a new activity -> Notify that!
        for item in current_activities:
            if item not in last_set:
                activities_to_notify.append(item)
        last_activities = current_activities

        # Activities_to_notify contains all the activities that needs to be notified.
        if len(activities_to_notify) > 0:
            msg = ""
            for index in activities_to_notify:  # Loop through activities_to_notify and notify them
                for item in data:
                    if item['id'] == index:
                        if item['model'] == "comment":
                            # Comments:
                            if not item['is_attachment']:
                                msg = ("_*{user}* commented \"{name}\":_\n```{content}```\n"
                                       .format(user=item['fullname'],
                                               name=item['name'],
                                               content=item['content']))
                            # Attachments:
                            else:
                                msg = ("_*{user}* added attachment to \"{name}\"_\n"
                                       .format(user=item['fullname'],
                                               name=item['name']))

                        # Items (new ideas):
                        elif item['model'] == "item":
                            msg = ("_*{user}* added \"{name}\":_"
                                   .format(user=item['fullname'],
                                           name=item['name']))

                            idea_data = get_data_from_server(IDEAS_URL)
                            new_idea = None
                            for idea in idea_data:
                                if idea['id'] == item['id']:
                                    new_idea = idea
                                    break

                            msg += "\n```{}```\n".format(new_idea['description'])

                        # Lets send notifications to default notification channel.
                        sc.rtm_send_message(NOTIFICATION_CHANNEL, msg)

        # Loop sleeps NOTIFY_INTERVAL seconds and starts over again.
        time.sleep(NOTIFY_INTERVAL)


def str_to_integer(string, default):
    """
    Returns string formatted to integer
    @param: string - String to format
    @param: default - Default integer wanted if string isn't possible to format.
    """
    try:
        return int(string)
    except ValueError:
        return default


@respond_to('^man (.*)', re.IGNORECASE)
def respond_manual(message, subject):
    # TODO: Put messages and subjects to the JSON file.
    subject = str.lower(subject)
    if subject == "recap":
        msg = "\nRecap gives you the newest updates since given day.\n" \
              ">_`recap` and *recap 1* recaps last day's activities._\n" \
              ">_`recap X` recaps activities for the last X days._"

    elif subject == "top":
        msg = "\nTop gives you the current most voted ideas.\n" \
              ">_`top` and `top 3` returns 3 most voted ideas._\n" \
              ">_`top X` returns X most voted ideas._"

    elif subject == "activity":
        msg = "\nActivity returns latest activity.\n" \
              ">_`activity` and `activity 1` returns last day's activity._\n" \
              ">_`activity X` returns activities for the last X days._\n" \
              ">_`activity X ITEM_NAME` returns ITEM_NAME's activities for the last X days._"

    elif subject == "show":
        msg = "\nShow returns comments of the selected idea.\n" \
              ">_`show [ideas name here]` returns idea and its comments._\n" \
              ">_E.g. `show the great idea`._\n"

    elif subject == "contributors":
        msg = "\nContributors returns most active contributors.\n" \
              ">_`contributors` returns top 5 contributors._\n" \
              ">_`contributors 2` returns top 2 contributors._\n"
    else:
        msg = "\n_{}_ not found from the manual. Type `help` to get existing commands.".format(subject)
    message.reply(msg)


@respond_to('^recap$', re.IGNORECASE)
@respond_to('^recap (.*)', re.IGNORECASE)
def respond_recap(message, days=1):
    # Format string to integer
    days = str_to_integer(days, 1)
    # Get the json data
    json_data = get_data_from_server(IDEAS_URL)

    # Get ideas from last 'days' days
    if len(json_data) > 0:
        new_ideas = get_last_ideas(json_data, days)
    else:
        new_ideas = []

    if len(new_ideas) != 0:

        message.reply("\n_Viima recap for last {day}_"
                      .format(day=str(days) + " days" if days > 1 else "day"))
        best_ideas = get_top_ideas_by_votes(new_ideas, 3)

        message.reply("*Here are the top {} most voted ideas:*"
                      .format(3 if len(best_ideas) > 2 else len(best_ideas)))
        msg = ""
        for item in best_ideas:
            msg = ("*Votes {votes}*: \"{name}\" created by {user}.\n{url}\n\n"
                   .format(votes=item['vote_count'],
                           name=item['name'],
                           user=item['fullname'],
                           url=WEBSITE_URL + "?activeItem=" + str(item['id'])))

        message.reply(msg)
        message.reply("A total of new {ideas} ideas for last {days}"
                      .format(ideas=len(best_ideas),
                              days=str(days) + " days" if days > 1 else "day"))

    else:
        message.reply("\nNo new activity since {days} days."
                      .format(days=days))


@respond_to('^top$', re.IGNORECASE)
@respond_to('^top (.*)', re.IGNORECASE)
def respond_top(message, top=3):
    # Format string to integer
    top = str_to_integer(top, 3)

    # Get json data from server
    ideas = get_data_from_server(IDEAS_URL)

    if len(ideas) > 0:
        message.reply("\nHere is current top {} ideas:"
                      .format(top))
        msg = "\n"

        ideas = get_top_ideas_by_votes(ideas, top)

        count = 0
        for item in ideas:
            count += 1
            msg += ("[{votes} votes] *{count}.* \"{name}\" created by {user}\n{url}\n\n"
                    .format(votes=item['vote_count'],
                            count=count,
                            name=item['name'],
                            user=item['fullname'],
                            url=WEBSITE_URL + "?activeItem=" + str(item['id'])))

        message.reply(msg)


@respond_to('^activity$', re.IGNORECASE)
@respond_to('^activity (.*)', re.IGNORECASE)
def respond_activity(message, days=1):
    # Format string to integer
    days = str_to_integer(days, 1)

    message.reply("\nHere is activity for last {}:"
                  .format(str(days) + " days" if days > 1 else "day"))

    # Get the json data from server
    activity_data = get_data_from_server(ACTIVITY_URL)['results']
    # Get the newest activity
    activity_data = get_last_ideas(activity_data, days)

    msg = "\n"

    for item in activity_data:
        if item['model'] == "comment":
            # Cut too long comments
            comment = item['content']
            if len(comment) > MAX_COMMENT_LENGTH:
                comment = comment[:MAX_COMMENT_LENGTH] + "..."
            msg += ("\n*{user}* commented \"{name}\"\n_{comment}_\n"
                    .format(user=item['fullname'],
                            name=item['name'],
                            comment=comment))
        elif item['model'] == "item":
            msg += ("\n*{user}* added new item \"{name}\"\n"
                    .format(user=item['fullname'],
                            name=item['name']))
    message.reply(msg)


@respond_to('^show$', re.IGNORECASE)
@respond_to('^show (.*)', re.IGNORECASE)
def respond_show(message, title=None):
    data = get_data_from_server(IDEAS_URL)
    idea = None
    idea_id = None
    msg = ""

    if title is not None:
        for item in data:
            # Find correct idea from the ideas
            if str.lower(item['name']) == str.lower(title):
                comments_url = get_comments_url(item)
                idea = item
                break

        if idea is not None:
            msg += ("```\n{name}\n\n{descr}\n\n```\n_Idea by {user}_\n"
                    .format(name=idea['name'],
                            descr=idea['description'],
                            user=idea['fullname']))

            if idea['comment_count'] == 0:
                msg += "_This item has no comments yet..._"
            else:
                data = get_data_from_server(comments_url)
                for i in range(len(data)):
                    item = data[len(data) - 1 - i]
                    msg += "--------------------------------------------"
                    msg += ("\n*{user}*:\n{content}\n{votes}\n"
                            .format(user=item['fullname'],
                                    content=item['content'],
                                    votes="_Votes: " + str(item['upvote_count']) + "_" if item['upvote_count'] > 0 else ""))
                msg += "--------------------------------------------"
        else:
            msg = "No item _{}_ found.".format(title)
    else:
        msg += "\nYou need to choose an idea. E.g. try:"
        for item in data[-3:]:
            msg += "\n>`show {}`".format(item['name'])

    message.reply(msg)


@respond_to('^contributors$', re.IGNORECASE)
@respond_to('^contributors (.*)', re.IGNORECASE)
def respond_contributors(message, top=5):
    top = str_to_integer(top, 5)

    data = get_data_from_server(PEOPLE_URL)['results']

    print(PEOPLE_URL)

    people = get_top_people_by_points(data, top)

    if len(people) > 0:
        msg = "\nTop {} most contributed people:\n".format(top)

        count = 0
        for item in people:
            count += 1
            msg += "--------------------------------------------"
            msg += ("\n*{count}.* - {user} - _{points} points_\n"
                    .format(count=count,
                            user=item['fullname'],
                            points=item['points']))
        msg += "--------------------------------------------"
    message.reply(msg)


@respond_to('help', re.IGNORECASE)
def respond_help(message):
    message.reply("\nI'm here to help.\n"
                  "You can operate me with these commands:\n"
                  ">_Type `recap` to get the newest Viima updates for one day_ :fire:\n"
                  ">_Type `show IDEA` to see the idea and comments_ :speech_balloon: \n"
                  ">_Type `top 5` to get 5 best ideas_ :chart_with_upwards_trend: \n"
                  ">_Type `activity` to get last day's activity_ :writing_hand::skin-tone-2: \n"
                  ">_Type `contributors` to get list of most active contributors_ :raising_hand::skin-tone-2:\n"
                  ">_Type `man recap` to get more info about recap_ :information_source:\n")

    message.react("hugging_face")


bot = Bot()
print("Starting notification engine..")
start_new_thread(notification_engine, ())
bot.run()
