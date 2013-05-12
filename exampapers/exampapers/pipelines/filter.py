from hashlib import sha1
from redis import StrictRedis

from scrapy.exceptions import DropItem

class ItemFilterPipeline(object):

    redis_cli = StrictRedis(host='localhost', port=6379, db=0) 

    def process_item(self, item, spider):
        """
            this filter will drop item that already been seen in the system, we identify a item by 
            doing a hash of its question body
        """
        
        fingerprint = sha1(item['question_content_html'].encode('utf8')).hexdigest()
        result = self.redis_cli.sadd('items', fingerprint)
        if result:
            return item
        raise DropItem

        
        
 
