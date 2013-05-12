from redis import StrictRedis

class ScreenshotPipeline(object):

    redis_cli = StrictRedis(host='localhost', port=6379, db=0) 

    def process_item(self, item, spider):
        content_req = [item['question_id'], 'question_content', item['question_content_html'] ]        
        self.redis_cli.lpush('%s_screenshot_requests' % spider.name, content_req)
        answer_html = item['question_answer_html']
        if answer_html:
            answer_req = [item['question_id'], 'answer_content', item['question_answer_html'] ]
            self.redis_cli.lpush('%s_screenshot_requests' % spider.name, answer_req)
            
        return item
