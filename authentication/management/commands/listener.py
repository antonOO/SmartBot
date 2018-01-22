from django.core.management.base import BaseCommand
from authentication.models import Team
from slackclient import SlackClient
import time
import requests
import re
from django.conf import settings
from rasa_nlu.config import RasaNLUConfig
from rasa_nlu.components import ComponentBuilder
from rasa_nlu.model import Metadata, Interpreter


class Command(BaseCommand):
    help = 'Starts the bot for the first'

    def analyse_message(self, message):
        model_directory = settings.TRAINING_MODEL_QUESTION_ORIENTED
        interpreter = Interpreter.load(model_directory, RasaNLUConfig(settings.TRAINING_CONFIGURATION_FILE))
        interpreted_message = interpreter.parse(message)
        return interpreted_message


    def parse_for_slack(self, message):
        block = re.compile('(<pre><code>|</code></pre>)')
        message = block.sub("```", message)
        snip = re.compile('(<code>|</code>)')
        message = snip.sub("`", message)
        parse = re.compile('</*h[0-9]>|</*[a-z]*>')
        message = parse.sub("", message)
        return message


    def handle(self, *args, **options):
        print(Team.objects)
        team = Team.objects.first()
        client = SlackClient(team.bot_access_token)
        if client.rtm_connect():
            while True:
                events = client.rtm_read()
                print("%s----%s" % (team, events))
                for event in events:
                    if 'type' in event and event['type'] == 'message' and event['user'] != 'U8CLSEWAC':
                        '''url = 'http://localhost:8001/answer/'
                        params =  {
                            'question': event['text']
                        }

                        response = requests.get(url, params)
                        answer = self.parse_for_slack(response.text)
                        '''
                        answer = self.analyse_message(event["text"])
                        print("answer " + str(answer))
                        if "programming" in answer["intent"]["name"] and float(answer["intent"]["confidence"]) > 0.90:
                            client.rtm_send_message(event['channel'], "opi")
                time.sleep(0.1)
