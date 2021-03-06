# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/topics/items.html

from scrapy.item import Item, Field

class QuestionItem(Item):
'''your comment here'''
    url = Field()
    question_number = Field()
    content = Field()
    options = Field()
    answer = Field()
    comment = Field()
    year = Field()
    paper_name = Field()
    exam_type = Field()
    question_purpose = Field()
    question_type = Field()
    question_analysis = Field()
    pass
