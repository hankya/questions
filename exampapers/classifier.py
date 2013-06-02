#encoding:utf8
import re
from exampapers.utils import clean_tags

question_types = {'选择':u'\u9009\u62e9\u9898','填空':u'\u586b\u7a7a\u9898','解答':u'\u89e3\u7b54\u9898'}

def question_type_classifier(type_str):
    question_types = {'选择':u'\u9009\u62e9\u9898','填空':u'\u586b\u7a7a\u9898','解答':u'\u89e3\u7b54\u9898'}
    for question_type in question_types:
        if type_str.find(question_types[question_type][:2]) > -1:
            return question_types[question_type]
    return type_str
    
def is_answer_unique(type_str):
    if type_str == u'\u9009\u62e9\u9898':
        return True
    return False    

def extract_answer_info(type_str, answer_html, p):
    question_type = question_type_classifier(type_str)
    is_unique = is_answer_unique(question_type)
    answer_text = clean_tags(answer_html)
    unique_answer = extract_answer(answer_html, p, answer_text) if is_unique else u''
    return question_type, is_unique, answer_text, unique_answer
    
def extract_answer_info_text(type_str, answer):
    question_type = question_type_classifier(type_str)
    is_unique = is_answer_unique(question_type)
    unique_answer = answer if is_unique else u''
    return question_type, is_unique, unique_answer

def extract_answer_text(answer_html):
    return clean_tags(answer_html)

def extract_answer(answer_html, p, answer_text):
    for pa in p:
        m = re.search(pa, answer_html)
        if m:
            return m.groups()[0]
    return answer_text[:25]
