from scrapy.contrib.spiders import CrawlSpider

from redis import StrictRedis

class FSpider(CrawlSpider):
    
    redis_cli = StrictRedis(host='localhost', port=6379, db=0)
    
    def start_requests(self):
        failure_url = self.redis_cli.lpop('%s_failures' % self.name)
        while failure_url:
            yield self.make_requests_from_url(failure_url)
            failure_url = self.redis_cli.lpop('%s_failures' % self.name)
            
        for url in self.start_urls:
            yield self.make_requests_from_url(url)
            
        
