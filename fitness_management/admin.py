from django.contrib import admin
from .models import (
    AcademicYear, Region, Department, Institute, Student, 
    Test, StudentTest, News, Event, Video, TrainingUnit, ExternalLink
)

@admin.register(AcademicYear)
class AcademicYearAdmin(admin.ModelAdmin):
    list_display = ['name', 'start_date', 'end_date', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name']

@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ['name', 'code']
    search_fields = ['name', 'code']

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'region', 'code']
    list_filter = ['region']
    search_fields = ['name', 'code']

@admin.register(Institute)
class InstituteAdmin(admin.ModelAdmin):
    list_display = ['name', 'department', 'code']
    list_filter = ['department__region', 'department']
    search_fields = ['name', 'code']

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['name', 'national_id', 'gender', 'education_level', 'grade', 'institute', 'academic_year']
    list_filter = ['gender', 'education_level', 'academic_year', 'institute__department__region']
    search_fields = ['name', 'national_id']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    list_display = ['name', 'education_level', 'gender', 'max_score']
    list_filter = ['education_level', 'gender']
    search_fields = ['name']

@admin.register(StudentTest)
class StudentTestAdmin(admin.ModelAdmin):
    list_display = ['student', 'test', 'score', 'test_date']
    list_filter = ['test', 'test_date', 'student__education_level']
    search_fields = ['student__name', 'test__name']

@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ['title', 'created_at', 'is_published']
    list_filter = ['is_published', 'created_at']
    search_fields = ['title', 'content']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'start_date', 'end_date', 'location', 'is_active']
    list_filter = ['is_active', 'start_date']
    search_fields = ['title', 'description', 'location']

@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'created_at']
    list_filter = ['category', 'created_at']
    search_fields = ['title', 'description']

@admin.register(TrainingUnit)
class TrainingUnitAdmin(admin.ModelAdmin):
    list_display = ['title', 'education_level', 'created_at']
    list_filter = ['education_level', 'created_at']
    search_fields = ['title', 'content']

@admin.register(ExternalLink)
class ExternalLinkAdmin(admin.ModelAdmin):
    list_display = ['title', 'url', 'created_at']
    search_fields = ['title', 'description'] 