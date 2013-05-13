from scrapy import log
from scrapy.contrib.downloadermiddleware.retry import RetryMiddleware
from scrapy.exceptions import IgnoreRequest
from scrapy.utils.response import response_status_message

from redis import StrictRedis

class EnhancedRetryMiddleware(RetryMiddleware):

    redis_cli = StrictRedis(host='localhost', port=6379, db=0)

    def process_response(self, request, response, spider):
        """
            this middleware will log failure in download, and it retry the request if the content of the
            respons is not valid by setting its status code to 500, its next slibing middleware will retry 
            it when it see the status code 500
        """
        if 'dont_retry' in request.meta:
            return response
        if response.status in self.retry_http_codes or not spider.is_valid_response(response):
            reason = response_status_message(response.status)
            req = self._retry(request, reason, spider)
            if req:
                return req
            else:
                raise IgnoreRequest
                
        return response
        
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

