def  flatten_item(item):
    for key in item.keys():
        item[key] = flatten(item[key])   
    return item
    
def flatten(value):
    if not isinstance(value, dict) and hasattr(value, '__iter__'):
            if isinstance(value, bool):
                value = value[0]
            else:
                value = ','.join(value)               
    return value
    
class FlattenItemPipeline(object):
    def process_item(self, item, spider):
        return flatten_item(item)
    
