from redis import StrictRedis
import shutil
import os

last = 119559

redis_cli = StrictRedis(host='localhost', port=6379, db=0)
def clear_cache_content():
    start = 0
    for i in range(1, 121):
        items = redis_cli.zrange('crawled_set_content', start * 1000, i * 1000)
        print 'processing %s to %s' % (start*1000, i*1000)
        start = i
        #now process items
        for item in iter(items):
            #delete item
            try:
                shutil.rmtree(os.path.join('/home/runyang/exampapers/.scrapy/httpcache/jyeoo', item[0:2], item))
                print 'folder removed'
            except os.error, error:
                
    
