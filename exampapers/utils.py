def get_image_name_from_url(self, url):
        tokens = url.split('/')
        return '%s.%s' % (hashlib.sha1(url).hexdigest(), tokens[-1].split('.')[-1])
        
