from django.core.management.base import BaseCommand
from authentication.models import Team
from slackclient import SlackClient
import time
import requests


class Command(BaseCommand):
    help = 'Starts the bot for the first'

    def handle(self, *args, **options):
        print(Team.objects)
        team = Team.objects.first()
        client = SlackClient(team.bot_access_token)
        if client.rtm_connect():
            while True:
                events = client.rtm_read()
                print("%s----%s" % (team, events))
                for event in events:
                    if 'type' in event and event['type'] == 'message':
                    #if 'type' in event and event['type'] == 'message' and event['text'] == 'hi':
                        #Send to Django server - http://localhost:8000/answer/?question=
                        #
                        url = 'http://localhost:8001/answer/'
                        params =  {
                            'question': event['text']
                        }
                        response = requests.get(url, params)
                        print(response.text)
                        client.rtm_send_message(event['channel'], response.text)
                time.sleep(1)
