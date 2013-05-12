import re
class CleanTags(object):

    def __init__(self, pa='<[^>]*>'):
        self.pa = pa
        
    def __call__(self, values):
        processed_values = []
        for value in values:
            processed_values.append(re.sub(self.pa, '', value))
            
        return processed_values
        
def clean_tags(html, pa='<[^>]*>'):
    return re.sub(pa, '', html)
    
