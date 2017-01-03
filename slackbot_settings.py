import os

API_TOKEN = os.environ["SLACK_BOT_TOKEN"]

DEFAULT_REPLY = "Write `help` to get help :baby_chick:"

PROJECT_ID = 280

IDEAS_URL = "https://demo.viima.com/api/customers/{}/items/".format(PROJECT_ID)

ACTIVITY_URL = "https://demo.viima.com/api/customers/{}/activities/".format(PROJECT_ID)

WEBSITE_URL = "https://demo.viima.com/demo/tutorial-board/"

PEOPLE_URL = "https://demo.viima.com/api/customers/{}/public_user_profiles/".format(PROJECT_ID)

MAX_COMMENT_LENGTH = 200

NOTIFY_INTERVAL = 10  # seconds

NOTIFICATION_CHANNEL = "#viima_notifications"
