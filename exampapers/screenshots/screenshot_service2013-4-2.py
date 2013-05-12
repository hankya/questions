import webkit
import jswebkit
import gtk

from scrapy import log
from redis import StrictRedis

import os
import cgi

class ScreenshotService(object):
    
    def __init__(self, spider_name):
        self.redis_cli = StrictRedis(host='localhost', port=6379, db=0)
        self.spider_name = spider_name
        self.container_path = 'containers/%s/%s.html' % (self.spider_name, self.spider_name)
        
        self.window = Window()
        self.window.set_spider_name(self.spider_name)
        self.window.show()
    
    def start(self):
        while True:
            req = self.redis_cli.brpop('%s_screenshot_requests' % self.spider_name, 0)
            self.process_request(req)
          
    _slots= ['question','answer','analysis']
            
    def process_request(self, req):              
        data = eval(req[1])
        self.window.set_url(data[0]) 
        for i in range(1,4):
            self.window.set_target(self._slots[i-1])
            self.window.set_html(data[i])
            self.window.output.load_uri('file://%s' % os.path.abspath(self.container_path))
            gtk.main()            
                      
class Window(gtk.Window):

    def __init__(self):
        gtk.Window.__init__(self)
        self.set_default_size(1024, 768)
        self.scroll = gtk.ScrolledWindow()
        self.output = webkit.WebView()
        self.scroll.add(self.output)
        self.add(self.scroll)        
        self.scroll.show_all()
        self.output.connect('load-finished', self.press_key_s)
        self.connect("key-press-event", self.on_key_press)          
        self.is_fullscreen = False                   
     
    def press_key_s(self,v, f):
        script_result = self.execute_script(self.html)
        event = gtk.gdk.Event(gtk.gdk.KEY_PRESS)
        event.keyval = gtk.keysyms.s
        event.time = 0
        self.emit("key-press-event", event)
        return True
           
    def execute_script(self, html):
        js = jswebkit.JSContext(self.output.get_main_frame().get_global_context())
        #insert html to div container
        script = 'decoder=document.getElementById("decoder");decoder.innerHTML="%s";document.getElementById("screenshot_container").innerHTML=decoder.innerText;' % cgi.escape(html, quote=True)
        try:
            temp = js.EvaluateScript(script)
            temp2 = js.EvaluateScript('hiddenAnswers()')
            self.area = js.EvaluateScript('document.getElementById("screenshot_container").getBoundingClientRect();')
        except AttributeError:
            print 'bad script is %s' % script
            
        return True 
        
    def on_key_press(self, widget, event):
        if event.keyval == gtk.keysyms.z:
            #print 'process %s, %s' % (self.html,self.target)
            self.take_screenshot(self.target)
            gtk.main_quit()
            return True
        return False                
              
    def _get_view_image(self):
        root = self.output.get_parent_window()
        pixbuf = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, False, 8, int(self.area.width), int(self.area.height))
        pixbuf.get_from_drawable(root, root.get_colormap(), int(self.area.left), int(self.area.top), 0, 0, int(self.area.width), int(self.area.height))
        return pixbuf
    
    def take_screenshot(self, target):
        '''taking screenshot and save the picture'''
        path = generate_path(self.url, self.spider_name)
        if not os.path.exists(path):
            os.makedirs(path)
        
        pixbuf = self._get_view_image()
        pixbuf.save('%s/%s' % (path, target), 'png',{})
    
    def set_area(self, area):
        '''set which area should be captured on the window'''
        self.area = area
    def set_url(self, url):
        '''set the original url for the question'''
        self.url = url
    def set_target(self, target):
        '''set the name of the picture'''
        self.target = target
    def set_html(self, html):
        self.html= html
        
    def set_spider_name(self, spider_name):
        self.spider_name = spider_name

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

