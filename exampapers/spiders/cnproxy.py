from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.selector import HtmlXPathSelector
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor

from redis import StrictRedis


class ProxySpider (CrawlSpider):
    name = 'cnproxy'
    allowed_domains = ['www.cnproxy.com']
    start_urls = ['http://www.cnproxy.com/proxy1.html',]
    rules = (
        Rule(SgmlLinkExtractor(allow=('http://www.cnproxy.com/proxy\d+.html',)), callback='parse_item',),
        #Rule(SgmlLinkExtractor(allow=('.*',)),),
        )
    redis_cli = StrictRedis(host='localhost', port=6379, db=0)
    
    mapping = {'z':"3", 'm':"4", 'a':"2", 'l':"9", 'f':"0", 'b':"5", 'i':"7", 'w':"6", 'x':"8", 'c':"1" }
    
    def parse_item(self, response):
        hxs = HtmlXPathSelector(response)
        trs = hxs.select('//div[@id="proxylisttb"]/table[3]/tr')
        trs.remove(trs[0])
        
        for tr in trs:
            o = tr.select('td[1]/script/text()').extract()[0][:-1].split('+')
            o.remove(o[0])
            try:
                port = ''.join([self.mapping[c] for c in o])
            except KeyError:
                prot = ':80'
            
            proxy = '%s://%s:%s' % (tr.select('td[2]/text()').extract()[0], tr.select('td[1]/text()').extract()[0], port)
            self.redis_cli.sadd('proxies', proxy)
            
        pass
        
        

