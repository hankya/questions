from django.db import models

from scrapy.contrib.djangoitem import DjangoItem
# Create your models here.


class QuestionModel(models.Model):
    
    question_id = models.CharField(max_length=50, blank=True)
    
    #image_urls = models.TextField()
    
    url = models.URLField()
    question_number = models.IntegerField(blank=True)
    
    question_content = models.TextField()
    question_content_html = models.TextField()
    
    question_answer = models.TextField()
    question_answer_html = models.TextField()
    
    question_analysis = models.TextField()
    question_analysis_html = models.TextField()
    
    #question_comment = models.TextField()
    #question_comment_html = models.TextField()
    
    knowledge_points = models.CharField(max_length=500, blank=True)
    
    #question_purpose = models.CharField(max_length=100, blank=True)
    difficult_level = models.CharField(max_length=50, blank=True)
    question_type = models.CharField(max_length=50, blank=True)
    
    #paper statics
    #from page name
    source = models.CharField(max_length=100, blank=True)    
    year = models.CharField(max_length=50, blank=True)
    region = models.CharField(max_length=100, blank=True)
    grade = models.CharField(max_length=100, blank=True)
    subject = models.CharField(max_length=100, blank=True)
    
    paper_url = models.URLField()
    paper_name = models.CharField(max_length=100, blank=True)
    paper_type = models.CharField(max_length=50, blank=True)
    
    #datetimes 
    created = models.DateTimeField(auto_now=True)
    modifed = models.DateTimeField(auto_now=True)
    #css_html = models.TextField()
    
    def __unicode__(self):
        return str(self.id)
        
class QuestionItem(DjangoItem):
    django_model = QuestionModel
