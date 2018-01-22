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

    def __init__(self):
        self.auto_detection_enabled = True

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

    def is_programming_question(self, event):
        if ('type' in event
        and event['type'] == 'message'
        and event['user'] != settings.BOT_UID):
            message_info = self.analyse_message(event['text'])
            print("answer " + str(message_info))
            return ("programming" in message_info['intent']['name'] and float(message_info['intent']['confidence']) > 0.90)
        return False

    def is_direct_message(self, event):
        return ('type' in event
        and event['type'] == 'message'
        and event['user'] != settings.BOT_UID
        and ("<@" + settings.BOT_UID + ">") in event['text'])

    def toggle_detection_check(self, event):
        return (self.is_direct_message(event) and ("<@" + settings.BOT_UID + "> toggle" == event['text']))


    def handle(self, *args, **options):
        print(Team.objects)
        team = Team.objects.first()
        client = SlackClient(team.bot_access_token)
        if client.rtm_connect():
            while True:
                events = client.rtm_read()
                print("%s----%s" % (team, events))
                for event in events:
                    if self.toggle_detection_check(event):
                        self.auto_detection_enabled = not self.auto_detection_enabled
                        client.rtm_send_message(event['channel'], ("Auto detection is enabled: %s" % str(self.auto_detection_enabled)))
                    elif self.is_direct_message(event):
                        client.rtm_send_message(event['channel'], "immediately")
                    elif self.auto_detection_enabled and self.is_programming_question(event):
                        client.rtm_send_message(event['channel'], "opi")
                        #response = requests.get(settings, message_info)
                        #answer = self.parse_for_slack(response.text)
                time.sleep(0.1)
