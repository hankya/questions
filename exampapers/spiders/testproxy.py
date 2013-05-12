from scrapy.spider import BaseSpider
from redis import StrictRedis

class TestProxy (BaseSpider):

    name = 'test_proxy'
    redis_cli = StrictRedis(host='localhost', port=6379, db=0)
    
    def start_requests(self):
        for proxy in self.redis_cli.smembers('proxies'):
            req = self.make_requests_from_url('http://www.baidu.com')
            req.meta['proxy'] = proxy
            self.redis_cli.srem('proxies', proxy)
            yield req
       
    def parse(self, response):
        self.redis_cli.sadd('proxies', response.request.meta['proxy'])
        pass
        
        
        
        
        


