#encoding:utf8
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/topics/item-pipeline.html
class DjangoWriterPipeline(object):
    def process_item(self, item, spider):
        paper_name = item['paper_name']
        item['question_type'] = question_type_classifier(item['question_type'])
        item['source'] = paper_source_classifier(paper_name)
        item['year'] = paper_year_classifier(paper_name)
        item['paper_type'] = paper_type_classifier(paper_name)
        item['region'] = paper_region_classifier(paper_name)
        item['grade'] = paper_grade_classifier(paper_name)
        item['subject'] = paper_subject_classifier(paper_name)     
        item['paper_name'] = paper_name.replace(u' - \u83c1\u4f18\u7f51', '')
        item.save()
        return item
        
class FlattenItemPipeline(object):
    def process_item(self, item, spider):
        return flatten_item(item)
        
import re
def clean_tags(html, pa='<[^>]*>'):
    return re.sub(pa, '', html)   
                 
class HtmlToTextPipeline(object):
    def process_item(self, item, spider):
        item['question_content'] = clean_tags(item['question_content_html'])
        item['question_answer'] = clean_tags(item['question_answer_html'])
        item['question_analysis'] = clean_tags(item['question_analysis_html'])
        return item

        
from scrapy.contrib.pipeline.images import ImagesPipeline
from scrapy.exceptions import DropItem
from scrapy.http import Request
from scrapy.utils.misc import md5sum
from scrapy import log
import os

class MyImagesPipeline(ImagesPipeline):
    
    def image_downloaded(self, response, request, info):
        checksum = None
        for key, image, buf in self.get_images(response, request, info):
            if checksum is None:
                buf.seek(0)
                checksum = md5sum(buf)
                folder, filename = self.get_path_from_url(response.url)
                #to do, move the folder under screenshot containers.
                folder_path = os.path.join('images', folder)
                if not os.path.exists(folder_path):
                    os.makedirs(folder_path)
                filepath = os.path.join(folder_path, filename)
                if not os.path.exists(filepath):
                    image.save(filepath)          
        return checksum
        
    def get_path_from_url(self, url):
        tokens = url.split('/')
        return ('/').join(tokens[3:-1]), tokens[-1]
        
    
from redis import StrictRedis       
class ScreenshotPipeline(object):

    redis_cli = StrictRedis(host='localhost', port=6379, db=0)
    
    def process_item(self, item, spider):         
        screenshot_request = [item['url'], flatten(item['question_content_html']) , flatten(item['question_answer_html']), flatten(item['question_analysis_html'])]
        self.redis_cli.rpush('%s_screenshot_requests' % spider.name, screenshot_request)
        return item
        
question_types = {'选择':u'\u9009\u62e9\u9898','填空':u'\u586b\u7a7a\u9898','解答':u'\u89e3\u7b54\u9898'}
     
def question_type_classifier(type_str):
    question_types = {'选择':u'\u9009\u62e9\u9898','填空':u'\u586b\u7a7a\u9898','解答':u'\u89e3\u7b54\u9898'}
    for question_type in question_types:
        if type_str.find(question_types[question_type][:2]) > -1:
            return question_types[question_type]
    return u'unknown'

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
    
#pattern to match region, \u7701 = ﻿省, \u5e02=市
PROVINCE_PATTERN = re.compile(u'\u5e74([^\u5e74].+\u7701)')
CITY_PATTERN = re.compile(u'\u5e74([^\u5e74].+\u5e02)')

def paper_region_classifier(paper_name):
    m = PROVINCE_PATTERN.search(paper_name)
    if not m:
        m = CITY_PATTERN.search(paper_name)
    return m.groups()[0] if m else u'unknown'
    
def paper_grade_classifier(paper_name):
    m = re.search(u'.\u5e74\u7ea7\uff08.\uff09', paper_name)
    return m.group() if m else paper_name[-10:-8]
    
def paper_subject_classifier(paper_name):
    return paper_name[-8:-6]

def  flatten_item(item):
    for key in item.keys():
        item[key] = flatten(item[key])   
    return item
    
def flatten(value):
    if not isinstance(value, dict) and hasattr(value, '__iter__'):
            if isinstance(value, bool):
                value = value[0]
            else:
                value = ''.join(value)               
    return value
                    
def truncate(item):
    for key in item.keys():
        value = item[key]
        item[key] = unicode(value)
    return item
