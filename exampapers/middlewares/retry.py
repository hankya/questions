from scrapy import log

from redis import StrictRedis

class RetryMiddleware (object):

    redis_cli = StrictRedis(host='localhost', port=6379, db=0)
    
    def __init__(self, settings):
        if not settings.getbool('RETRY_ENABLED'):
            raise NotConfigured
        self.max_retry_times = settings.getint('RETRY_TIMES')
        
        
    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)
        
    def process_response(self, request, response, spider):
        """
            this middleware will log failure in download, and it retry the request if the content of the
            respons is not valid by setting its status code to 500, its next slibing middleware will retry 
            it when it see the status code 500
        """
        
        retries = request.meta.get('retry_times', 0) + 1 
        if retries > self.max_retry_times:
            log.msg(request.url, level=log.ERROR)
            self.redis_cli.sadd('%s_failures' % spider.name, request.url)
        if not spider.is_valid_response(response):
            response.status = 500
                                
        return response
