from django.test import TestCase
from .management.commands.listener import Command
from django.conf import settings

class SlackListenerTests(TestCase):

    def setUp(self):
        self.command_obj = Command()
        self.sobotref = "<@" + settings.BOT_UID + ">"

    def test_analyze_message(self):
        rasa_dict = self.command_obj.analyse_message("How do you write a java for-loop?")
        try:
            intent = rasa_dict['intent']['name']
            self.assertEqual("programming_procedure", intent)
        except:
            self.fail("Wrong modeling!")

    def test_parse_message(self):
        parsed = self.command_obj.parse_message("<code><h1>parsed<h1><code>")
        parsed2 = self.command_obj.parse_message("<pre><code>parsed2<pre><code>")
        self.assertEqual(parsed, "`parsed`")
        self.assertEqual(parsed2, "```parsed2```")

    def test_is_programming_question(self):
        event = {
                    'type' : "message",
                    'user' : "me",
                    'text' : "How to create a java for-loop?"
                }
        result = self.command_obj.is_programming_question(event)
        self.assertEqual(result, True)
        self.assertEqual(len(self.command_obj.messages_info), 1)

        event['text'] = "Please, stop bothering the model."
        result = self.command_obj.is_programming_question(event)
        self.assertEqual(result, False)


    def test_remove_stopwords(self):
        message = "what is happening?"
        parsed = self.command_obj.remove_stopwords_non_direct(message)
        self.assertEqual(parsed.strip(), "happening?")

        self.command_obj.direct_search_flag = True
        parsed = self.command_obj.remove_stopwords_non_direct(message)
        self.assertEqual(parsed.strip(), "what is happening?")

    def test_handle_commands_toggle(self):
        try:
            self.command_obj.handle_commands(None, {"text" : self.sobotref + " toggle"})
        except:
            self.assertEqual(self.command_obj.auto_detection_enabled, False)

    def test_handle_commands_divergency(self):
        try:
            self.command_obj.handle_commands(None, {"text" : self.sobotref + " divergency"})
        except:
            self.assertEqual(self.command_obj.divergent_flag, True)

    def test_handle_commands_directsearch(self):
        try:
            self.command_obj.handle_commands(None, {"text" : self.sobotref + " directsearch"})
        except:
            self.assertEqual(self.command_obj.direct_search_flag, True)

    def test_handle_commands_number_of_answers(self):
        try:
            self.command_obj.handle_commands(None, {"text" : self.sobotref + " answers 3q"})
        except:
            self.assertEqual(self.command_obj.number_of_answers, 1)

        try:
            self.command_obj.handle_commands(None, {"text" : self.sobotref + " answers 3"})
        except:
            self.assertEqual(self.command_obj.number_of_answers, 3)

    def test_create_attachment(self):
        attachment = self.command_obj.create_attachment("message",
                                                        "query",
                                                        "intent",
                                                        "link",
                                                        "bm25",
                                                        "qscore",
                                                        None,
                                                        None,
                                                        None,
                                                        None)
        self.assertEqual("actions" in attachment, True)
        self.assertEqual("I like the answer" in attachment, True)
        self.assertEqual("message" in attachment, True)

    def test_post_message_to_middleware_with_adequate_data(self):
        parsed_message = {
                            'text' : "What is a java for-loop?",
                            'entities' : [],
                            'intent'   : {
                                            'name' : "programming_factoid",
                                            'confidence' : "99"
                                         }
                         }
        parsed_output = self.command_obj.post_message_to_middleware(parsed_message)
        self.assertEqual("answer" in parsed_output[0][1], True)
        self.assertEqual(isinstance(parsed_output[0][0], str), True)

    def test_post_message_to_middleware_with_inadequate_data(self):
        parsed_message = {
                            'text' : "",
                            'entities' : [],
                            'intent'   : {
                                            'name' : "",
                                            'confidence' : ""
                                         }
                         }
        parsed_output = self.command_obj.post_message_to_middleware(parsed_message)
        self.assertEqual("answer" in parsed_output[0][1], False)
        self.assertEqual(isinstance(parsed_output[0][0], str), True)

    def test_is_for_handling(self):
        event = {}
        self.assertEqual(self.command_obj.is_for_handling(event), False)
        event = {'type' : "message"}
        self.assertEqual(self.command_obj.is_for_handling(event), False)
        event = {'type' : "message", 'user' : "me"}
        self.assertEqual(self.command_obj.is_for_handling(event), True)
