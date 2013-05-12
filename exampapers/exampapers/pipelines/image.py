#encoding:utf8
from scrapy.contrib.pipeline.images import ImagesPipeline
from scrapy.exceptions import DropItem
from scrapy.http import Request
from scrapy.utils.misc import md5sum
from scrapy import log
import os

class MyImagePipeline(ImagesPipeline):
    def image_downloaded(self, response, request, info):
        checksum = None
        for key, image, buf in self.get_images(response, request, info):
            if checksum is None:
                buf.seek(0)
                checksum = md5sum(buf)
                folder, filename = self.get_path_from_url(response.url)
                #to do, move the folder under screenshot containers.
                folder_path = os.path.join(self.store.basedir, info.spider.name, folder)
                if not os.path.exists(folder_path):
                    os.makedirs(folder_path)
                filepath = os.path.join(folder_path, filename)
                if not os.path.exists(filepath):
                    image.save(filepath)          
        return checksum
        
    def get_path_from_url(self, url):
        tokens = url.split('/')
        return ('/').join(tokens[3:-1]), tokens[-1]
