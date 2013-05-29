#encoding:utf8
import re

class DjangoWriterPipeline(object):
    def process_item(self, item, spider):
        paper_name = item['paper_name']
        item['question_type'] = question_type_classifier(item['question_type'])
        item['source'] = paper_source_classifier(paper_name)
        item['year'] = paper_year_classifier(paper_name)
        item['paper_type'] = paper_type_classifier(paper_name)
        item['region'] = paper_region_classifier(paper_name)
        #item['grade'] = paper_grade_classifier(paper_name)
        #item['subject'] = paper_subject_classifier(paper_name)     
        item['paper_name'] = paper_name.replace(u' - \u83c1\u4f18\u7f51', '')
        item.save()
        return item
        
question_types = {'选择':u'\u9009\u62e9\u9898','填空':u'\u586b\u7a7a\u9898','解答':u'\u89e3\u7b54\u9898'}
     
def question_type_classifier(type_str):
    question_types = {'选择':u'\u9009\u62e9\u9898','填空':u'\u586b\u7a7a\u9898','解答':u'\u89e3\u7b54\u9898'}
    for question_type in question_types:
        if type_str.find(question_types[question_type][:2]) > -1:
            return question_types[question_type]
    return type_str

def paper_year_classifier(paper_name):
    return '-'.join(re.findall('\d{4}', paper_name))

paper_types = {'竞赛' : u'\u7ade\u8d5b','比赛' : u'\u6bd4\u8d5b', '中考' : u'\u4e2d\u8003', '高考' : u'\u9ad8\u8003', '期中' : u'\u671f\u4e2d', '期末' : u'\u671f\u672b', '月考' : u'\u6708\u8003'}

def paper_type_classifier(paper_name):
    for paper_type in paper_types:
        if paper_name.find(paper_types[paper_type]) > -1:
            return paper_types[paper_type]
    return u'unknown'
    
def paper_source_classifier(paper_name):
    return u''
    
#pattern to match region, \u7701 = ﻿省, \u5e02=市, u'\u5e74'=年, u'\u5ea6'=度,
REGION_PATTERN = [re.compile(u'\u5e74\u5ea6([^\u5ea6].+\u7701)'), re.compile(u'\u5e74\u5ea6([^\u5ea6].+\u5e02)'), re.compile(u'\u5e74([^\u5e74].+\u7701)'),  re.compile(u'\u5e74([^\u5e74].+\u5e02)')]

def paper_region_classifier(paper_name):
    if paper_name.find(u'\u5168\u56fd') > -1:
        return u'\u5168\u56fd'
    for mp in REGION_PATTERN:
        m = mp.search(paper_name)
        if m:
            return m.groups()[0]
            
    return u'unknown'
    
def paper_grade_classifier(paper_name):
    m = re.search(u'.\u5e74\u7ea7\uff08.\uff09', paper_name)
    return m.group() if m else paper_name[-10:-8]
    
def paper_subject_classifier(paper_name):
    return paper_name[-8:-6]
