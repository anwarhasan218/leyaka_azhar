from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Q, Sum, Avg
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.utils import timezone
from .models import *
from .forms import *
from accounts.models import UserProfile
import json

def is_super_admin(user):
    try:
        return user.userprofile.user_type == 'super_admin'
    except:
        return False

def is_region_admin(user):
    try:
        return user.userprofile.user_type in ['super_admin', 'region_admin']
    except:
        return False

def is_department_admin(user):
    try:
        return user.userprofile.user_type in ['super_admin', 'region_admin', 'department_admin']
    except:
        return False

def is_institute_admin(user):
    try:
        return user.userprofile.user_type in ['super_admin', 'region_admin', 'department_admin', 'institute_admin']
    except:
        return False

def can_manage_student(user_profile, student):
    """
    التحقق من صلاحيات المستخدم في إدارة الطالب
    """
    if user_profile.user_type == 'super_admin':
        return True
    elif user_profile.user_type == 'region_admin':
        return student.institute.department.region == user_profile.region
    elif user_profile.user_type == 'department_admin':
        return student.institute.department == user_profile.department
    elif user_profile.user_type == 'institute_admin':
        return student.institute == user_profile.institute
    return False

def get_available_institutes(user_profile):
    """
    الحصول على المعاهد المتاحة للمستخدم حسب صلاحياته
    """
    if user_profile.user_type == 'super_admin':
        return Institute.objects.all()
    elif user_profile.user_type == 'region_admin':
        return Institute.objects.filter(department__region=user_profile.region)
    elif user_profile.user_type == 'department_admin':
        return Institute.objects.filter(department=user_profile.department)
    elif user_profile.user_type == 'institute_admin':
        return Institute.objects.filter(id=user_profile.institute.id)
    return Institute.objects.none()

def get_available_departments(user_profile):
    """
    الحصول على الإدارات المتاحة للمستخدم حسب صلاحياته
    """
    if user_profile.user_type == 'super_admin':
        return Department.objects.all()
    elif user_profile.user_type == 'region_admin':
        return Department.objects.filter(region=user_profile.region)
    elif user_profile.user_type == 'department_admin':
        return Department.objects.filter(id=user_profile.department.id)
    elif user_profile.user_type == 'institute_admin':
        return Department.objects.filter(id=user_profile.institute.department.id)
    return Department.objects.none()

def get_available_regions(user_profile):
    """
    الحصول على المناطق المتاحة للمستخدم حسب صلاحياته
    """
    if user_profile.user_type == 'super_admin':
        return Region.objects.all()
    elif user_profile.user_type == 'region_admin':
        return Region.objects.filter(id=user_profile.region.id)
    elif user_profile.user_type == 'department_admin':
        return Region.objects.filter(id=user_profile.department.region.id)
    elif user_profile.user_type == 'institute_admin':
        return Region.objects.filter(id=user_profile.institute.department.region.id)
    return Region.objects.none()

def can_manage_region(user_profile, region):
    """
    التحقق من صلاحيات المستخدم في إدارة المنطقة
    """
    if user_profile.user_type == 'super_admin':
        return True
    elif user_profile.user_type == 'region_admin':
        return region == user_profile.region
    elif user_profile.user_type == 'department_admin':
        return region == user_profile.department.region
    elif user_profile.user_type == 'institute_admin':
        return region == user_profile.institute.department.region
    return False

def can_manage_department(user_profile, department):
    """
    التحقق من صلاحيات المستخدم في إدارة الإدارة
    """
    if user_profile.user_type == 'super_admin':
        return True
    elif user_profile.user_type == 'region_admin':
        return department.region == user_profile.region
    elif user_profile.user_type == 'department_admin':
        return department == user_profile.department
    elif user_profile.user_type == 'institute_admin':
        return department == user_profile.institute.department
    return False

def can_manage_institute(user_profile, institute):
    """
    التحقق من صلاحيات المستخدم في إدارة المعهد
    """
    if user_profile.user_type == 'super_admin':
        return True
    elif user_profile.user_type == 'region_admin':
        return institute.department.region == user_profile.region
    elif user_profile.user_type == 'department_admin':
        return institute.department == user_profile.department
    elif user_profile.user_type == 'institute_admin':
        return institute == user_profile.institute
    return False

def home(request):
    """الصفحة الرئيسية"""
    context = {
        'news': News.objects.filter(is_published=True)[:5],
        'events': Event.objects.filter(is_active=True)[:3],
        'stats': {
            'total_students': Student.objects.count(),
            'total_regions': Region.objects.count(),
            'total_departments': Department.objects.count(),
            'total_institutes': Institute.objects.count(),
        }
    }
    return render(request, 'fitness_management/home.html', context)

@login_required
def dashboard(request):
    """لوحة التحكم"""
    try:
        user_profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        # إنشاء UserProfile للمستخدم إذا لم يكن موجوداً
        user_profile = UserProfile.objects.create(
            user=request.user,
            user_type='super_admin'  # افتراضياً كإدارة عليا
        )
    
    if user_profile.user_type == 'super_admin':
        students = Student.objects.all()
        regions = Region.objects.all()
        departments = Department.objects.all()
        institutes = Institute.objects.all()
    elif user_profile.user_type == 'region_admin':
        students = Student.objects.filter(institute__department__region=user_profile.region)
        regions = Region.objects.filter(id=user_profile.region.id)
        departments = Department.objects.filter(region=user_profile.region)
        institutes = Institute.objects.filter(department__region=user_profile.region)
    elif user_profile.user_type == 'department_admin':
        students = Student.objects.filter(institute__department=user_profile.department)
        regions = Region.objects.filter(id=user_profile.department.region.id)
        departments = Department.objects.filter(id=user_profile.department.id)
        institutes = Institute.objects.filter(department=user_profile.department)
    else:  # institute_admin
        students = Student.objects.filter(institute=user_profile.institute)
        regions = Region.objects.filter(id=user_profile.institute.department.region.id)
        departments = Department.objects.filter(id=user_profile.institute.department.id)
        institutes = Institute.objects.filter(id=user_profile.institute.id)
    
    context = {
        'students': students,
        'regions': regions,
        'departments': departments,
        'institutes': institutes,
        'user_profile': user_profile,
        'today': timezone.now().date(),
        'now': timezone.now(),
    }
    return render(request, 'fitness_management/dashboard.html', context)

@login_required
def student_list(request):
    """قائمة الطلاب"""
    try:
        user_profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        # إنشاء UserProfile للمستخدم إذا لم يكن موجوداً
        user_profile = UserProfile.objects.create(
            user=request.user,
            user_type='super_admin'  # افتراضياً كإدارة عليا
        )
    
    if user_profile.user_type == 'super_admin':
        students = Student.objects.all()
    elif user_profile.user_type == 'region_admin':
        students = Student.objects.filter(institute__department__region=user_profile.region)
    elif user_profile.user_type == 'department_admin':
        students = Student.objects.filter(institute__department=user_profile.department)
    else:  # institute_admin
        students = Student.objects.filter(institute=user_profile.institute)
    
    # البحث والتصفية
    search = request.GET.get('search')
    if search:
        students = students.filter(
            Q(name__icontains=search) |
            Q(national_id__icontains=search) |
            Q(institute__name__icontains=search)
        )
    
    gender = request.GET.get('gender')
    if gender:
        students = students.filter(gender=gender)
    
    education_level = request.GET.get('education_level')
    if education_level:
        students = students.filter(education_level=education_level)
    
    # الترقيم
    paginator = Paginator(students, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search': search,
        'gender': gender,
        'education_level': education_level,
    }
    return render(request, 'fitness_management/student_list.html', context)

@login_required
def add_student(request):
    """إضافة طالب جديد - متاح لجميع المستخدمين حسب صلاحياتهم"""
    user_profile = request.user.userprofile
    
    if request.method == 'POST':
        form = StudentForm(request.POST, request.FILES, user_profile=user_profile)
        if form.is_valid():
            student = form.save(commit=False)
            
            # التحقق من الصلاحيات
            if not can_manage_student(user_profile, student):
                messages.error(request, 'لا تملك الصلاحيات لإضافة طالب لهذا المعهد!')
                return render(request, 'fitness_management/student_form.html', {'form': form, 'user_profile': user_profile})
            
            student.save()
            messages.success(request, 'تم إضافة الطالب بنجاح!')
            return redirect('fitness_management:student_detail', student.id)
    else:
        form = StudentForm(user_profile=user_profile)
    
    context = {
        'form': form,
        'user_profile': user_profile,
    }
    return render(request, 'fitness_management/student_form.html', context)

@login_required
def edit_student(request, student_id):
    """تعديل الطالب - متاح لجميع المستخدمين حسب صلاحياتهم"""
    student = get_object_or_404(Student, id=student_id)
    user_profile = request.user.userprofile
    
    # التحقق من الصلاحيات
    if not can_manage_student(user_profile, student):
        messages.error(request, 'لا تملك الصلاحيات لتعديل هذا الطالب!')
        return redirect('fitness_management:student_list')
    
    if request.method == 'POST':
        form = StudentForm(request.POST, request.FILES, instance=student, user_profile=user_profile)
        if form.is_valid():
            # التحقق من الصلاحيات مرة أخرى عند الحفظ
            if not can_manage_student(user_profile, form.instance):
                messages.error(request, 'لا تملك الصلاحيات لتعديل الطالب لهذا المعهد!')
                return render(request, 'fitness_management/student_form.html', {'form': form, 'user_profile': user_profile})
            
            form.save()
            messages.success(request, 'تم تعديل الطالب بنجاح!')
            return redirect('fitness_management:student_detail', student.id)
    else:
        form = StudentForm(instance=student, user_profile=user_profile)
    
    context = {
        'form': form,
        'user_profile': user_profile,
    }
    return render(request, 'fitness_management/student_form.html', context)

@login_required
def delete_student(request, student_id):
    """حذف الطالب - متاح لجميع المستخدمين حسب صلاحياتهم"""
    student = get_object_or_404(Student, id=student_id)
    user_profile = request.user.userprofile
    
    # التحقق من الصلاحيات
    if not can_manage_student(user_profile, student):
        messages.error(request, 'لا تملك الصلاحيات لحذف هذا الطالب!')
        return redirect('fitness_management:student_list')
    
    student.delete()
    messages.success(request, 'تم حذف الطالب بنجاح!')
    return redirect('fitness_management:student_list')

@login_required
def student_detail(request, student_id):
    """تفاصيل الطالب"""
    student = get_object_or_404(Student, id=student_id)
    tests = StudentTest.objects.filter(student=student)
    
    context = {
        'student': student,
        'tests': tests,
    }
    return render(request, 'fitness_management/student_detail.html', context)

@login_required
def add_student_test(request, student_id):
    """إضافة اختبار للطالب - متاح لجميع المستخدمين حسب صلاحياتهم"""
    student = get_object_or_404(Student, id=student_id)
    user_profile = request.user.userprofile
    
    # التحقق من الصلاحيات
    if not can_manage_student(user_profile, student):
        messages.error(request, 'لا تملك الصلاحيات لإضافة اختبار لهذا الطالب!')
        return redirect('fitness_management:student_list')
    
    if request.method == 'POST':
        form = StudentTestForm(request.POST)
        if form.is_valid():
            test = form.save(commit=False)
            test.student = student
            test.save()
            messages.success(request, 'تم إضافة الاختبار بنجاح!')
            return redirect('fitness_management:student_detail', student.id)
    else:
        form = StudentTestForm()
    
    context = {
        'form': form,
        'student': student,
        'user_profile': user_profile,
    }
    return render(request, 'fitness_management/student_test_form.html', context)

@login_required
def reports(request):
    """التقارير والإحصائيات"""
    user_profile = request.user.userprofile
    
    # تحديد نطاق البيانات حسب نوع المستخدم
    if user_profile.user_type == 'super_admin':
        students = Student.objects.all()
    elif user_profile.user_type == 'region_admin':
        students = Student.objects.filter(institute__department__region=user_profile.region)
    elif user_profile.user_type == 'department_admin':
        students = Student.objects.filter(institute__department=user_profile.department)
    else:  # institute_admin
        students = Student.objects.filter(institute=user_profile.institute)
    
    # إحصائيات عامة
    stats = {
        'total_students': students.count(),
        'male_students': students.filter(gender='male').count(),
        'female_students': students.filter(gender='female').count(),
        'primary_students': students.filter(education_level='primary').count(),
        'middle_students': students.filter(education_level='middle').count(),
        'secondary_students': students.filter(education_level='secondary').count(),
    }
    
    # إحصائيات الاختبارات
    tests = StudentTest.objects.filter(student__in=students)
    test_stats = {
        'total_tests': tests.count(),
        'average_score': tests.aggregate(Avg('score'))['score__avg'] or 0,
        'max_score': tests.aggregate(Sum('score'))['score__sum'] or 0,
    }
    
    context = {
        'stats': stats,
        'test_stats': test_stats,
        'user_profile': user_profile,
    }
    return render(request, 'fitness_management/reports.html', context)

def news_list(request):
    """قائمة الأخبار"""
    news = News.objects.filter(is_published=True)
    paginator = Paginator(news, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'fitness_management/news_list.html', context)

def news_detail(request, news_id):
    """تفاصيل الخبر"""
    news = get_object_or_404(News, id=news_id, is_published=True)
    
    context = {
        'news': news,
    }
    return render(request, 'fitness_management/news_detail.html', context)

def events_list(request):
    """قائمة الفعاليات"""
    events = Event.objects.filter(is_active=True)
    
    context = {
        'events': events,
    }
    return render(request, 'fitness_management/events_list.html', context)

def videos_list(request):
    """قائمة الفيديوهات"""
    videos = Video.objects.all()
    category = request.GET.get('category')
    if category:
        videos = videos.filter(category=category)
    
    context = {
        'videos': videos,
        'categories': Video.objects.values_list('category', flat=True).distinct(),
    }
    return render(request, 'fitness_management/videos_list.html', context)

def training_units_list(request):
    """قائمة الوحدات التدريبية"""
    units = TrainingUnit.objects.all()
    education_level = request.GET.get('education_level')
    if education_level:
        units = units.filter(education_level=education_level)
    
    context = {
        'units': units,
    }
    return render(request, 'fitness_management/training_units_list.html', context)

def external_links_list(request):
    """قائمة الروابط الخارجية"""
    links = ExternalLink.objects.all()
    
    context = {
        'links': links,
    }
    return render(request, 'fitness_management/external_links_list.html', context)

def about_project(request):
    """صفحة رؤية وأهداف المشروع"""
    return render(request, 'fitness_management/about_project.html')

def contact(request):
    """صفحة الاتصال"""
    return render(request, 'fitness_management/contact.html')

# ===== الأخبار =====
@login_required
@user_passes_test(is_super_admin)
def add_news(request):
    """إضافة خبر جديد"""
    if request.method == 'POST':
        form = NewsForm(request.POST, request.FILES)
        if form.is_valid():
            news = form.save()
            messages.success(request, 'تم إضافة الخبر بنجاح!')
            return redirect('fitness_management:news_list')
    else:
        form = NewsForm()
    
    return render(request, 'fitness_management/news_form.html', {'form': form})

@login_required
@user_passes_test(is_super_admin)
def edit_news(request, news_id):
    """تعديل الخبر"""
    news = get_object_or_404(News, id=news_id)
    if request.method == 'POST':
        form = NewsForm(request.POST, request.FILES, instance=news)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم تعديل الخبر بنجاح!')
            return redirect('fitness_management:news_list')
    else:
        form = NewsForm(instance=news)
    
    return render(request, 'fitness_management/news_form.html', {'form': form})

@login_required
@user_passes_test(is_super_admin)
def delete_news(request, news_id):
    """حذف الخبر"""
    news = get_object_or_404(News, id=news_id)
    news.delete()
    messages.success(request, 'تم حذف الخبر بنجاح!')
    return redirect('fitness_management:news_list')

# ===== الفعاليات =====
@login_required
@user_passes_test(is_super_admin)
def add_event(request):
    """إضافة فعالية جديدة"""
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save()
            messages.success(request, 'تم إضافة الفعالية بنجاح!')
            return redirect('fitness_management:events_list')
    else:
        form = EventForm()
    
    return render(request, 'fitness_management/event_form.html', {'form': form})

def event_detail(request, event_id):
    """تفاصيل الفعالية"""
    event = get_object_or_404(Event, id=event_id)
    
    context = {
        'event': event,
    }
    return render(request, 'fitness_management/event_detail.html', context)

@login_required
@user_passes_test(is_super_admin)
def edit_event(request, event_id):
    """تعديل الفعالية"""
    event = get_object_or_404(Event, id=event_id)
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم تعديل الفعالية بنجاح!')
            return redirect('fitness_management:events_list')
    else:
        form = EventForm(instance=event)
    
    return render(request, 'fitness_management/event_form.html', {'form': form})

@login_required
@user_passes_test(is_super_admin)
def delete_event(request, event_id):
    """حذف الفعالية"""
    event = get_object_or_404(Event, id=event_id)
    event.delete()
    messages.success(request, 'تم حذف الفعالية بنجاح!')
    return redirect('fitness_management:events_list')

# ===== الفيديوهات =====
@login_required
@user_passes_test(is_super_admin)
def add_video(request):
    """إضافة فيديو جديد"""
    if request.method == 'POST':
        form = VideoForm(request.POST)
        if form.is_valid():
            video = form.save()
            messages.success(request, 'تم إضافة الفيديو بنجاح!')
            return redirect('fitness_management:videos_list')
    else:
        form = VideoForm()
    
    return render(request, 'fitness_management/video_form.html', {'form': form})

@login_required
@user_passes_test(is_super_admin)
def edit_video(request, video_id):
    """تعديل الفيديو"""
    video = get_object_or_404(Video, id=video_id)
    if request.method == 'POST':
        form = VideoForm(request.POST, instance=video)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم تعديل الفيديو بنجاح!')
            return redirect('fitness_management:videos_list')
    else:
        form = VideoForm(instance=video)
    
    return render(request, 'fitness_management/video_form.html', {'form': form})

@login_required
@user_passes_test(is_super_admin)
def delete_video(request, video_id):
    """حذف الفيديو"""
    video = get_object_or_404(Video, id=video_id)
    video.delete()
    messages.success(request, 'تم حذف الفيديو بنجاح!')
    return redirect('fitness_management:videos_list')

# ===== الوحدات التدريبية =====
@login_required
@user_passes_test(is_super_admin)
def add_training_unit(request):
    """إضافة وحدة تدريبية جديدة"""
    if request.method == 'POST':
        form = TrainingUnitForm(request.POST, request.FILES)
        if form.is_valid():
            unit = form.save()
            messages.success(request, 'تم إضافة الوحدة التدريبية بنجاح!')
            return redirect('fitness_management:training_units_list')
    else:
        form = TrainingUnitForm()
    
    return render(request, 'fitness_management/training_unit_form.html', {'form': form})

def training_unit_detail(request, unit_id):
    """تفاصيل الوحدة التدريبية"""
    unit = get_object_or_404(TrainingUnit, id=unit_id)
    
    context = {
        'unit': unit,
    }
    return render(request, 'fitness_management/training_unit_detail.html', context)

@login_required
@user_passes_test(is_super_admin)
def edit_training_unit(request, unit_id):
    """تعديل الوحدة التدريبية"""
    unit = get_object_or_404(TrainingUnit, id=unit_id)
    if request.method == 'POST':
        form = TrainingUnitForm(request.POST, request.FILES, instance=unit)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم تعديل الوحدة التدريبية بنجاح!')
            return redirect('fitness_management:training_units_list')
    else:
        form = TrainingUnitForm(instance=unit)
    
    return render(request, 'fitness_management/training_unit_form.html', {'form': form})

@login_required
@user_passes_test(is_super_admin)
def delete_training_unit(request, unit_id):
    """حذف الوحدة التدريبية"""
    unit = get_object_or_404(TrainingUnit, id=unit_id)
    unit.delete()
    messages.success(request, 'تم حذف الوحدة التدريبية بنجاح!')
    return redirect('fitness_management:training_units_list')

# ===== الروابط الخارجية =====
@login_required
@user_passes_test(is_super_admin)
def add_external_link(request):
    """إضافة رابط خارجي جديد"""
    if request.method == 'POST':
        form = ExternalLinkForm(request.POST)
        if form.is_valid():
            link = form.save()
            messages.success(request, 'تم إضافة الرابط بنجاح!')
            return redirect('fitness_management:external_links_list')
    else:
        form = ExternalLinkForm()
    
    return render(request, 'fitness_management/external_link_form.html', {'form': form})

@login_required
@user_passes_test(is_super_admin)
def edit_external_link(request, link_id):
    """تعديل الرابط الخارجي"""
    link = get_object_or_404(ExternalLink, id=link_id)
    if request.method == 'POST':
        form = ExternalLinkForm(request.POST, instance=link)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم تعديل الرابط بنجاح!')
            return redirect('fitness_management:external_links_list')
    else:
        form = ExternalLinkForm(instance=link)
    
    return render(request, 'fitness_management/external_link_form.html', {'form': form})

@login_required
@user_passes_test(is_super_admin)
def delete_external_link(request, link_id):
    """حذف الرابط الخارجي"""
    link = get_object_or_404(ExternalLink, id=link_id)
    link.delete()
    messages.success(request, 'تم حذف الرابط بنجاح!')
    return redirect('fitness_management:external_links_list') 

# ===== إدارة المناطق =====
@login_required
def region_list(request):
    """قائمة المناطق - متاح لجميع المستخدمين حسب صلاحياتهم"""
    user_profile = request.user.userprofile
    
    # تحديد المناطق المتاحة حسب نوع المستخدم
    regions = get_available_regions(user_profile)
    
    context = {
        'regions': regions,
        'user_profile': user_profile,
    }
    return render(request, 'fitness_management/region_list.html', context)

@login_required
def add_region(request):
    """إضافة منطقة جديدة - متاح للإدارة العليا فقط"""
    user_profile = request.user.userprofile
    
    # التحقق من الصلاحيات
    if user_profile.user_type != 'super_admin':
        messages.error(request, 'لا تملك الصلاحيات لإضافة منطقة جديدة!')
        return redirect('fitness_management:region_list')
    
    if request.method == 'POST':
        form = RegionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم إضافة المنطقة بنجاح!')
            return redirect('fitness_management:region_list')
    else:
        form = RegionForm()
    
    context = {
        'form': form,
        'user_profile': user_profile,
    }
    return render(request, 'fitness_management/region_form.html', context)

@login_required
def edit_region(request, region_id):
    """تعديل المنطقة - متاح للإدارة العليا فقط"""
    region = get_object_or_404(Region, id=region_id)
    user_profile = request.user.userprofile
    
    # التحقق من الصلاحيات
    if user_profile.user_type != 'super_admin':
        messages.error(request, 'لا تملك الصلاحيات لتعديل المنطقة!')
        return redirect('fitness_management:region_list')
    
    if request.method == 'POST':
        form = RegionForm(request.POST, instance=region)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم تعديل المنطقة بنجاح!')
            return redirect('fitness_management:region_list')
    else:
        form = RegionForm(instance=region)
    
    context = {
        'form': form,
        'user_profile': user_profile,
    }
    return render(request, 'fitness_management/region_form.html', context)

@login_required
def delete_region(request, region_id):
    """حذف المنطقة - متاح للإدارة العليا فقط"""
    region = get_object_or_404(Region, id=region_id)
    user_profile = request.user.userprofile
    
    # التحقق من الصلاحيات
    if user_profile.user_type != 'super_admin':
        messages.error(request, 'لا تملك الصلاحيات لحذف المنطقة!')
        return redirect('fitness_management:region_list')
    
    region.delete()
    messages.success(request, 'تم حذف المنطقة بنجاح!')
    return redirect('fitness_management:region_list') 

# ===== إدارة الإدارات =====
@login_required
def department_list(request):
    """قائمة الإدارات - متاح لجميع المستخدمين حسب صلاحياتهم"""
    user_profile = request.user.userprofile
    
    # تحديد الإدارات المتاحة حسب نوع المستخدم
    departments = get_available_departments(user_profile)
    
    context = {
        'departments': departments,
        'user_profile': user_profile,
    }
    return render(request, 'fitness_management/department_list.html', context)

@login_required
def add_department(request):
    """إضافة إدارة جديدة - متاح للإدارة العليا ومشرفي المناطق"""
    user_profile = request.user.userprofile
    
    # التحقق من الصلاحيات
    if user_profile.user_type not in ['super_admin', 'region_admin']:
        messages.error(request, 'لا تملك الصلاحيات لإضافة إدارة جديدة!')
        return redirect('fitness_management:department_list')
    
    if request.method == 'POST':
        form = DepartmentForm(request.POST, user_profile=user_profile)
        if form.is_valid():
            department = form.save(commit=False)
            
            # التحقق من الصلاحيات
            if user_profile.user_type == 'region_admin' and department.region != user_profile.region:
                messages.error(request, 'لا يمكنك إضافة إدارة لمنطقة أخرى!')
                return render(request, 'fitness_management/department_form.html', {'form': form, 'user_profile': user_profile})
            
            department.save()
            messages.success(request, 'تم إضافة الإدارة بنجاح!')
            return redirect('fitness_management:department_list')
    else:
        form = DepartmentForm(user_profile=user_profile)
    
    context = {
        'form': form,
        'user_profile': user_profile,
    }
    return render(request, 'fitness_management/department_form.html', context)

@login_required
def edit_department(request, department_id):
    """تعديل الإدارة - متاح للإدارة العليا ومشرفي المناطق"""
    department = get_object_or_404(Department, id=department_id)
    user_profile = request.user.userprofile
    
    # التحقق من الصلاحيات
    if not can_manage_department(user_profile, department):
        messages.error(request, 'لا تملك الصلاحيات لتعديل هذه الإدارة!')
        return redirect('fitness_management:department_list')
    
    if request.method == 'POST':
        form = DepartmentForm(request.POST, instance=department, user_profile=user_profile)
        if form.is_valid():
            # التحقق من الصلاحيات مرة أخرى عند الحفظ
            if not can_manage_department(user_profile, form.instance):
                messages.error(request, 'لا تملك الصلاحيات لتعديل الإدارة لهذه المنطقة!')
                return render(request, 'fitness_management/department_form.html', {'form': form, 'user_profile': user_profile})
            
            form.save()
            messages.success(request, 'تم تعديل الإدارة بنجاح!')
            return redirect('fitness_management:department_list')
    else:
        form = DepartmentForm(instance=department, user_profile=user_profile)
    
    context = {
        'form': form,
        'user_profile': user_profile,
    }
    return render(request, 'fitness_management/department_form.html', context)

@login_required
def delete_department(request, department_id):
    """حذف الإدارة - متاح للإدارة العليا ومشرفي المناطق"""
    department = get_object_or_404(Department, id=department_id)
    user_profile = request.user.userprofile
    
    # التحقق من الصلاحيات
    if not can_manage_department(user_profile, department):
        messages.error(request, 'لا تملك الصلاحيات لحذف هذه الإدارة!')
        return redirect('fitness_management:department_list')
    
    department.delete()
    messages.success(request, 'تم حذف الإدارة بنجاح!')
    return redirect('fitness_management:department_list') 

# ===== إدارة المعاهد =====
@login_required
def institute_list(request):
    """قائمة المعاهد - متاح لجميع المستخدمين حسب صلاحياتهم"""
    user_profile = request.user.userprofile
    
    # تحديد المعاهد المتاحة حسب نوع المستخدم
    institutes = get_available_institutes(user_profile)
    
    context = {
        'institutes': institutes,
        'user_profile': user_profile,
    }
    return render(request, 'fitness_management/institute_list.html', context)

@login_required
def add_institute(request):
    """إضافة معهد جديد - متاح للإدارة العليا ومشرفي المناطق والإدارات"""
    user_profile = request.user.userprofile
    
    # التحقق من الصلاحيات
    if user_profile.user_type not in ['super_admin', 'region_admin', 'department_admin']:
        messages.error(request, 'لا تملك الصلاحيات لإضافة معهد جديد!')
        return redirect('fitness_management:institute_list')
    
    if request.method == 'POST':
        form = InstituteForm(request.POST, user_profile=user_profile)
        if form.is_valid():
            institute = form.save(commit=False)
            
            # التحقق من الصلاحيات
            if user_profile.user_type == 'region_admin' and institute.department.region != user_profile.region:
                messages.error(request, 'لا يمكنك إضافة معهد لمنطقة أخرى!')
                return render(request, 'fitness_management/institute_form.html', {'form': form, 'user_profile': user_profile})
            elif user_profile.user_type == 'department_admin' and institute.department != user_profile.department:
                messages.error(request, 'لا يمكنك إضافة معهد لإدارة أخرى!')
                return render(request, 'fitness_management/institute_form.html', {'form': form, 'user_profile': user_profile})
            
            institute.save()
            messages.success(request, 'تم إضافة المعهد بنجاح!')
            return redirect('fitness_management:institute_list')
    else:
        form = InstituteForm(user_profile=user_profile)
    
    context = {
        'form': form,
        'user_profile': user_profile,
    }
    return render(request, 'fitness_management/institute_form.html', context)

@login_required
def edit_institute(request, institute_id):
    """تعديل المعهد - متاح للإدارة العليا ومشرفي المناطق والإدارات"""
    institute = get_object_or_404(Institute, id=institute_id)
    user_profile = request.user.userprofile
    
    # التحقق من الصلاحيات
    if not can_manage_institute(user_profile, institute):
        messages.error(request, 'لا تملك الصلاحيات لتعديل هذا المعهد!')
        return redirect('fitness_management:institute_list')
    
    if request.method == 'POST':
        form = InstituteForm(request.POST, instance=institute, user_profile=user_profile)
        if form.is_valid():
            # التحقق من الصلاحيات مرة أخرى عند الحفظ
            if not can_manage_institute(user_profile, form.instance):
                messages.error(request, 'لا تملك الصلاحيات لتعديل المعهد لهذه الإدارة!')
                return render(request, 'fitness_management/institute_form.html', {'form': form, 'user_profile': user_profile})
            
            form.save()
            messages.success(request, 'تم تعديل المعهد بنجاح!')
            return redirect('fitness_management:institute_list')
    else:
        form = InstituteForm(instance=institute, user_profile=user_profile)
    
    context = {
        'form': form,
        'user_profile': user_profile,
    }
    return render(request, 'fitness_management/institute_form.html', context)

@login_required
def delete_institute(request, institute_id):
    """حذف المعهد - متاح للإدارة العليا ومشرفي المناطق والإدارات"""
    institute = get_object_or_404(Institute, id=institute_id)
    user_profile = request.user.userprofile
    
    # التحقق من الصلاحيات
    if not can_manage_institute(user_profile, institute):
        messages.error(request, 'لا تملك الصلاحيات لحذف هذا المعهد!')
        return redirect('fitness_management:institute_list')
    
    institute.delete()
    messages.success(request, 'تم حذف المعهد بنجاح!')
    return redirect('fitness_management:institute_list')

# ===== API للفلترة الديناميكية =====
from django.http import JsonResponse

def get_departments_by_region(request, region_id):
    """API للحصول على الإدارات حسب المنطقة المختارة"""
    try:
        departments = Department.objects.filter(region_id=region_id).values('id', 'name', 'code')
        return JsonResponse({'departments': list(departments)})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

def get_institutes_by_department(request, department_id):
    """API للحصول على المعاهد حسب الإدارة المختارة"""
    try:
        institutes = Institute.objects.filter(department_id=department_id).values('id', 'name', 'code')
        return JsonResponse({'institutes': list(institutes)})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400) 