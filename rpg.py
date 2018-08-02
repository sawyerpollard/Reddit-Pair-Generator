import json
import os
import time

from nltk.parse.corenlp import CoreNLPParser

from recognizers_text import Culture, ModelResult
from recognizers_number import NumberRecognizer
from recognizers_number_with_unit import NumberWithUnitRecognizer
from recognizers_date_time import DateTimeRecognizer


class RPG:
    def __init__(self, storage_path, corenlp_url):
        self.storage_path = os.path.abspath(storage_path)
        self.parser = CoreNLPParser(url=corenlp_url)

    def create_question_json(self, filepath: str, max_question_word_count: int = 30, update: bool = False) -> str:
        newfilepath = os.path.join(
            self.storage_path, 'questions_' + os.path.basename(filepath))
        if not update and os.path.exists(newfilepath):
            return newfilepath
        wfile = open(newfilepath, 'w')

        filepath = os.path.abspath(filepath)
        rfile = open(filepath, 'r')

        question_symbols = {'SBARQ', 'SQ'}

        for line in rfile:
            answer = next(rfile)
            json_line = json.loads(line)
            property = str(json_line['body'])
            if len(property.split()) > max_question_word_count:
                continue
            try:
                parse_trees = self.parser.parse_text(property)
                for parse_tree in parse_trees:
                    for subtree in parse_tree.subtrees():
                        if subtree.label() in question_symbols:
                            wfile.write(line)
                            wfile.write(answer)
                            raise Exception('Prevent duplicate write')
            except Exception as e:
                pass
        return newfilepath

    def perform_ner(self, filepath: str, entity_type: str = 'number', update: bool = False) -> str:
        newfilepath = os.path.join(
            self.storage_path, entity_type + '_' + os.path.basename(filepath))
        if not update and os.path.exists(newfilepath):
            return newfilepath
        wfile = open(newfilepath, 'w')

        filepath = os.path.abspath(filepath)
        rfile = open(filepath, 'r')

        recognizer = NumberRecognizer(Culture.English)
        model = recognizer.get_number_model()
        for line in rfile:
            answer = next(rfile)

            answer_json = json.loads(answer)

            text = str(answer_json['body'])
            try:
                result = model.parse(text)
                if result:
                    for x in result:
                        if x.type_name == entity_type:
                            wfile.write(line)
                            wfile.write(answer)
                            break
            except Exception as e:
                print(e)
        return newfilepath

    def create_subreddit_json(self, filepath: str, subreddit: str, update: bool = False) -> str:
        subreddit = subreddit.lower()

        newfilepath = os.path.join(
            self.storage_path, subreddit + '_' + os.path.basename(filepath))
        if not update and os.path.exists(newfilepath):
            return newfilepath
        wfile = open(newfilepath, 'w')

        filepath = os.path.abspath(filepath)
        rfile = open(filepath, 'r')

        for line in rfile:
            try:
                json_line = json.loads(line)
                if json_line['subreddit'].lower() == subreddit:
                    wfile.write(line)
            except Exception as e:
                print(e)

        rfile.close()
        wfile.close()
        return newfilepath

    def find_comment_pairs(self, filepath: str, min_score: int = 0, update: bool = False) -> str:
        newfilepath = os.path.join(
            self.storage_path, 'pairs_' + os.path.basename(filepath))
        if not update and os.path.exists(newfilepath):
            return newfilepath
        wfile = open(newfilepath, 'w')

        filepath = os.path.abspath(filepath)
        rfile = open(filepath, 'r')

        for line in rfile:
            try:
                comment = json.loads(line)
            except Exception as e:
                print(e)
                continue
            if comment['score'] > min_score:
                rfile_comparison = open(filepath, 'r')
                highest_score_comparison = {'score': 0}
                for line_comparison in rfile_comparison:
                    try:
                        comment_comparison = json.loads(line_comparison)
                    except Exception as e:
                        print(e)
                        continue
                    if (comment['parent_id'][3:] == comment_comparison['id'] and
                            comment_comparison['score'] > highest_score_comparison['score']):
                        highest_score_comparison = comment_comparison
                if highest_score_comparison['score'] > 0:
                    wfile.write(json.dumps(highest_score_comparison) + '\n')
                    wfile.write(line)
        return newfilepath
    
    def perform_all(self, filepath: str, subreddits: list, update: bool):
        for subreddit in subreddits:
            sub_time = time.time()
            sub = self.create_subreddit_json(filepath, subreddit, update = update)
            print('Subreddit comments file created in {:.2f} seconds'.format(time.time() - sub_time))

            pairs_time = time.time()
            pairs = self.find_comment_pairs(sub, update = update)
            print('Comment pairs file created in {:.2f} seconds'.format(time.time() - pairs_time))

            questions_time = time.time()
            questions = self.create_question_json(pairs, update = update)
            print('Question-answer file created in {:.2f} seconds'.format(time.time() - questions_time))

            ner_time = time.time()
            ner = self.perform_ner(questions)
            print('Entity file created in {:.2f} seconds'.format(time.time() - ner_time))