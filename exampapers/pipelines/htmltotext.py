#encoding:utf8
import re
def clean_tags(html, pa='<[^>]*>'):
    return re.sub(pa, '', html)   
from html2text import html2text
                 
class HtmlToTextPipeline(object):
    def process_item(self, item, spider):
        item['question_content'] = clean_tags(item['question_content_html']).strip()
        item['question_answer'] = clean_tags(item['question_answer_html']).strip()
        item['question_analysis'] = clean_tags(item['question_analysis_html']).strip()
        #item['question_comment'] = clean_tags(item['question_comment_html'])
        return item
