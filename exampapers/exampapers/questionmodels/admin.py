# Create your views here.
from django.contrib import admin
from django.db import models

from widgets import HtmlWidget

from models import QuestionModel



class QuestionAdmin(admin.ModelAdmin):
    formfield_overrides = { models.TextField: {'widget':HtmlWidget}, models.CharField: {'widget':HtmlWidget}}
    list_display = ('id','paper_name', 'region', 'subject', 'grade','question_type','year','paper_type','question_answer')
       
admin.site.register(QuestionModel, QuestionAdmin)
