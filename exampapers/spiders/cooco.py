'''this file defines the spider for jyeoo.com'''
from scrapy.contrib.loader.processor import Compose, TakeFirst
from scrapy.selector import HtmlXPathSelector
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.contrib.loader import XPathItemLoader
from scrapy.http import Request
from scrapy.utils.response import get_base_url
from scrapy import log

import re
import os

from exampapers.utils import urls_from_imgs, get_path_from_url, rewrite_imgsrc, get_uuid
from exampapers.questionmodels.models import QuestionItem

def add_meta(request):
    request.meta['skip'] = True
    return request

class CoocoSpider(CrawlSpider):
    name = 'cooco'
    allowed_domains = ['cooco.net.cn']
    start_urls = ['http://gzsx.cooco.net.cn/','http://gzwl.cooco.net.cn/','http://gzhx.cooco.net.cn/','http://czsx.cooco.net.cn/','http://czhx.cooco.net.cn/','http://czwl.cooco.net.cn/']         
    
    rules = (
        Rule(SgmlLinkExtractor(allow=('http://\w+.cooco.net.cn/user/newdown/\d+/?$', 'http://\w+.cooco.net.cn/shijuan/\d+/?$', ),),),
        Rule(SgmlLinkExtractor(allow=('http://\w+.cooco.net.cn/paper/\d+/?',)), callback='parse_items', process_request=add_meta),
        #Rule(SgmlLinkExtractor(allow=('http://\w+.cooco.net.cn/.*\.[bmp|gif|png|jpg|jpeg]',), tags=('a', 'img'), attrs=('href', 'src'),), callback='parse_image', ),
        )     
    ban_codes = [400, 403]
        
    def is_valid_response(self, response):
        if response.status == 404:
            return False
        if response.body.find('<html><body><br><br><br><script>window.location=') > -1:
            return False
        return True
        
    def parse_items(self, response):
        hxs = HtmlXPathSelector(response)
        base_url = '/'.join(response.url.split('/')[:3])
        
        #capture all images
        image_urls = urls_from_imgs(hxs.select('//img/@src').extract())
        for image_url in image_urls:
            req = Request(image_url, callback=self.parse_image)
            yield req
        
        paper_name = hxs.select('//div[@class="spy"]/text()').extract()[1].strip()
        
        questions = hxs.select('//ul[@id="test"]/li')
        for question in questions:
            item = QuestionItem()
            item['paper_name'] = paper_name.replace(' ', '')
            item['grade'] = paper_name[0:2]
            item['subject'] = paper_name[2:4]
            item['image_urls'] = u''
            item['question_id'] = get_uuid()
            item['question_number'] = 1
            item['paper_url'] = response.url
            item['url'] = response.url
            statics = question.select('.//span[@style="color:blue;"]/text()').extract()
            item['question_type'] = statics[0] if statics else u''
            item['knowledge_points'] = statics[1] if len(statics) > 1 else u''
            #rewrite the image source so when taking screenshot we do not depend on internet
            item['question_content_html'] = rewrite_imgsrc(''.join(question.select('.//p').extract()), response.url)
            difficult_level_signs = question.select('div/div[1]/div/img/@src').extract()
            item['difficult_level'] = len(filter(lambda s:s==u'/site_media/img/sts.gif', difficult_level_signs))
            answer_id = question.select('.//div[@class="daan"]/@id').extract()
            if answer_id:
                answer_url = urlparse.urljoin(base_url, 'answerdetail/%s/' % answer_id[0].split('-')[1])
                req = Request(answer_url, callback=self.parse_item)
                req.meta['item'] = item
                req.meta['skip'] = True
                yield req
            else:
                yield item
                                  
    def parse_item(self, response):
        #log.msg('parsing new item %s' % response.url, level=log.ERROR)
        response_url = response.url
        hxs = HtmlXPathSelector(response)
        item = response.request.meta['item']
        item['question_answer_html'] = response.body_as_unicode()
        item['question_analysis_html'] = u'<body></body>',
        #img_urls = set(hxs.select('//img/@src').extract())
        #for img_url in img_urls:
            #item['image_urls'].append(urlparse.urljoin(get_base_url(response), img_url))
        return item

    def parse_image(self, response):
        filename = get_path_from_url(response.url)
        #specify the folder path
        folder = os.path.join('/mnt/images', filename[:2])
        if not os.path.exists(folder):
            os.makedirs(folder)
        filepath = os.path.join(folder, filename)
        if not os.path.exists(filepath): 
            with open(filepath, 'wb') as f:
                f.write(response.body)
                f.flush()
        pass
