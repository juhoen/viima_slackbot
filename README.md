**What is Viima Slack bot?**
---

Viima Slack bot is a Viima implementation for Slack. It allows user to interract with Viima straigth from the Slack chat. This bot is only for demo purposes and it is not official.

---
**Installing (on Ubuntu):**

Navigate to same folder with slack_bot.py file and create virtual environment for Python:
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
pip install -r requirements.txt
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
