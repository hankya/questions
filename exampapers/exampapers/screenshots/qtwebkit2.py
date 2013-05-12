import sys
import time
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtWebKit import *
from redis import StrictRedis

import os
import cgi

class Screenshot(QWebView):
    def __init__(self, spider_name):
        self.app = QApplication(sys.argv)
        QWebView.__init__(self)
        self._loaded = False
        self.redis_cli = StrictRedis(host='localhost', port=6379, db=0)
        self.loadFinished.connect(self._loadFinished)
        self.spider_name = spider_name
        self.container_path = 'file://%s' % os.path.abspath('containers/%s/%s.html' % (self.spider_name, self.spider_name))

    def _create_script(self, html):
        return 'decoder=document.getElementById("decoder");decoder.innerHTML="%s";document.getElementById("screenshot_container").innerHTML=decoder.innerText;' % cgi.escape(html, quote=True)
    
    def start(self):
        while True:
            req = self.redis_cli.brpop('%s_screenshot_requests' % self.spider_name, 0)
            self.process_request(req)
            
    def process_request(self, req):
        data = eval(req[1])
        url = data[0]   
        folder_path = generate_path(url, self.spider_name)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        for i, data in enumerate(data[1:]):
            file_path = os.path.join(folder_path, '%s.png' %str(i))
            if not os.path.exists(file_path):
                html = container.replace(self.replace_sign, data[i])
                self.capture(self.container_path, file_path, data.decode('utf8'))  
    
    def capture(self, url, output_file, html):
        self.load(QUrl(url))
        self.wait_load()
        # set to webpage size
        frame = self.page().mainFrame()
        dump = frame.evaluateJavaScript(QString(self._create_script(html)))
        dump2 = frame.evaluateJavaScript(QString('hiddenAnswers()'))
        qv = frame.evaluateJavaScript(QString('document.getElementById("screenshot_container").scrollHeight;'))
        height_info = qv.toInt()
        
        size = frame.contentsSize()
        if height_info[1]:
            size.setHeight(height_info[0])
            
        self.page().setViewportSize(size)
        # render image
        image = QImage(self.page().viewportSize(), QImage.Format_ARGB32)
        painter = QPainter(image)
        frame.render(painter)
        painter.end()
        print 'saving', output_file
        image.save(output_file)

    def wait_load(self, delay=0):
        # process app events until page loaded
        while not self._loaded:
            self.app.processEvents()
            time.sleep(delay)
        self._loaded = False

    def _loadFinished(self, result):
        self._loaded = True

#s.capture('http://sitescraper.net', 'website.png')
#s.capture('http://sitescraper.net/blog', 'blog.png')
from scrapy.utils.url import canonicalize_url     
import hashlib   
def url_fingerprint(url):
    fp = hashlib.sha1()
    fp.update(canonicalize_url(url))
    return fp.hexdigest()
    
def generate_path(url, name):
    '''generate path for url'''
    #key = url_fingerprint(url)
    return os.path.join('store2',name,url[-36:-34],url[-36:])
    
    
def main():
    serv = Screenshot(sys.argv[1])
    serv.start()

if __name__=='__main__':
    main()
