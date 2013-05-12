from django.forms import widgets
from django.utils.safestring import mark_safe

class HtmlWidget(widgets.Widget):
    '''A widget to display HTML in admin fields'''
    
    input_type = None
    
    def render(self, name, value, attrs=None):
        if value is None:
            value = ''
        return mark_safe(u'%s' % value)
    

