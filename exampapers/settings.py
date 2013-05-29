# Scrapy settings for exampapers project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/topics/settings.html
#

USER_AGENT = 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:19.0) Gecko/20100101 Firefox/19.0'
BOT_NAME = 'Baiduspider'
DOWNLOAD_DELAY = '0.05'
DOWNLOAD_TIMEOUT = 10
SPIDER_MODULES = ['exampapers.spiders']
NEWSPIDER_MODULE = 'exampapers.spiders'
ITEM_PIPELINES = [
#'exampapers.pipelines.image.MyImagePipeline',
#'exampapers.pipelines.normalize.UrlRewriterPipeline',
'exampapers.pipelines.flatten.FlattenItemPipeline',
'exampapers.pipelines.htmltotext.HtmlToTextPipeline',
'exampapers.pipelines.normalize.AnswerPipeline',
'exampapers.pipelines.filter.ItemFilterPipeline',
'exampapers.pipelines.djangowriter.DjangoWriterPipeline',
#'exampapers.pipelines.ScreenshotPipeline',
]

DOWNLOADER_MIDDLEWARES = {
#'exampapers.middlewares.RotateUserAgentMiddleware':401,
#'exampapers.middlewares.FirefoxCookiesMiddleware':700,
#'scrapy.contrib.downloadermiddleware.cookies.CookiesMiddleware':None,
#'scrapy.contrib.downloadermiddleware.useragent.UserAgentMiddleware':None,
#'exampapers.middlewares.FilterMiddleware':875,
#'exampapers.middlewares._webkit.WebkitDownloader':1000,
#'exampapers.middlewares.RelativeToAbsMiddleware':1100,
'exampapers.middlewares.retry.RetryMiddleware':450,
'exampapers.middlewares.httpproxy.HttpProxyMiddleware':750,
'scrapy.contrib.downloadermiddleware.httpproxy.HttpProxyMiddleware':None,
}
RETRY_ENABLED = True
RETRY_TIMES = 25
RETRY_HTTP_CODES = [400, 401, 403, 404, 408, 500, 503, 504]
RETRY_PRIORITY_ADJUST = 0

#IMAGES_STORE='screenshots/containers'

LOG_LEVEL='DEBUG'
#LOG_FILE='logs/errors'

#DUPEFILTER_CLASS = 'exampapers.dupefilter.RedisDupeFilter'

HTTPCACHE_ENABLED = True
HTTPCACHE_EXPIRATION_SECS = 0
HTTPCACHE_STORAGE = 'scrapy.contrib.downloadermiddleware.httpcache.FilesystemCacheStorage'
HTTPCACHE_DIR = '/mnt/httpcache'
HTTPCACHE_IGNORE_HTTP_CODES =[400, 401, 403, 404, 408, 500, 503, 504]

COOKIES_ENABLED = True
#COOKIES_DEBUG = True



from django.core.management import setup_environ
import web.settings
setup_environ(web.settings)
