from django.urls import path
from . import views

app_name = 'fitness_management'

urlpatterns = [
    # الصفحات الرئيسية
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('about/', views.about_project, name='about_project'),
    path('contact/', views.contact, name='contact'),
    
    # إدارة الطلاب
    path('students/', views.student_list, name='student_list'),
    path('students/add/', views.add_student, name='add_student'),
    path('students/<int:student_id>/', views.student_detail, name='student_detail'),
    path('students/<int:student_id>/edit/', views.edit_student, name='edit_student'),
    path('students/<int:student_id>/delete/', views.delete_student, name='delete_student'),
    path('students/<int:student_id>/add-test/', views.add_student_test, name='add_student_test'),
    
    # إدارة المناطق
    path('regions/', views.region_list, name='region_list'),
    path('regions/add/', views.add_region, name='add_region'),
    path('regions/<int:region_id>/edit/', views.edit_region, name='edit_region'),
    path('regions/<int:region_id>/delete/', views.delete_region, name='delete_region'),
    
    # إدارة الإدارات
    path('departments/', views.department_list, name='department_list'),
    path('departments/add/', views.add_department, name='add_department'),
    path('departments/<int:department_id>/edit/', views.edit_department, name='edit_department'),
    path('departments/<int:department_id>/delete/', views.delete_department, name='delete_department'),
    
    # إدارة المعاهد
path('institutes/', views.institute_list, name='institute_list'),
path('institutes/add/', views.add_institute, name='add_institute'),
path('institutes/<int:institute_id>/edit/', views.edit_institute, name='edit_institute'),
path('institutes/<int:institute_id>/delete/', views.delete_institute, name='delete_institute'),

# API للفلترة الديناميكية
path('api/departments/<int:region_id>/', views.get_departments_by_region, name='get_departments_by_region'),
path('api/institutes/<int:department_id>/', views.get_institutes_by_department, name='get_institutes_by_department'),
    
    # التقارير والإحصائيات
    path('reports/', views.reports, name='reports'),
    
    # الأخبار
    path('news/', views.news_list, name='news_list'),
    path('news/add/', views.add_news, name='add_news'),
    path('news/<int:news_id>/', views.news_detail, name='news_detail'),
    path('news/<int:news_id>/edit/', views.edit_news, name='edit_news'),
    path('news/<int:news_id>/delete/', views.delete_news, name='delete_news'),
    
    # الفعاليات
    path('events/', views.events_list, name='events_list'),
    path('events/add/', views.add_event, name='add_event'),
    path('events/<int:event_id>/', views.event_detail, name='event_detail'),
    path('events/<int:event_id>/edit/', views.edit_event, name='edit_event'),
    path('events/<int:event_id>/delete/', views.delete_event, name='delete_event'),
    
    # الفيديوهات
    path('videos/', views.videos_list, name='videos_list'),
    path('videos/add/', views.add_video, name='add_video'),
    path('videos/<int:video_id>/edit/', views.edit_video, name='edit_video'),
    path('videos/<int:video_id>/delete/', views.delete_video, name='delete_video'),
    
    # الوحدات التدريبية
    path('training/', views.training_units_list, name='training_units_list'),
    path('training/add/', views.add_training_unit, name='add_training_unit'),
    path('training/<int:unit_id>/', views.training_unit_detail, name='training_unit_detail'),
    path('training/<int:unit_id>/edit/', views.edit_training_unit, name='edit_training_unit'),
    path('training/<int:unit_id>/delete/', views.delete_training_unit, name='delete_training_unit'),
    
    # الروابط الخارجية
    path('links/', views.external_links_list, name='external_links_list'),
    path('links/add/', views.add_external_link, name='add_external_link'),
    path('links/<int:link_id>/edit/', views.edit_external_link, name='edit_external_link'),
    path('links/<int:link_id>/delete/', views.delete_external_link, name='delete_external_link'),
] 