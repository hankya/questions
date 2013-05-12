# Create your views here.
from django.contrib import admin
from models import QuestionModel

class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question_number', 'paper_name')
    list_display_link = ('question_number',)

def main():
    admin.site.register(QuestionModel, QuestionAdmin)    
    
if __name__ == '__main__':
    main()
