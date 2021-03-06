from scrapy.spider import BaseSpider
from redis import StrictRedis
from PIL import Image
import hashlib
from cStringIO import StringIO
import os

class ImageSpider (BaseSpider):

    name = 'image'
    redis_cli = StrictRedis(host='localhost', port=6379, db=0)
    
    def start_requests(self):
        for url in self.redis_cli.smembers('images'):
            req = self.make_requests_from_url(url)
            filename = self.get_path_from_url(response.url)
            folder = os.path.join('screenshots/images', filename[:2])
            if not os.path.exists(folder):
                yield req
       
    def parse(self, response):
        filename = self.get_path_from_url(response.url)
        folder = os.path.join('screenshots/images', filename[:2])
        if not os.path.exists(folder):
            os.makedirs(folder)
        filepath = os.path.join(folder, filename)
        if not os.path.exists(filepath): 
            with open(filepath, 'wb') as f:
                f.write(response.body)
                f.flush()
        pass

    def get_path_from_url(self, url):
        tokens = url.split('/')
        return '%s.%s' % (hashlib.sha1(url).hexdigest(), tokens[-1].split('.')[-1])
