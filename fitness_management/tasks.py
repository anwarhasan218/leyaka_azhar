"""
Background tasks for fitness_management app.
"""

import os
import shutil
import zipfile
from datetime import datetime, timedelta
from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.db import connection
from .models import Student, StudentTest, News, Event

@shared_task
def backup_database():
    """نسخ احتياطي لقاعدة البيانات"""
    try:
        from django.core.management import call_command
        from django.utils import timezone
        
        # إنشاء اسم الملف
        timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f'backup_{timestamp}.json'
        backup_path = os.path.join(settings.BACKUP_DIR, backup_filename)
        
        # إنشاء النسخة الاحتياطية
        call_command('dumpdata', 
                    exclude=['contenttypes', 'auth.permission'],
                    output=backup_path,
                    indent=2)
        
        # ضغط الملف
        zip_filename = f'{backup_path}.zip'
        with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(backup_path, os.path.basename(backup_path))
        
        # حذف الملف الأصلي
        os.remove(backup_path)
        
        # حذف النسخ الاحتياطية القديمة
        cleanup_old_backups()
        
        return f"Database backup created: {zip_filename}"
    except Exception as e:
        return f"Backup failed: {str(e)}"

@shared_task
def cleanup_old_backups():
    """حذف النسخ الاحتياطية القديمة"""
    try:
        retention_days = getattr(settings, 'BACKUP_RETENTION_DAYS', 30)
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        
        for filename in os.listdir(settings.BACKUP_DIR):
            file_path = os.path.join(settings.BACKUP_DIR, filename)
            if os.path.isfile(file_path):
                file_time = datetime.fromtimestamp(os.path.getctime(file_path))
                if file_time < cutoff_date:
                    os.remove(file_path)
        
        return "Old backups cleaned up"
    except Exception as e:
        return f"Cleanup failed: {str(e)}"

@shared_task
def cleanup_old_files():
    """حذف الملفات القديمة"""
    try:
        # حذف الملفات المؤقتة
        temp_dirs = ['temp', 'cache', 'tmp']
        for temp_dir in temp_dirs:
            temp_path = os.path.join(settings.MEDIA_ROOT, temp_dir)
            if os.path.exists(temp_path):
                shutil.rmtree(temp_path)
                os.makedirs(temp_path)
        
        return "Old files cleaned up"
    except Exception as e:
        return f"File cleanup failed: {str(e)}"

@shared_task
def generate_periodic_reports():
    """إنشاء التقارير الدورية"""
    try:
        from .models import Region, Department, Institute
        
        # إحصائيات عامة
        stats = {
            'total_students': Student.objects.count(),
            'total_regions': Region.objects.count(),
            'total_departments': Department.objects.count(),
            'total_institutes': Institute.objects.count(),
            'total_tests': StudentTest.objects.count(),
        }
        
        # إحصائيات حسب النوع
        male_students = Student.objects.filter(gender='male').count()
        female_students = Student.objects.filter(gender='female').count()
        
        # إحصائيات حسب المرحلة التعليمية
        primary_students = Student.objects.filter(education_level='primary').count()
        middle_students = Student.objects.filter(education_level='middle').count()
        secondary_students = Student.objects.filter(education_level='secondary').count()
        
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'general_stats': stats,
            'gender_stats': {
                'male': male_students,
                'female': female_students,
            },
            'education_stats': {
                'primary': primary_students,
                'middle': middle_students,
                'secondary': secondary_students,
            }
        }
        
        # حفظ التقرير
        report_filename = f'report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        report_path = os.path.join(settings.BACKUP_DIR, 'reports', report_filename)
        
        os.makedirs(os.path.dirname(report_path), exist_ok=True)
        
        import json
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        return f"Periodic report generated: {report_filename}"
    except Exception as e:
        return f"Report generation failed: {str(e)}"

@shared_task
def send_notification_email(subject, message, recipient_list):
    """إرسال إشعار بالبريد الإلكتروني"""
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipient_list,
            fail_silently=False,
        )
        return f"Email sent to {len(recipient_list)} recipients"
    except Exception as e:
        return f"Email sending failed: {str(e)}"

@shared_task
def export_student_data(student_ids, format='json'):
    """تصدير بيانات الطلاب"""
    try:
        students = Student.objects.filter(id__in=student_ids)
        
        if format == 'json':
            from django.core.serializers import serialize
            data = serialize('json', students)
        elif format == 'csv':
            import csv
            from io import StringIO
            
            output = StringIO()
            writer = csv.writer(output)
            
            # كتابة العناوين
            writer.writerow(['ID', 'Name', 'National ID', 'Gender', 'Education Level', 'Grade', 'Institute'])
            
            # كتابة البيانات
            for student in students:
                writer.writerow([
                    student.id,
                    student.name,
                    student.national_id,
                    student.get_gender_display(),
                    student.get_education_level_display(),
                    student.grade,
                    student.institute.name
                ])
            
            data = output.getvalue()
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        # حفظ الملف
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'students_export_{timestamp}.{format}'
        file_path = os.path.join(settings.BACKUP_DIR, 'exports', filename)
        
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(data)
        
        return f"Student data exported: {filename}"
    except Exception as e:
        return f"Export failed: {str(e)}"

@shared_task
def generate_student_report(student_id):
    """إنشاء تقرير الطالب"""
    try:
        student = Student.objects.get(id=student_id)
        tests = StudentTest.objects.filter(student=student)
        
        report_data = {
            'student_info': {
                'id': student.id,
                'name': student.name,
                'national_id': student.national_id,
                'gender': student.get_gender_display(),
                'education_level': student.get_education_level_display(),
                'grade': student.grade,
                'institute': student.institute.name,
            },
            'tests': [],
            'statistics': {
                'total_tests': tests.count(),
                'average_score': 0,
                'total_score': 0,
            }
        }
        
        total_score = 0
        for test in tests:
            test_data = {
                'test_name': test.test.name,
                'score': float(test.score),
                'max_score': test.test.max_score,
                'percentage': (test.score / test.test.max_score) * 100,
                'test_date': test.test_date.isoformat(),
                'notes': test.notes,
            }
            report_data['tests'].append(test_data)
            total_score += test.score
        
        if tests.count() > 0:
            report_data['statistics']['total_score'] = total_score
            report_data['statistics']['average_score'] = total_score / tests.count()
        
        # حفظ التقرير
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'student_report_{student_id}_{timestamp}.json'
        file_path = os.path.join(settings.BACKUP_DIR, 'reports', filename)
        
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        import json
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        return f"Student report generated: {filename}"
    except Student.DoesNotExist:
        return f"Student with ID {student_id} not found"
    except Exception as e:
        return f"Report generation failed: {str(e)}"

@shared_task
def cleanup_database():
    """تنظيف قاعدة البيانات"""
    try:
        # حذف السجلات القديمة (أكثر من سنة)
        cutoff_date = datetime.now() - timedelta(days=365)
        
        # حذف الأخبار القديمة
        old_news = News.objects.filter(created_at__lt=cutoff_date)
        old_news_count = old_news.count()
        old_news.delete()
        
        # حذف الفعاليات المنتهية
        old_events = Event.objects.filter(end_date__lt=datetime.now())
        old_events_count = old_events.count()
        old_events.delete()
        
        return f"Database cleaned: {old_news_count} old news, {old_events_count} old events"
    except Exception as e:
        return f"Database cleanup failed: {str(e)}"

@shared_task
def optimize_database():
    """تحسين قاعدة البيانات"""
    try:
        with connection.cursor() as cursor:
            # تحليل الجداول
            cursor.execute("ANALYZE;")
            
            # إعادة بناء الفهارس
            cursor.execute("REINDEX DATABASE fitness_project;")
        
        return "Database optimized successfully"
    except Exception as e:
        return f"Database optimization failed: {str(e)}" 