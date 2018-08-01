import json
import os
import time

from nltk.parse.corenlp import CoreNLPParser

from recognizers_text import Culture, ModelResult
from recognizers_number import NumberRecognizer
from recognizers_number_with_unit import NumberWithUnitRecognizer
from recognizers_date_time import DateTimeRecognizer


class RPG:
    def __init__(self, comment_data, storage_path, corenlp_url):
        self.storage_path = storage_path
        self.parser = CoreNLPParser(url=corenlp_url)

    def create_question_json(self, comment_data, max_question_word_count):
        question_symbols = {'SBARQ', 'SQ'}
        try:
            os.remove(os.path.join(self.storage_path,
                                   'questions_' + comment_data.name))
        except OSError:
            pass
        a = open(os.path.join(self.storage_path,
                              'questions_' + comment_data.name), 'a')
        for line in comment_data:
            answer = next(comment_data)
            json_line = json.loads(line)
            property = str(json_line['body'])
            if len(property.split()) > max_question_word_count:
                continue
            try:
                parse_trees = self.parser.parse_text(property)
                for parse_tree in parse_trees:
                    for subtree in parse_tree.subtrees():
                        if subtree.label() in question_symbols:
                            a.write(line)
                            a.write(answer)
                            raise Exception('Prevent duplicate write')
            except Exception as e:
                pass
        return a

    def perform_ner(self, comment_data, entity_type):
        try:
            os.remove(entity_type + '_' + comment_data)
        except OSError:
            pass
        a = open(entity_type + '_' + comment_data, 'a')

        recognizer = NumberRecognizer(Culture.English)
        model = recognizer.get_number_model()
        for line in comment_data:
            answer = next(comment_data)

            question_json = json.loads(line)
            answer_json = json.loads(answer)

            text = str(answer_json['body'])
            try:
                result = model.parse(text)
                if result:
                    for x in result:
                        print(x.type_name)
                        if x.type_name == entity_type:
                            print('<')
                            print(text)
                            print('RES: ' + str(x.resolution) + '\n')
                            print('>')
                            a.write(line)
                            a.write(answer)
                            break
            except Exception as e:
                print(e)
        return a

    def create_subreddit_json(self, comment_data, subreddit):
        file_path = os.path.join(
            self.storage_path, subreddit + '_' + os.path.basename(comment_data.name))
        print(file_path)
        subreddit = subreddit.lower()
        try:
            os.remove(file_path)
        except OSError:
            pass
        a = open(file_path, 'a')
        for line in comment_data:
            try:
                json_line = json.loads(line)
            except Exception as e:
                print(e)
                continue
            if json_line['subreddit'].lower() == subreddit:
                a.write(line)
        return a

    def find_comment_pairs(self, comment_data, min_score):
        file_path = os.path.join(
            self.storage_path, 'pairs_' + os.path.basename(comment_data.name))
        try:
            os.remove(file_path)
        except OSError:
            pass
        a = open(file_path, 'a')
        print(file_path)
        comment_data_comparison = comment_data
        comment_data_comparison.seek(0)
        for line in comment_data:
            try:
                comment = json.loads(line)
            except Exception as e:
                print(e)
                continue
            if comment['score'] > min_score:
                comment_data_comparison.seek(0)
                highest_score_comparison = {'score': 0}
                for line_comparison in comment_data_comparison:
                    print('hello')
                    try:
                        comment_comparison = json.loads(line_comparison)
                    except Exception as e:
                        print(e)
                        continue
                    if (comment['parent_id'][3:] == comment_comparison['id'] and
                            comment_comparison['score'] > highest_score_comparison['score']):
                        highest_score_comparison = comment_comparison
                if highest_score_comparison['score'] > 0:
                    a.write(json.dumps(highest_score_comparison) + '\n')
                    a.write(line)
        return a
