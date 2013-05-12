from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtWebKit import *

from scrapy import log
from redis import StrictRedis

import os
import cgi
import time

class Window(QWebView):
    def __init__(self, parent=None):
        self.app = QApplication(sys.argv)
        QWebView.__init__(self)
        self._loaded = False
        #self.loadFinished.connect(self.on_loadFinished)
        self.loadFinished.connect(self._load_Finished)
        
    def load_url(self, url):
        self.load(QUrl(url))
        
    @pyqtSlot(str)
    def on_loadFinished(self):
        #self.page().mainFrame().evaluateJavascript('script')
        path = generate_path(self.url, self.spider_name)
        if not os.path.exists(path):
            os.makedirs(path)
        self.filepath = '%s/%s' % (path, self.target_name)
        self._capture()
        
    def capture(self, url, spider_name, target_name):
        self.url = url
        self.spider_name = spider_name
        self.target_name = target_name
        self.load_url(url)
        
    def capture2(self, url, spider_name, target_name):
        self.show()
        self.load_url(url)
        self.wait_load()
        path = generate_path(url, spider_name)
        if not os.path.exists(path):
            os.makedirs(path)
        self.filepath = '%s/%s' % (path, target_name)
        frame = self.page().mainFrame()
        self.page().setViewportSize(frame.contentsSize())
        image = QImage(self.page().viewportSize(), QImage.Format_ARGB32)
        painter = QPainter(image)
        painter.begin(self)
        frame.render(painter)
        painter.end()
        image.save(self.filepath, 'png')    
         
    def on_paint_event(self, event):
        print 'now start painting'
        frame = self.page().mainFrame()
        self.page().setViewportSize(frame.contentsSize())
        image = QImage(self.page().viewportSize(), QImage.Format_ARGB32)
        painter = QPainter(image)
        painter.begin(self)
        frame.render(painter)
        painter.end()
        image.save(self.filepath, 'png')
       
    def _capture(self):
        '''sending paint event'''
        region = QRegion(0,0,64,64)
        event = QPaintEvent(region)
        self.paintEvent(event)
        print 'event sent'
        self.show()       
        
    def f(self):
        path = generate_path(self.url, self.spider_name)
        if not os.path.exists(path):
            os.makedirs(path)
        pixbuf.save('%s/%s' % (path, self.target), 'png',{})
        
        
    def wait_load(self, delay=0):
        while not self._loaded:
            self.app.processEvents()
            time.sleep(delay)
        self._loaded = False
        
    def _load_Finished(self, result):
        print 'load finished'
        self._loaded = True
        
    def load_html_by_script(self, js):
        script = 'decoder=document.getElementById("decoder");decoder.innerHTML="%s";d=document.createElement("div");d.innerHTML=decoder.innerText;document.getElementById("screenshot_container").innerHTML=d.innerText;' % cgi.escape(html, quote=True)
        temp = js.EvaluateScript(script)


from scrapy.utils.url import canonicalize_url     
import hashlib   
def url_fingerprint(url):
    fp = hashlib.sha1()
    fp.update(canonicalize_url(url))
    return fp.hexdigest()
    
def generate_path(url, name):
    '''generate path for url'''
    key = url_fingerprint(url)
    return os.path.join('store',name,key[0:2],key)
    
import sys
def main():
    serv = ScreenshotService(sys.argv[1])
    test_req = ['http://www.baidu.com', '<span>hello<checkbox>on</checkbox><label>question</label></span>', '<label style="color:yellow">answer</label>', '<button style="color:red"></button><label>analysis</label>']
    serv.start()

if __name__=='__main__':
    main()

