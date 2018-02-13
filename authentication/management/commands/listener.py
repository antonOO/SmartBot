from django.core.management.base import BaseCommand
from authentication.models import Team
from slackclient import SlackClient
import time
import requests
import re
import json
import urllib
from django.conf import settings
from rasa_nlu.config import RasaNLUConfig
from rasa_nlu.components import ComponentBuilder
from rasa_nlu.model import Metadata, Interpreter


class Command(BaseCommand):

    def __init__(self):
        self.auto_detection_enabled = True
        self.divergent_flag = False
        self.messages_info = []
        self.number_of_answers = 1

    def analyse_message(self, message):
        model_directory = settings.TRAINING_MODEL_QUESTION_ORIENTED
        interpreter = Interpreter.load(model_directory, RasaNLUConfig(settings.TRAINING_CONFIGURATION_FILE))
        interpreted_message = interpreter.parse(message)
        return interpreted_message

    def parse_for_slack(self, messages, query):
        parsed_output = []
        print(messages)
        for message, link in messages:

            if message == "Cannot find an answer":
                return [("Cannot find an answer", "")]

            block = re.compile('(<pre><code>|</code></pre>)')
            message = block.sub("```", message)
            snip = re.compile('(<code>|</code>)')
            message = snip.sub("`", message)
            parse = re.compile('</*h[0-9]>|</*[a-z]*>')
            message = parse.sub("", message)

            params = {'answer' : message, 'query' : query}
            url_update_negative = settings.MIDDLEWARE_URL_UPDATE_TRAINING_DATA_NEGATIVE + urllib.parse.urlencode(params)
            url_update_positive = settings.MIDDLEWARE_URL_UPDATE_TRAINING_DATA_POSITIVE + urllib.parse.urlencode(params)
            review_attachment = json.dumps([{
                  "fallback": "Make Sobot better!",
                  "actions": [
                    {
                      "type": "button",
                      "text": "I like the answer!",
                      "url": url_update_positive,
                      "style": "primary"
                    },
                    {
                      "type": "button",
                      "text": "Sobot this is garbage!",
                      "url": url_update_negative,
                      "style": "danger"
                    },
                    {
                      "type": "button",
                      "text": "Show me more.",
                      "url": link
                    }
                  ]
                }
              ])


            parsed_output.append((message,review_attachment))
        return  parsed_output

    def is_programming_question(self, event):
        if ('type' in event
        and event['type'] == 'message'
        and 'text' in event
        and len(event['text'].split()) >= settings.MINIMAL_NUMBER_OF_WORDS
        and 'user' in event
        and event['user'] != settings.BOT_UID):
            message_info = self.analyse_message(event['text'])
            print(message_info)
            if ("programming" in message_info['intent']['name'] and float(message_info['intent']['confidence']) > 0.90):
                self.messages_info.append(message_info)
                return True
        return False

    def is_direct_message(self, event):
        return ('type' in event
        and event['type'] == 'message'
        and 'user' in event
        and event['user'] != settings.BOT_UID
        and ("<@" + settings.BOT_UID + ">") == event['text'].split()[0])

    def toggle_detection_check(self, event):
        return (self.is_direct_message(event) and ("<@" + settings.BOT_UID + "> toggle" == event['text']))

    def change_nasnwers_check(self, event):
        return (self.is_direct_message(event)
        and 'text' in event
        and len(event['text'].split()) == 3
        and "answers" == event['text'].split()[1]
        and event['text'].split()[2].isdigit()
        and int(event['text'].split()[2]) > 0)

    def change_divergency_check(self, event):
        return (self.is_direct_message(event)
        and 'text' in event
        and len(event['text'].split()) == 2
        and "divergency" == event['text'].split()[1])

    def help_check(self, event):
        return (self.is_direct_message(event)
        and 'text' in event
        and len(event['text'].split()) == 2
        and "help" == event['text'].split()[1])

    def post_message_to_middleware(self, message):
        message_json = {
                            'question' : message['text'],
                            'entities' : str([(e['value'], e['entity']) for e in message['entities']]),
                            'intent'   : message['intent']['name'],
                            'confidence' : message['intent']['confidence'],
                            'num_answers' : self.number_of_answers,
                            'divergent_flag' : self.divergent_flag
                        }

        response = requests.get(settings.MIDDLEWARE_URL_ANSWER, message_json)
        json_answer_info = json.loads(response.text)

        query_string = json_answer_info['query']
        array_of_answers = eval(json_answer_info['passages'])
        return self.parse_for_slack(array_of_answers, query_string)

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
                    elif self.help_check(event):
                        client.rtm_send_message(event['channel'], settings.INFORMATIVE_MESSAGE)
                    elif self.change_nasnwers_check(event):
                        self.number_of_answers = int(event['text'].split()[2])
                        client.rtm_send_message(event['channel'], "Number of answers returned are %d" % self.number_of_answers)
                    elif self.change_divergency_check(event):
                        self.divergent_flag = not self.divergent_flag
                        client.rtm_send_message(event['channel'], ("Divergent answers: %s" % str(self.divergent_flag)))
                    elif self.is_direct_message(event):
                        message = event["text"].replace("<@" + settings.BOT_UID + ">", "")
                        message_info = self.analyse_message(message)
                        parsed_output = self.post_message_to_middleware(message_info)
                        for (answer, review) in parsed_output:
                            client.api_call("chat.postMessage",text=answer, channel=event["channel"], attachments=review, as_user=True)
                    elif self.auto_detection_enabled and self.is_programming_question(event):
                        message_info =  self.messages_info.pop(0)
                        parsed_output = self.post_message_to_middleware(message_info)
                        for (answer, review) in parsed_output:
                            client.api_call("chat.postMessage",text=answer, channel=event["channel"], attachments=review, as_user=True)

                time.sleep(0.1)
