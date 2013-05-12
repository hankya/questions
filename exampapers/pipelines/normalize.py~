from scrapy.utils.request import request_fingerprint

from lxml import html
import re
import os

abs_url_pattern = re.compile('http://[^/]+/.*')

def rewrite_imgsrc(value):
    return [_rewrite_imgsrc(v) for v in value] if hasattr(value, '__iter__') else _rewrite_imgsrc(value)    
    
def _rewrite_imgsrc(value):
    hdoc = html.fromstring(value)
    imgs = hdoc.xpath('//img')
    for img in imgs:
        img_link = img.get('src')
        filename = get_path_from_url(request.url)
        img.set('src', os.path.join('images', filename[:2], filename))
    return html.tostring(hdoc, encoding='unicode')

def get_path_from_url(url):
        tokens = url.split('/')
        return '%s.%s' % (hashlib.sha1(url).hexdigest(), tokens[-1].split('.')[-1])

class UrlRewriterPipeline(object):
    def process_item(self, item, spider):
        item['question_answer_html'] = rewrite_imgsrc(item['question_answer_html'])
        item['question_analysis_html'] = rewrite_imgsrc(item['question_analysis_html'])
        item['question_content_html'] = rewrite_imgsrc(item['question_content_html'])
        return item
        
class AnswerPipeline(object):
    def process_item(self, item, spider):
    
        def process_answer(answer_html, content_html):
           if answer_html.find(u'\u67e5\u770b\u672c\u9898\u89e3\u6790\u9700\u8981') > -1:
               hdoc = html.fromstring(content_html)
               ma = hdoc.xpath('//label[@class=" s"]/text()')
               if ma:
                   return ','.join([m[0] for m in ma])
               ma = hdoc.xpath('//div[@class="sanwser"]/text()')
               return ','.join([m for m in ma]) if ma else u'unknown'
               
        answer = process_answer(item['question_answer_html'], item['question_content_html'])
        if answer:
            item['question_answer'] = answer
            item['question_answer_html'] = u''
        return item
