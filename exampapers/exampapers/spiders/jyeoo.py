'''this file defines the spider for jyeoo.com'''
from scrapy.contrib.loader.processor import Compose, TakeFirst
from scrapy.selector import HtmlXPathSelector
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.contrib.loader import XPathItemLoader
from scrapy.http import Request
from scrapy import log
import re

from exampapers.questionmodels.models import QuestionItem

def add_meta(request):
    request.meta['skip'] = True
    return request

class JyeooSpider(CrawlSpider):
    name = 'jyeoo'
    allowed_domains = ['www.jyeoo.com','img.jyeoo.net']
    start_urls = ['http://www.jyeoo.com/chemistry',] 
    
    ban_codes = [403, 500, 503]
    captcha_symptom = 'x'

    __item_url_pattern = re.compile('http://www.jyeoo.com/\w+/ques/detail/[A-Za-z0-9]{8}-[A-Za-z0-9]{4}-[A-Za-z0-9]{4}-[A-Za-z0-9]{4}-[A-Za-z0-9]{12}')
    
    rules = (
        Rule(SgmlLinkExtractor(allow=('http://www.jyeoo.com/\w+/report/detail/[A-Za-z0-9]{8}-[A-Za-z0-9]{4}-[A-Za-z0-9]{4}-[A-Za-z0-9]{4}-[A-Za-z0-9]{12}',)), callback='parse_items', process_request=add_meta),
        Rule(SgmlLinkExtractor(allow=('http://www.jyeoo.com/\w+/report/search.+',)),),
        )     
            
    def parse_items(self, response):
        hxs = HtmlXPathSelector(response)
        paper_name = hxs.select("//title/text()").extract()[0]
        exam_type = hxs.select("//li[@class='active']/a/text()").extract()[0]
        
        #select all the question categories
        question_types = hxs.select('//h3')
        question_counter = 0
        
        for question_type in question_types:
            question_container = question_type.select('following-sibling::div[1]') 
            if question_container:
                question_type_text = question_type.select('text()').extract()
                question_type = question_type_text[0][0:49] if question_type_text else ''
                fieldset = question_container[0].select('fieldset')
                for field in fieldset:
                    url = field.select('following-sibling::span[1]/a/@href').extract()
                    if url:
                        url = url[0]
                        if self.__item_url_pattern.match(url):
                            question_counter = question_counter + 1
                            item = QuestionItem()
                            item['paper_name'] = paper_name
                            item['difficult_level'] = field.select('following-sibling::span[1]/em/text()').extract()
                            item['question_type'] = question_type
                            item['question_number'] = question_counter
                            item['question_content_html'] = field.extract()
                            item['paper_url'] = response.url
                            
                            req = Request(url, callback=self.parse_item)
                            req.item = item
                            req.meta['skip'] = True  
                            yield req       
    
    def parse_item(self, response):
        log.msg('parsing new item %s' % response.url, level=log.ERROR)
        hxs= HtmlXPathSelector(response)
        item = response.request.item
        item['image_urls'] = set(hxs.select('//img/@src').extract())
        item['question_id'] = get_uuid()
        item['url'] = response.url
        
        #!--todo, if answer is not showing, grab it from content
        item['question_answer_html'] = hxs.select('//fieldset/div[@class="pt6"]').extract()
        item['question_comment_html'] = hxs.select('//fieldset/div[@class="pt6"]').extract()
        item['question_analysis_html'] = hxs.select('//fieldset/div[@class="pt5"]/text()').extract()
        item['knowledge_points'] = hxs.select('//fieldset/div[@class="pt3"]/a/text()').extract()
  
        return item

from lxml import html
abs_url_pattern = re.compile('http://[^/]+/.*')

def rewrite_imgsrc(value):
    return [_rewrite_imgsrc(v) for v in value] if hasattr(value, '__iter__') else _rewrite_imgsrc(value)    
    
def _rewrite_imgsrc(value):
    hdoc = html.fromstring(value)
    imgs = hdoc.xpath('//img')
    for img in imgs:
        img_link = img.get('src')
        if abs_url_pattern.match(img_link):
            img.set('src', '/'.join(img_link.split('/')[3:]) )
    #or return html.tostring(hdoc, encoding='utf8').decode('utf8')
    return html.tostring(hdoc, encoding='unicode')
        
import uuid
def get_uuid():
    return uuid.uuid4().hex
    
