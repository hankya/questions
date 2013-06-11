class ResponseFilterMiddleware(object):
    
    def process_response(self, request, response, spider):
        if not spider.is_valid_response(response):
            response.status = 550
        return response
