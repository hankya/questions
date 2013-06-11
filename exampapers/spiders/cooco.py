'''this file defines the spider for jyeoo.com'''
from scrapy.contrib.loader.processor import Compose, TakeFirst
from scrapy.selector import HtmlXPathSelector
from scrapy.contrib.spiders import Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.contrib.loader import XPathItemLoader
from scrapy.http import Request, HtmlResponse
from scrapy.utils.response import get_base_url
from scrapy import log

import re
import os
import urlparse
from exampapers.utils import enqueue_imgs, get_path_from_url, rewrite_imgsrc_abs
from exampapers.classifier import extract_answer_info
from exampapers.questionmodels.models import QuestionItem
from exampapers.spiders.fspider import FSpider

def add_meta(request):
    request.meta['skip'] = True
    return request

class CoocoSpider(FSpider):
    name = 'cooco'
    allowed_domains = ['cooco.net.cn']
    start_urls = ['http://gzwl.cooco.net.cn/user/newdown/50/', 'http://gzhx.cooco.net.cn/user/newdown/50/', 'http://gzsx.cooco.net.cn/user/newdown/50/', 'http://gzyw.cooco.net.cn/shijuan/50/', 'http://gzls.cooco.net.cn/shijuan/50/', 'http://gzsw.cooco.net.cn/shijuan/50/', 'http://gzdl.cooco.net.cn/shijuan/50/', 'http://gzzz.cooco.net.cn/shijuan/50/', 'http://gzyy.cooco.net.cn/shijuan/50/', 'http://czwl.cooco.net.cn/user/newdown/50/', 'http://czhx.cooco.net.cn/user/newdown/50/', 'http://czsx.cooco.net.cn/user/newdown/50/', 'http://czyw.cooco.net.cn/shijuan/50/', 'http://czls.cooco.net.cn/shijuan/50/', 'http://czsw.cooco.net.cn/shijuan/50/', 'http://czdl.cooco.net.cn/shijuan/50/', 'http://czzz.cooco.net.cn/shijuan/50/', 'http://czyy.cooco.net.cn/shijuan/50/']         
    
    rules = (
        Rule(SgmlLinkExtractor(allow=('http://\w+.cooco.net.cn/user/newdown/\d+/?$', 'http://\w+.cooco.net.cn/shijuan/\d+/?$', ),),),
        Rule(SgmlLinkExtractor(allow=('http://\w+.cooco.net.cn/paper/\d+/?',)), callback='parse_items', process_request=add_meta),
        #Rule(SgmlLinkExtractor(allow=('http://\w+.cooco.net.cn/.*\.[bmp|gif|png|jpg|jpeg]',), tags=('a', 'img'), attrs=('href', 'src'),), callback='parse_image', ),
        )     
    ban_codes = [400, 403]
        
    def is_valid_response(self, response):
        if type(response) is HtmlResponse:
            if response.body.find('<html><body><br><br><br><script>window.location=') > -1:
                return False
            if not response.body.strip():
                return False
            if response.url.find('answerdetail') > -1:
                if response.body.find('<html xmlns') > -1:
                    return False
        return True
        
    def parse_items(self, response):
        hxs = HtmlXPathSelector(response)
        base_url = '/'.join(response.url.split('/')[:3])
        
        #capture all images
        enqueue_imgs(self.name, base_url, hxs.select('//img/@src').extract())

        paper_name = u''
        try:
            paper_name = hxs.select('//div[@class="spy"]/text()').extract()[1].strip()
        except:
            log.msg("fail to extract %s" % response.body, level=log.ERROR)
            
        questions = hxs.select('//ul[@id="test"]/li')
        for question in questions:
            item = QuestionItem()
            item['paper_name'] = paper_name.replace(' ', '')
            item['grade'] = paper_name[0:2]
            item['subject'] = paper_name[2:4]
            #item['image_urls'] = u''
            #item['question_id'] = get_uuid()
            item['question_number'] = 1
            item['paper_url'] = response.url
            item['url'] = response.url
            statics = question.select('.//span[@style="color:blue;"]/text()').extract()
            item['question_type'] = statics[0] if statics else u''
            item['knowledge_points'] = statics[1] if len(statics) > 1 else u''
            #rewrite the image source so when taking screenshot we do not depend on internet
            item['question_content_html'] = rewrite_imgsrc_abs(''.join(question.select('.//p').extract()), \
            base_url)
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
    
    no_answer = u'1\u3001\u6240\u6709\u8bd5\u9898\u90fd\u6709\u7b54\u6848\uff0c\u8bf7\u653e\u5fc3\u7ec4\u5377'
                                  
    def parse_item(self, response):
        #log.msg('parsing new item %s' % response.url, level=log.ERROR)
        response_url = response.url
        hxs = HtmlXPathSelector(response)
        item = response.request.meta['item']
        body = response.body_as_unicode()
        if body.find(self.no_answer) > -1:
            item['question_answer_html'] = u''
        else:
            item['question_answer_html'] = ''.join(rewrite_imgsrc_abs(response.body_as_unicode(), response.url))            
        item['question_type'], item['is_answer_unique'], item['question_answer'], item['unique_answer'] = \
            extract_answer_info(item['question_type'], item['question_answer_html'], \
            [u'<p>1\u3001<span>(\w)</span>',])
        item['question_analysis_html'] = u''
        return item
