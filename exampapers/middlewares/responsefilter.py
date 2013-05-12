class ResponseFilterMiddleware(object):
    
    def __init__(self, settings):
        self.cachedir = data_path(settings['HTTPCACHE_DIR'])
    
    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)
        
    def process_response(self, request, response, spider):
        if type(response) is HtmlResponse and len(response.body) > 4000 and response.status <> 403:
            times = request.meta.get('retry_times2', 0)
            if times > 0:
                log.msg('retry %s time(s) saved %s' % (times, response.url), level=log.ERROR)
                
        retry = False
        if response.status == 403:
            retry = True   
        if type(response) is HtmlResponse:
            if len(response.body) < 4000:
                retry = True
            elif response_is_invalid(response):
                retry = True
        if retry:     
                retries = request.meta.get('retry_times2', 0) + 1
                if retries < 10:
                    key = request_fingerprint(request)
                    rpath = os.path.join(self.cachedir, spider.name, key[0:2], key)
                    metapath = os.path.join(rpath, 'pickled_meta')
                    if os.path.exists(metapath):
                        os.unlink(metapath)
                    retryreq = request.copy()
                    retryreq.meta['retry_times2'] = retries  
                    retryreq.dont_filter = True
                    log.msg('retry %s time(s) %s' % (retries, request.url), level=log.ERROR)  
                    return retryreq
                log.msg('give up %s' % request.url, level=log.ERROR)    
                raise IgnoreRequest    
            
        return response

