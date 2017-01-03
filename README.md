**What is Viima Slack bot?**
---

Viima Slack bot is a Viima implementation for Slack. It allows user to interract with Viima straigth from the Slack chat. This bot is only for demo purposes and it is not official.

---
**Installing (on Ubuntu):**

Navigate to viimabot -folder and create virtual environment for Python:
```
virtualenv env
```
----

Activate the virtual environment:
```
source env/bin/activate
```
---

Install requirements:
```
pip install requirements.txt
```
In case of getting error "No matching distribution found for requirements", try:
```
pip install --upgrade -r requirements.txt
```
---

Set your private API token as environmental variable:
```
export SLACK_BOT_TOKEN='[TOKEN HERE]'
```
---

Run the Slack bot:
```
python3 slack_bot.py
```
