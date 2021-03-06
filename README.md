## What is SmartBot (Sobot)?

SmartBot (or Sobot) is a computer science oriented QA bot, which is attachable to Slack. 
It identifies only computer science related questions, within a channel,
and tries to find their answers on SO. 

SmartBot is written in Python3 - all of the dependencies are listed in the requirements.txt.
In order to run SmartBot You need to have Python3. 

## To install Sobot:

1. Clone the repository to a directory of your choice.
2. Install dependencies in `requirements.txt` (if install failed exec. `sudo apt-get install python3-dev` and try again)
3. Create a [Slack App] (https://api.slack.com/slack-apps) / an account is required.
4. When the app is created, click it, and select OAuth & Permissions, from the Features tab.
5. Add a new Redirect url, which is the following - `http://127.0.0.1:8000/slack/oauth/` 
6. Save Your Slack App's client_id and client_secret.
7. Open the SmartBot repo folder and navigate to "django_bot/". There you will find a setting.py file.
8. Change the `SLACK_CLIENT_ID` and `SLACK_CLIENT_SECRET` variables to the ones obtained from Your Slack App.
9. Navigate back to the repo folder and from a terminal execute `python manage.py runserver`
10. Go to `0.0.0.0:8000` and complete the authentication process. 

If you receive a success message, then Sobot is successfully added to Your workspace.
To run sobot execute `python manage.py listener` from a terminal window in the project directory.

11. After you run the Slack listener and start the bot, see in the terminal window Your bot UID and
set the `BOT_UID` in the settings.py file.


## Disclaimer - installed and tested only on Linux/ May have Rasa_NLU installation problems on Windows
