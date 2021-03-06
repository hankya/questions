from scrapy.utils.httpobj import urlparse_cached
from scrapy.exceptions import NotConfigured
from scrapy import log

from twisted.internet.error import TimeoutError as ServerTimeoutError, DNSLookupError, \
                                   ConnectionRefusedError, ConnectionDone, ConnectError, \
                                   ConnectionLost, TCPTimedOutError
from twisted.internet.defer import TimeoutError as UserTimeoutError
from redis import StrictRedis


class HttpProxyMiddleware (object):
    """
        this middleware will select a proxy from the proxy pool
    """
    
    redis_cli = StrictRedis(host='localhost', port=6379, db=0)
    rings = {}

    def __init__(self):
        self.key = 'proxies'
        self.EXCEPTIONS_TO_RETRY = (ServerTimeoutError, UserTimeoutError, DNSLookupError,
                           ConnectionRefusedError, ConnectionDone, ConnectError,
                           ConnectionLost, TCPTimedOutError,
                           IOError)
        
    def process_request(self, request, spider):
        spider_name = spider.name
        if spider_name not in self.rings.keys():
            key_name = 'proxies_%s' % spider_name
            self.redis_cli.sunionstore(key_name, 'proxies')
            self.rings[spider_name] = Ring(self.redis_cli.smembers(key_name))
            
        ring = self.rings[spider_name]
        proxy = ring.next()
        log.msg('using proxy %s' % proxy, level=log.DEBUG)
        request.meta['proxy'] = proxy
            
    def process_response(self, request, response, spider):
        if hasattr(spider, 'ban_codes'):
            if response.status in spider.ban_codes:
                self.redis_cli.srem('proxies_%s' % spider.name, request.meta['proxy'])
                self.rings[spider.name].remove(request.meta['proxy'])
        return response
        
    def process_exception(self, request, exception, spider):
        if isinstance(exception, self.EXCEPTIONS_TO_RETRY):
            self.redis_cli.srem('proxies_%s' % spider.name, request.meta['proxy'])
            self.rings[spider.name].remove(request.meta['proxy'])
            log.msg('removed proxy %s' % request.meta['proxy'], level = log.DEBUG)
        
class Ring(object):

    def __init__(self, _list):
        self.nodes = [Node(data) for data in _list]
        length = len(self.nodes)
        for i in range(length):
            if i < length - 1 :
                self.nodes[i].link(self.nodes[i+1])
            else:
                self.nodes[i].link(self.nodes[0])
                
        self.current = self.nodes[-1]    
    
    def remove(self, proxy):
        nodes = filter(lambda n: n.data == proxy, self.nodes)
        length = len(self.nodes)
        for node in nodes:
            index = self.nodes.index(node) 
            self.nodes[index - 1].link(self.nodes[-(length - index) + 1])
            self.nodes.remove(node)
      
    def next(self):
        self.current = self.current.next
        return self.current.data
        
class Node(object):

    def __init__(self, data):
        self.data = data
    
    def link(self, node):
        self.next = node
