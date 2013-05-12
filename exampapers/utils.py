import hashlib
from scrapy import log

def get_path_from_url(url):
    tokens = url.split('/')
    return '%s.%s' % (hashlib.sha1(url).hexdigest(), tokens[-1].split('.')[-1])
        
from lxml import html
from lxml.etree import XMLSyntaxError

def rewrite_imgsrc(value, url):
    return [_rewrite_imgsrc(v, url) for v in value] if hasattr(value, '__iter__') else _rewrite_imgsrc(value, url)
    
def rewrite_imgsrc_abs(value, url):
    return [_rewrite_imgsrc2(v, url) for v in value] if hasattr(value, '__iter__') else _rewrite_imgsrc2(value, url)    
    
def _rewrite_imgsrc(value, url):
    hdoc = html.fromstring(value)
    imgs = hdoc.xpath('//img')
    for img in imgs:
        img_link = img.get('src')
        base_url = '/'.join(url.split('/')[:3])
        abs_link = urlparse.urljoin(base_url, img_link)
        filename = get_path_from_url(abs_link)
        img.set('src', '/'.join(['/mnt/images', filename[:2], filename]))
        img.set('alt', '')
    return html.tostring(hdoc, encoding='unicode')
    
def _rewrite_imgsrc2(value, url):
    try:
        hdoc = html.fromstring(value)
        imgs = hdoc.xpath('//img')
        for img in imgs:
            img_link = img.get('src').strip()
            base_url = '/'.join(url.split('/')[:3])
            abs_link = urlparse.urljoin(base_url, img_link)
            img.set('src', abs_link)
            img.set('alt', '')
        return html.tostring(hdoc, encoding='unicode')
    except XMLSyntaxError:
        log.msg('rewrite img src failed, see %s' % value, level=log.ERROR)
        return u''
               
import uuid
def get_uuid():
    return uuid.uuid4().hex
    
from redis import StrictRedis    
import urlparse    
def enqueue_imgs(name, base_url, img_srcs):
    redis_cli = StrictRedis(host='localhost', port=6379, db=0)
    for url in set(img_srcs):
        redis_cli.sadd('%s_images' % name, urlparse.urljoin(base_url, url))
    
