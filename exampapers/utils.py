import hashlib

def get_path_from_url(url):
    tokens = url.split('/')
    return '%s.%s' % (hashlib.sha1(url).hexdigest(), tokens[-1].split('.')[-1])
        
from lxml import html

def rewrite_imgsrc(value, url):
    return [_rewrite_imgsrc(v, url) for v in value] if hasattr(value, '__iter__') else _rewrite_imgsrc(value, url)    
    
def _rewrite_imgsrc(value, url):
    hdoc = html.fromstring(value)
    imgs = hdoc.xpath('//img')
    for img in imgs:
        img_link = img.get('src')
        base_url = '/'.join(url.split('/')[:3])
        abs_link = urlparse.urljoin(base_url, img_link)
        filename = get_path_from_url(abs_link)
        img.set('src', '/'.join(['/mnt/images', filename[:2], filename]))
    return html.tostring(hdoc, encoding='unicode')
        
import uuid
def get_uuid():
    return uuid.uuid4().hex
    
import urlparse    
def urls_from_imgs(img_srcs):
    return [urlparse.urljoin(base_url, url) for url in set(img_srcsdddd)]
    
