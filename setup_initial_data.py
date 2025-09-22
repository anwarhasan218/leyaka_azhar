#!/usr/bin/env python
"""
سكريبت إعداد البيانات الأولية للمشروع القومي للياقة البدنية
"""

import os
import django

# إعداد Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fitness_project.settings')
django.setup()

from django.contrib.auth.models import User
from accounts.models import UserProfile
from fitness_management.models import (
    AcademicYear, Region, Department, Institute, 
    News, Event, Video, TrainingUnit, ExternalLink
)

def create_initial_data():
    """إنشاء البيانات الأولية للمشروع"""
    
    print("بدء إنشاء البيانات الأولية...")
    
    # إنشاء العام الدراسي الحالي
    current_year, created = AcademicYear.objects.get_or_create(
        name="2024-2025",
        defaults={
            'is_active': True,
            'start_date': '2024-09-01',
            'end_date': '2025-06-30'
        }
    )
    if created:
        print(f"تم إنشاء العام الدراسي: {current_year}")
    
    # إنشاء المناطق
    regions_data = [
        {'name': 'القاهرة', 'code': 'CAI'},
        {'name': 'الجيزة', 'code': 'GIZ'},
        {'name': 'الإسكندرية', 'code': 'ALX'},
        {'name': 'أسيوط', 'code': 'ASY'},
        {'name': 'سوهاج', 'code': 'SUH'},
    ]
    
    for region_data in regions_data:
        region, created = Region.objects.get_or_create(
            name=region_data['name'],
            defaults={'code': region_data['code']}
        )
        if created:
            print(f"تم إنشاء المنطقة: {region}")
    
    # إنشاء الإدارات لكل منطقة
    departments_data = [
        {'name': 'إدارة شرق', 'code': 'EAST'},
        {'name': 'إدارة غرب', 'code': 'WEST'},
        {'name': 'إدارة شمال', 'code': 'NORTH'},
        {'name': 'إدارة جنوب', 'code': 'SOUTH'},
    ]
    
    for region in Region.objects.all():
        for dept_data in departments_data:
            department, created = Department.objects.get_or_create(
                name=f"{dept_data['name']} {region.name}",
                region=region,
                defaults={'code': f"{dept_data['code']}_{region.code}"}
            )
            if created:
                print(f"تم إنشاء الإدارة: {department}")
    
    # إنشاء المعاهد لكل إدارة
    institutes_data = [
        {'name': 'معهد الأزهر الابتدائي', 'type': 'primary'},
        {'name': 'معهد الأزهر الإعدادي', 'type': 'middle'},
        {'name': 'معهد الأزهر الثانوي', 'type': 'secondary'},
    ]
    
    for department in Department.objects.all():
        for inst_data in institutes_data:
            institute, created = Institute.objects.get_or_create(
                name=f"{inst_data['name']} {department.name}",
                department=department,
                defaults={'code': f"{inst_data['type']}_{department.code}"}
            )
            if created:
                print(f"تم إنشاء المعهد: {institute}")
    
    # إنشاء أخبار أولية
    news_data = [
        {
            'title': 'انطلاق المشروع القومي للياقة البدنية',
            'content': 'تم إطلاق المشروع القومي للياقة البدنية للطلاب على مستوى الأزهر الشريف بنجاح.',
            'is_published': True
        },
        {
            'title': 'بدء التسجيل للطلاب',
            'content': 'يمكن للطلاب الآن التسجيل في المشروع من خلال معاهدهم.',
            'is_published': True
        },
    ]
    
    for news_item in news_data:
        news, created = News.objects.get_or_create(
            title=news_item['title'],
            defaults=news_item
        )
        if created:
            print(f"تم إنشاء الخبر: {news}")
    
    # إنشاء فعاليات أولية
    events_data = [
        {
            'title': 'اللقاء القمم لأبطال اللياقة البدنية',
            'description': 'لقاء يجمع أبطال اللياقة البدنية من جميع المناطق.',
            'start_date': '2025-03-15 09:00:00',
            'end_date': '2025-03-15 17:00:00',
            'location': 'القاهرة',
            'is_active': True
        },
        {
            'title': 'مسابقة المنطقة',
            'description': 'مسابقة لاختيار أفضل الطلاب على مستوى المنطقة.',
            'start_date': '2025-02-20 10:00:00',
            'end_date': '2025-02-20 16:00:00',
            'location': 'الجيزة',
            'is_active': True
        },
    ]
    
    for event_item in events_data:
        event, created = Event.objects.get_or_create(
            title=event_item['title'],
            defaults=event_item
        )
        if created:
            print(f"تم إنشاء الفعالية: {event}")
    
    # إنشاء وحدات تدريبية أولية
    training_data = [
        {
            'title': 'اللياقة البدنية الأساسية',
            'content': 'تمارين أساسية لتحسين اللياقة البدنية للطلاب.',
            'education_level': 'primary'
        },
        {
            'title': 'تمارين القوة',
            'content': 'تمارين لبناء قوة العضلات بشكل آمن.',
            'education_level': 'middle'
        },
    ]
    
    for training_item in training_data:
        training, created = TrainingUnit.objects.get_or_create(
            title=training_item['title'],
            defaults=training_item
        )
        if created:
            print(f"تم إنشاء الوحدة التدريبية: {training}")
    
    # إنشاء روابط خارجية أولية
    links_data = [
        {
            'title': 'موقع الأزهر الشريف',
            'url': 'https://www.azhar.eg',
            'description': 'الموقع الرسمي للأزهر الشريف'
        },
        {
            'title': 'وزارة التربية والتعليم',
            'url': 'https://moe.gov.eg',
            'description': 'الموقع الرسمي لوزارة التربية والتعليم'
        },
    ]
    
    for link_item in links_data:
        link, created = ExternalLink.objects.get_or_create(
            title=link_item['title'],
            defaults=link_item
        )
        if created:
            print(f"تم إنشاء الرابط: {link}")
    
    print("تم إنشاء البيانات الأولية بنجاح!")

if __name__ == '__main__':
    create_initial_data()
