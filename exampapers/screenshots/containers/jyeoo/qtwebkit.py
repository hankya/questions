import sys
import time
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtWebKit import *

import os
import cgi

class Screenshot(QWebView):
    import time
    from PyQt4.QtCore import *
    from PyQt4.QtGui import *
    from PyQt4.QtWebKit import *
    import os
    
    def __init__(self, spider_name):
        self.app = QApplication(sys.argv)
        QWebView.__init__(self)
        self._loaded = False
        #self.redis_cli = StrictRedis(host='localhost', port=6379, db=0)
        self.loadFinished.connect(self._loadFinished)
        self.spider_name = spider_name
        self.replace_sign = 'replace_me'
        self.container_path = 'screenshots/containers/%s' % self.spider_name
        self.container = open('%s/%s.html' % (self.container_path, self.spider_name), 'rb').read().decode('utf8')

    def _create_script(self, html):
        return 'decoder=document.getElementById("decoder");decoder.innerHTML="%s";document.getElementById("screenshot_container").innerHTML=decoder.innerText;' % cgi.escape(html, quote=True)
    
    def start(self):
        while True:
            #req = self.redis_cli.brpop('%s_screenshot_requests' % self.spider_name, 0)
            self.process_item(req)
            
    def process_item(self, item):
        self.item = item
        folder_path = self.generate_path(item.question_id, self.spider_name)
        print 'process item %s' % item.id
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            self.process_html('question_content', folder_path)
            self.process_html('question_answer', folder_path)
            self.process_html('question_analysis', folder_path)
                
    def process_html(self, name, folder_path):
        data = getattr(self.item, '%s_html' % name)
        if data and data.find(u'\u67e5\u770b\u672c\u9898\u89e3\u6790\u9700\u8981') == -1:
            out_file = os.path.join(folder_path, '%s.png' % name)
            if not os.path.exists(out_file):
                html = self.container.replace(self.replace_sign, data)
                html_file = os.path.join(self.container_path, '%s.html' % name)
                with open(html_file, 'wb') as f:
                    f.write(html.encode('utf8'))
                    f.flush()
                self.capture('file://%s' % os.path.abspath(html_file), out_file)
                os.unlink(html_file)

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
        
    def generate_path(self, question_id, name):
        '''generate path for url'''
        #key = url_fingerprint(url)
        return os.path.join('screenshots', 'store',name,question_id[:2],question_id)
    
#s.capture('http://sitescraper.net', 'website.png')
#s.capture('http://sitescraper.net/blog', 'blog.png')
from scrapy.utils.url import canonicalize_url     
import hashlib   
def url_fingerprint(url):
    fp = hashlib.sha1()
    fp.update(canonicalize_url(url))
    return fp.hexdigest()
    
def generate_path(question_id, name):
    '''generate path for url'''
    #key = url_fingerprint(url)
    return os.path.join('store',name,question_id[:2],question_id)
    
    
def main():
    serv = Screenshot(sys.argv[1])
    serv.start()

if __name__=='__main__':
    main()
