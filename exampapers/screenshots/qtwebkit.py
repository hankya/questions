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
        self.replace_sign = 'replace_me'
        self.container_path = 'screenshots/containers/%s' % self.spider_name
        self.container = open('%s/%s.html' % (self.container_path, self.spider_name), 'rb').read().decode('utf8')

    def _create_script(self, html):
        return 'decoder=document.getElementById("decoder");decoder.innerHTML="%s";document.getElementById("screenshot_container").innerHTML=decoder.innerText;' % cgi.escape(html, quote=True)
    
    def start(self):
        while True:
            req = self.redis_cli.brpop('%s_screenshot_requests' % self.spider_name, 0)
            print req
            self.process_request(req[1])      

    def process_request(self, request):
        request = eval(request)
        question_id = request[0]
        name = request[1]
        data = request[2]
        folder_path = os.path.join('/mnt/screenshots', question_id[:2], question_id)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        if data:
            out_file = os.path.join(folder_path, '%s.png' % name)
            if not os.path.exists(out_file):
                html = self.container.replace(self.replace_sign, data)
                html_file = os.path.join(self.container_path, '%s.html' % name)
                with open(html_file, 'wb') as f:
                    f.write(html.encode('utf8'))
                    f.flush()
                self.capture('file://%s' % os.path.abspath(html_file), out_file)
                #os.unlink(html_file)

    def capture(self, html_file, output_file):
        self.load(QUrl(html_file))
        self.wait_load()
        # set to webpage size
        frame = self.page().mainFrame()
        #dump = frame.evaluateJavaScript(QString(self._create_script(html)))
        dump2 = frame.evaluateJavaScript(QString('hiddenAnswers()'))
        qv = frame.evaluateJavaScript(QString('document.getElementById("screenshot_container").scrollHeight;'))
        height_info = qv.toInt() 
        size = frame.contentsSize()
        #ensure width is 700
        size.setWidth(700)
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
        
    def generate_path(self, question_id):
        '''generate path for url'''
        #key = url_fingerprint(url)
        return os.path.join('/mnt/screenshots', question_id[:2], question_id)
    
#s.capture('http://sitescraper.net', 'website.png')
#s.capture('http://sitescraper.net/blog', 'blog.png')
from scrapy.utils.url import canonicalize_url     
import hashlib   
def url_fingerprint(url):
    fp = hashlib.sha1()
    fp.update(canonicalize_url(url))
    return fp.hexdigest()
    
def generate_path(question_id, name):
    '''generate path for url, put all screenshots onto /mnt'''
    #key = url_fingerprint(url)
    return os.path.join('/mnt/screenshots', question_id[:2], question_id)
    
    
def main():
    serv = Screenshot(sys.argv[1])
    serv.start()

if __name__=='__main__':
    main()
