from scrapy import log
from scrapy.contrib.downloadermiddleware.retry import RetryMiddleware
from scrapy.exceptions import IgnoreRequest
from scrapy.utils.response import response_status_message

from redis import StrictRedis

class EnhancedRetryMiddleware(RetryMiddleware):

    redis_cli = StrictRedis(host='localhost', port=6379, db=0)
        
    def _retry(self, request, reason, spider):
        retries = request.meta.get('retry_times', 0) + 1

        if retries <= self.max_retry_times:
            log.msg(format="Retrying %(request)s (failed %(retries)d times): %(reason)s",
                    level=log.DEBUG, spider=spider, request=request, retries=retries, reason=reason)
            retryreq = request.copy()
            retryreq.meta['retry_times'] = retries
            retryreq.dont_filter = True
            retryreq.priority = request.priority + self.priority_adjust
            return retryreq
        else:
            log.msg(format="Gave up retrying %(request)s (failed %(retries)d times): %(reason)s",
                    level=log.ERROR, spider=spider, request=request, retries=retries, reason=reason)
            self.redis_cli.rpush('%s_failures' % spider.name, 
                    (request.url, request.headers.get('Referer') or None))

