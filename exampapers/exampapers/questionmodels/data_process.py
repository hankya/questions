def process_item(item):
    import re
    def paper_year_classifier(paper_name):
        return '-'.join(re.findall('\d{4}', paper_name))

    paper_types = {'竞赛' : u'\u7ade\u8d5b','比赛' : u'\u6bd4\u8d5b', '中考' : u'\u4e2d\u8003', '高考' : u'\u9ad8\u8003', '期中' : u'\u671f\u4e2d', '期末' : u'\u671f\u672b', '月考' : u'\u6708\u8003'}

    def paper_type_classifier(paper_name):
        for paper_type in paper_types:
            if paper_name.find(paper_types[paper_type]) > -1:
                return paper_types[paper_type]
        return u'unknown'
    def question_type_classifier(question_type):
        return u''
    def paper_source_classifier(paper_name):
        return u''
        
    #pattern to match region, \u7701 = ﻿省, \u5e02=市
    PROVINCE_PATTERN = re.compile(u'\u5e74([^\u5e74].+\u7701)')
    CITY_PATTERN = re.compile(u'\u5e74([^\u5e74].+\u5e02)')

    def paper_region_classifier(paper_name):
        m = PROVINCE_PATTERN.search(paper_name)
        if not m:
            m = CITY_PATTERN.search(paper_name)
        return m.groups()[0] if m else u'unknown'
        
    def paper_grade_classifier(paper_name):
        m = re.search(u'.\u5e74\u7ea7\uff08.\uff09', paper_name)
        return m.group() if m else paper_name[-8:-6]
        
    def paper_subject_classifier(paper_name):
        return paper_name[-10:-8]
        
    def question_type_classifier(type_str):
        for question_type in question_types:
            if type_str.find(question_types[question_type][:2]) > -1:
                return question_types[question_type]
        return u'unknown'
       
    item.source = paper_source_classifier(item.paper_name)
    item.question_type = question_type_classifier(item.question_type)
    item.year = paper_year_classifier(item.paper_name)
    item.paper_type = paper_type_classifier(item.paper_name)
    item.region = paper_region_classifier(item.paper_name)     
    item.grade = paper_grade_classifier(item.paper_name)
    item.subject = paper_subject_classifier(item.paper_name)     
    item.paper_name = item.paper_name.replace(u' - \u83c1\u4f18\u7f51', '') 
    item.save()
all = QuestionModel.objects.all()
def process_answer(answer, content_html):
    from lxml import html
    if answer.find(u'\u67e5\u770b\u672c\u9898\u89e3\u6790\u9700\u8981\u767b\u5f55') > -1:
        hdoc = html.fromstring(content_html)
        ma = hdoc.xpath('//label[@class=" s"]/text()')
        if ma:
            return unicode(ma[0][0])
        ma = hdoc.xpath('//div[@class="sanwser"]/text()')
        return unicode(ma[0]) if ma else u'unknown'  

        
