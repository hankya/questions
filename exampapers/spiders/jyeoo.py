'''this file defines the spider for jyeoo.com'''
from scrapy.contrib.loader.processor import Compose, TakeFirst
from scrapy.selector import HtmlXPathSelector
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.contrib.loader import XPathItemLoader
from scrapy.http import Request, HtmlResponse
from scrapy import log
import re
import os

from exampapers.questionmodels.models import QuestionItem
from exampapers.utils import enqueue_imgs, get_path_from_url, rewrite_imgsrc_abs, get_uuid

def add_meta(request):
    request.meta['skip'] = True
    return request

class JyeooSpider(CrawlSpider):
    name = 'jyeoo'
    allowed_domains = ['www.jyeoo.com','img.jyeoo.net']
    start_urls = ['http://www.jyeoo.com/chemistry', 'http://www.jyeoo.com/bio', 'http://www.jyeoo.com/math', 'http://www.jyeoo.com/math2', 'http://www.jyeoo.com/math3', 'http://www.jyeoo.com/physics'] 
    
    ban_codes = [403, 500, 503]
    captcha_symptom = 'x'

    __item_url_pattern = re.compile('http://www.jyeoo.com/\w+/ques/detail/[A-Za-z0-9]{8}-[A-Za-z0-9]{4}-[A-Za-z0-9]{4}-[A-Za-z0-9]{4}-[A-Za-z0-9]{12}')
    
    rules = (
        Rule(SgmlLinkExtractor(allow=('http://www.jyeoo.com/\w+/report/detail/[A-Za-z0-9]{8}-[A-Za-z0-9]{4}-[A-Za-z0-9]{4}-[A-Za-z0-9]{4}-[A-Za-z0-9]{12}',)), callback='parse_items', process_request=add_meta),
        Rule(SgmlLinkExtractor(allow=('http://www.jyeoo.com/\w+/report/search.+',)),),
        )     
    
    def is_valid_response(self, response):
        if type(response) is HtmlResponse:
            if len(response.body) < 4000:
                return False
        return True
            
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
                            difficult_level_signs = field.select('following-sibling::span[1]/em/text()').extract()
                            item['difficult_level'] = difficult_level_signs[0].count(u'\u2605') if difficult_level_signs else 0
                            item['question_type'] = question_type
                            item['question_number'] = question_counter
                            item['question_content_html'] = rewrite_imgsrc_abs(field.extract(), response.url)
                            item['paper_url'] = response.url
                            
                            req = Request(url, callback=self.parse_item)
                            req.meta['item'] = item
                            req.meta['skip'] = True  
                            yield req       
    
    def parse_item(self, response):
        hxs= HtmlXPathSelector(response)
        item = response.request.meta['item']
        #here need to create requests from img sources
        base_url = '/'.join(response.url.split('/')[:3])
        #capture all images
        enqueue_imgs(self.name, base_url, hxs.select('//img/@src').extract())
        
        item['question_id'] = get_uuid()
        item['url'] = response.url        
        #!--todo, if answer is not showing, grab it from content
        item['question_answer_html'] = rewrite_imgsrc_abs(hxs.select('//fieldset/div[@class="pt6"]').extract(), response.url)
        #item['question_comment_html'] = hxs.select('//fieldset/div[@class="pt6"]').extract()
        item['question_analysis_html'] = hxs.select('//fieldset/div[@class="pt5"]/text()').extract()
        item['knowledge_points'] = ','.join(hxs.select('//fieldset/div[@class="pt3"]/a/text()').extract())  
        yield item
        
#    def parse_image(self, response):
#        filename = get_path_from_url(response.url)
#        folder = os.path.join('/mnt/images', filename[:2])
#        if not os.path.exists(folder):
#            os.makedirs(folder)
#        filepath = os.path.join(folder, filename)
#        if not os.path.exists(filepath): 
#            with open(filepath, 'wb') as f:
#                f.write(response.body)
#                f.flush()
#        pass
