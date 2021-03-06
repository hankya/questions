from scrapy.http import Request, FormRequest, HtmlResponse, Response
from scrapy.contrib.downloadermiddleware.cookies import CookiesMiddleware
from scrapy.xlib.pydispatch import dispatcher
from scrapy.utils.project import data_path
from scrapy.utils.request import request_fingerprint
from scrapy.exceptions import IgnoreRequest
from scrapy import signals
from scrapy import log

from datetime import datetime

import gtk
import webkit
import jswebkit
import time


class WebkitDownloader(object):

    def process_request(self, request, spider):
        if  not request.meta.has_key('no_webkit') and type(request) is not FormRequest:
            webview = webkit.WebView()
            #set browser settings
            settings = webkit.WebSettings()
            settings.set_property('user-agent','Mozilla/5.0 (X11; U; Linux x86_64; zh-CN; rv:1.9.2.10) Gecko/20100922 Ubuntu/10.10 (maverick) Firefox/3.6.10')
            webview.set_settings(settings)     
            webview.connect('load-finished', lambda v,f: gtk.main_quit())
            webview.load_uri(request.url)
            gtk.main()        
            js = jswebkit.JSContext(webview.get_main_frame().get_global_context())
            renderedBody = str(js.EvaluateScript('document.documentElement.innerHTML'))
            return HtmlResponse(request.url, body=renderedBody)  
            
import random          
class RotateUserAgentMiddleware(object):
    '''rotate user agent'''
    uas = ['Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.8 (KHTML, like Gecko) Beamrise/17.2.0.9 Chrome/17.0.939.0 Safari/535.8',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.60 Safari/537.17',
    'Mozilla/5.0 (Windows NT 6.1; rv:9.0) Gecko/20100101 Firefox/9.0',
    'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1)',
    'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; .NET CLR 1.1.4322; .NET CLR 2.0.50727; .NET CLR 3.0.04506.30)',
    'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0)',
    'Opera/9.10 (Windows NT 5.1; U; en)',
    'Opera/9.60 (Windows NT 5.1; U; en) Presto/2.1.1',
    'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; TencentTraveler 4.0)',
    'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/531.0 (KHTML, like Gecko) Chrome/3.0.183.1 Safari/531.0',
    'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:2.0a1pre) Gecko/2008031002 Minefield/4.0a1pre',
    'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; Maxthon)',
    'BaiduSpider',
    'GoogleBot',
    'BingBit'
    ]
    
    def process_request(self, request, spider):
        i = random.randint(0, len(self.uas) - 1)
        request.headers.setdefault('User-Agent', self.uas[i])
        
                 
class HtmlFileMiddleware(object):
    '''download response as html file'''
    def process_response(self, request, response, spider):
        pass
                   
from lxml import html
import urlparse
from scrapy.utils.response import get_base_url

def body_as_unicode(self):
    return self.body.decode('utf8')
    
import re
_file_pattern = re.compile('http://[^/]+/.*\w+\.\w+')

from scrapy.selector import HtmlXPathSelector
invalid_response_urls = ['http://www.jyeoo.com/error.htm', 'http://www.jyeoo.com/404.htm']
def response_is_invalid(response):
    for url in invalid_response_urls:
        if response.url.find(url) > -1:
            return True
    return False
    
class FilterMiddleware(object):
      
    def process_response(self, request, response, spider):
        if not spider.is_valid_response(response):
            retries = request.meta.get('retry_times2', 0) + 1
            if retries < 10:
                retryreq = request.copy()
                retryreq.meta['retry_times2'] = retries  
                retryreq.dont_filter = True
                log.msg('retry %s time(s) %s' % (retries, request.url), level=log.ERROR)  
                return retryreq
            log.msg('give up %s' % request.url, level=log.ERROR)    
            raise IgnoreRequest
            
        #log.msg('valid response passed', level=log.ERROR)
        return response
            

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
       

class RelativeToAbsMiddleware(object):
    '''convert relative url to absolute url'''
    #abs_url_pattern = re.compile('http://[^/]+/.*')
    
    def process_response(self, request, response, spider):
        #log.msg('%s is type %s' % (response.url, type(response)), level=log.DEBUG)
        if type(response) is Response and not _file_pattern.match(response.url):
            response = HtmlResponse(response.url, body=response.body)
            
        if hasattr(response, 'body_as_unicode'):
            hdoc = html.fromstring(response.body_as_unicode())
            links = hdoc.xpath('//a')
            for link in links:
                href = link.get('href')
                link.set('href', urlparse.urljoin(get_base_url(response), href) )    
            return response.replace(body=html.tostring(hdoc, encoding='unicode'))            
        return response
                
class FirefoxCookiesMiddleware(CookiesMiddleware):
    def __init__(self, debug=False):
        
        super(FirefoxCookiesMiddleware, self).__init__(debug)
        dispatcher.connect(self.spider_opened, signals.spider_opened)
        
    def spider_opened(self, spider):
        jar = self.jars[None]
        jar.jar._cookies =  sqlite2cookie()._cookies
        
def sqlite2cookie(filename='/home/user/.mozilla/firefox/q0kuegus.default/cookies.sqlite'):
    from cStringIO import StringIO
    from pysqlite2 import dbapi2 as sqlite
    import cookielib
    #programtically get the cookie filepath
    filename = _get_firefox_cookie_path()
    
    with sqlite.connect(filename) as con:
        cur = con.cursor()
        cur.execute("select host, path, isSecure, expiry, name, value from moz_cookies")
        ftstr = ["FALSE","TRUE"]    
        s = StringIO()
        s.write("""\
# Netscape HTTP Cookie File
# http://www.netscape.com/newsref/std/cookie_spec.html
# This is a generated file!  Do not edit.
""")
        for item in cur.fetchall():
            s.write("%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % (
                item[0], ftstr[item[0].startswith('.')], item[1],
                                  ftstr[item[2]], item[3], item[4], item[5]))
                
        s.seek(0)
        cookie_jar = cookielib.MozillaCookieJar()
        cookie_jar._really_load(s, '', True, True)
        return cookie_jar

import os
import ConfigParser        
def _get_firefox_cookie_path():
    homedir = os.path.expanduser('~')
    firefoxdir = os.path.join(homedir, '.mozilla/firefox')
    profiles_ini = os.path.join(firefoxdir, 'profiles.ini')
    if not os.path.exists(profiles_ini):
        return None

    profiles_ini_reader = ConfigParser.ConfigParser()
    profiles_ini_reader.readfp(open(profiles_ini))
    profile_name = profiles_ini_reader.get('Profile0', 'Path', True)
    
    profile_path = os.path.join(firefoxdir, profile_name)
    if not os.path.exists(profile_path):
        return None
    else:
        if os.path.join(profile_path, 'cookies.sqlite'):
            return os.path.join(profile_path, 'cookies.sqlite')
        elif os.path.join(profile_path, 'cookies.txt'):
            return os.path.join(profile_path, 'cookies.txt')
