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
from nltk.corpus import stopwords
from collections import defaultdict

class Command(BaseCommand):

    def __init__(self):
        self.auto_detection_enabled = True
        self.divergent_flag = False
        self.messages_info = []
        self.number_of_answers = 1
        self.direct_search_flag = False

    def analyse_message(self, message):
        model_directory = settings.TRAINING_MODEL_QUESTION_ORIENTED
        interpreter = Interpreter.load(model_directory, RasaNLUConfig(settings.TRAINING_CONFIGURATION_FILE))
        interpreted_message = interpreter.parse(message)
        return interpreted_message

    def parse_message(self, message):
        block = re.compile('(<pre><code>|</code></pre>)')
        message = block.sub("```", message)
        snip = re.compile('(<code>|</code>)')
        message = snip.sub("`", message)
        parse = re.compile('</*h[0-9]>|</*[a-z]*>')
        return parse.sub("", message)

    def create_attachment(self, message, query, intent, link, bm25_score, qscore, view_count, ascore, is_accepted):
        params = {
                      'answer' : message,
                      'query' : query,
                      'intent' : intent,
                      'bm25_score' : bm25_score,
                      'qscore' : qscore,
                      'view_count' : view_count,
                      'ascore' : ascore,
                      'is_accepted' : is_accepted
                  }
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
        return review_attachment

    def parse_for_slack(self, messages, query, intent):
        try:
            parsed_output = []
            for message, link, bm25_score, qscore, view_count, ascore, is_accepted in messages:
                message = self.parse_message(message)
                review_attachment = self.create_attachment(message, query, intent, link, bm25_score, qscore, view_count, ascore, is_accepted)
                parsed_output.append((message,review_attachment))
            return parsed_output
        except:
            parsed_output = []
            for message in messages:
                parsed_output.append((message, ""))
            return parsed_output



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

    def is_for_handling(self, event):
        return ('type' in event
        and event['type'] == 'message'
        and 'user' in event
        and event['user'] != settings.BOT_UID)

    def help_command(self, client, event):
        client.rtm_send_message(event['channel'], settings.INFORMATIVE_MESSAGE)

    def toggle_command(self, client, event):
        self.auto_detection_enabled = not self.auto_detection_enabled
        client.rtm_send_message(event['channel'], ("Auto detection is enabled: %s" % str(self.auto_detection_enabled)))

    def divergency_command(self, client, event):
        self.divergent_flag = not self.divergent_flag
        client.rtm_send_message(event['channel'], ("Divergent answers: %s" % str(self.divergent_flag)))

    def num_answer_command(self, client, event):
        if (len(event['text'].split()) == 3
         and event['text'].split()[2].isdigit()
         and int(event['text'].split()[2]) > 0):
            self.number_of_answers = int(event['text'].split()[2])
            client.rtm_send_message(event['channel'], "Number of answers returned are %d" % self.number_of_answers)
        else:
            client.rtm_send_message(event['channel'], "Invalid use of answers command!")

    def direct_search_command(self, client, event):
        self.direct_search_flag = not self.direct_search_flag
        client.rtm_send_message(event['channel'], ("Direct search: %s" % str(self.direct_search_flag)))

    def direct_message_command(self, client, event):
        message = event["text"].replace("<@" + settings.BOT_UID + ">", "")
        message_info = self.analyse_message(message)
        parsed_output = self.post_message_to_middleware(message_info)
        for (answer, review) in parsed_output:
            client.api_call("chat.postMessage",text=answer, channel=event["channel"], attachments=review, as_user=True)

    def autodetection_triggered_command(self, client, event):
        if self.auto_detection_enabled and self.is_programming_question(event):
            message_info =  self.messages_info.pop(0)
            parsed_output = self.post_message_to_middleware(message_info)
            for (answer, review) in parsed_output:
                client.api_call("chat.postMessage",text=answer, channel=event["channel"], attachments=review, as_user=True)

    def handle_commands(self, client, event):
        sobot_commands = defaultdict(lambda : self.direct_message_command,
                                     {
                                        "help" : self.help_command,
                                        "toggle" : self.toggle_command,
                                        "divergency" : self.divergency_command,
                                        "answers" : self.num_answer_command,
                                        "directsearch" : self.direct_search_command
                                     })

        command_dict = defaultdict(lambda : self.autodetection_triggered_command, {
                            "<@" + settings.BOT_UID + ">" : sobot_commands
        })

        for word in event['text'].split():
            if callable(command_dict[word]):
                command_dict[word](client, event)
                break;
            else:
                command_dict = command_dict[word]

    def remove_stopwords_non_direct(self, message):
        if not self.direct_search_flag:
            cached_stop_words = stopwords.words("english")
            return " ".join(word for word in message["text"].split() if word not in cached_stop_words)
        return message['text']

    def post_message_to_middleware(self, message):
        question = self.remove_stopwords_non_direct(message)
        message_json = {
                            'question' : question,
                            'entities' : str([(e['value'], e['entity']) for e in message['entities']]),
                            'intent'   : message['intent']['name'],
                            'confidence' : message['intent']['confidence'],
                            'num_answers' : self.number_of_answers,
                            'divergent_flag' : self.divergent_flag,
                            'direct_search_flag' : self.direct_search_flag
                        }

        response = requests.get(settings.MIDDLEWARE_URL_ANSWER, message_json)
        json_answer_info = json.loads(response.text)

        query_string = json_answer_info['query']
        array_of_answers = eval(json_answer_info['passages'])
        intent = json_answer_info['intent']

        return self.parse_for_slack(array_of_answers, query_string, intent)

    def handle(self, *args, **options):
        print(Team.objects)
        team = Team.objects.first()
        client = SlackClient(team.bot_access_token)
        if client.rtm_connect():
            while True:
                events = client.rtm_read()
                print("%s----%s" % (team, events))
                for event in events:
                    if self.is_for_handling(event):
                        self.handle_commands(client, event)

                time.sleep(0.1)
