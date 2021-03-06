from scrapy.utils.request import request_fingerprint
from scrapy.utils.job import job_dir
from scrapy import log

import os
from redis import StrictRedis
from time import time

class BaseDupeFilter(object):
    
        @classmethod
        def from_settings(cls, settings):
            return cls()
            
        def request_seen(self, request):
            return False
            
        def open(self):
            pass
            
        def close(self, reason):
            pass
            
        def log(self, request, spider):
            pass
            
class RedisDupeFilter(BaseDupeFilter):
    
    def __init__(self, path=None):
        self.redis_cli = StrictRedis(host='localhost', port=6379, db=0)
    
    @classmethod
    def from_settings(cls, settings):
        return cls(job_dir(settings))
     
    def request_seen(self, request):
        fp = request_fingerprint(request)
        domain = request.url.split('/')[2]
        suffix = 'category'
        if request.meta.has_key('skip'):
            suffix = 'content'
        key = '%s_%s' % (domain, suffix)
        timestamp = self.redis_cli.zscore(key, fp)
        if timestamp:
            #log.msg('skip %s' % request.url, level=log.INFO)
            return True
        self.redis_cli.zadd(key, time(), fp)
        return False

