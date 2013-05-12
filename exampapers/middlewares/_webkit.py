from scrapy.http import Request, FormRequest, HtmlResponse, Response

import gtk
import webkit
import jswebkit
import time


class WebkitDownloader(object):

    def process_request(self, request, spider):
        if  not request.meta.has_key('no_webkit') and type(request) is not FormRequest:
            webview = webkit.WebView()
            #set browser settings
            #settings = webkit.WebSettings()
            #settings.set_property('user-agent','Mozilla/5.0 (X11; U; Linux x86_64; zh-CN; rv:1.9.2.10) Gecko/20100922 Ubuntu/10.10 (maverick) Firefox/3.6.10')
            #webview.set_settings(settings)     
            webview.connect('load-finished', lambda v,f: gtk.main_quit())
            webview.load_uri(request.url)
            gtk.main()        
            js = jswebkit.JSContext(webview.get_main_frame().get_global_context())
            renderedBody = str(js.EvaluateScript('document.documentElement.innerHTML'))
            return HtmlResponse(request.url, body=renderedBody)  
