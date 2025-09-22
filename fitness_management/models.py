from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.models import User

class AcademicYear(models.Model):
    name = models.CharField(max_length=50, verbose_name="اسم العام الدراسي")
    start_date = models.DateField(verbose_name="تاريخ البداية")
    end_date = models.DateField(verbose_name="تاريخ النهاية")
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    
    class Meta:
        verbose_name = "العام الدراسي"
        verbose_name_plural = "السنوات الدراسية"
    
    def __str__(self):
        return self.name

class Region(models.Model):
    name = models.CharField(max_length=100, verbose_name="اسم المنطقة")
    code = models.CharField(max_length=10, unique=True, verbose_name="رمز المنطقة")
    
    class Meta:
        verbose_name = "المنطقة"
        verbose_name_plural = "المناطق"
    
    def __str__(self):
        return self.name

class Department(models.Model):
    name = models.CharField(max_length=100, verbose_name="اسم الإدارة")
    region = models.ForeignKey(Region, on_delete=models.CASCADE, verbose_name="المنطقة")
    code = models.CharField(max_length=10, unique=True, verbose_name="رمز الإدارة")
    
    class Meta:
        verbose_name = "الإدارة"
        verbose_name_plural = "الإدارات"
    
    def __str__(self):
        return f"{self.name} - {self.region.name}"

class Institute(models.Model):
    name = models.CharField(max_length=100, verbose_name="اسم المعهد")
    department = models.ForeignKey(Department, on_delete=models.CASCADE, verbose_name="الإدارة")
    code = models.CharField(max_length=10, unique=True, verbose_name="رمز المعهد")
    
    class Meta:
        verbose_name = "المعهد"
        verbose_name_plural = "المعاهد"
    
    def __str__(self):
        return f"{self.name} - {self.department.name}"

class Student(models.Model):
    GENDER_CHOICES = [
        ('male', 'بنين'),
        ('female', 'فتيات'),
    ]
    
    EDUCATION_LEVELS = [
        ('primary', 'ابتدائي'),
        ('middle', 'إعدادي'),
        ('secondary', 'ثانوي'),
    ]
    
    name = models.CharField(max_length=100, verbose_name="اسم الطالب")
    national_id = models.CharField(max_length=14, unique=True, verbose_name="الرقم القومي")
    gender = models.CharField(max_length=6, choices=GENDER_CHOICES, verbose_name="النوع")
    education_level = models.CharField(max_length=10, choices=EDUCATION_LEVELS, verbose_name="المرحلة التعليمية")
    grade = models.CharField(max_length=20, verbose_name="الصف")
    institute = models.ForeignKey(Institute, on_delete=models.CASCADE, verbose_name="المعهد")
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, verbose_name="العام الدراسي")
    
    # الصور
    personal_photo = models.ImageField(upload_to='students/photos/', verbose_name="الصورة الشخصية")
    birth_certificate = models.ImageField(upload_to='students/documents/', verbose_name="شهادة الميلاد/البطاقة")
    
    # معلومات إضافية
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="رقم الهاتف يجب أن يكون بالصيغة: '+999999999'. يسمح حتى 15 رقم."
    )
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True, verbose_name="رقم الهاتف")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "الطالب"
        verbose_name_plural = "الطلاب"
    
    def __str__(self):
        return f"{self.name} - {self.institute.name}"
    
    @property
    def region(self):
        return self.institute.department.region
    
    @property
    def department(self):
        return self.institute.department

class Test(models.Model):
    name = models.CharField(max_length=100, verbose_name="اسم الاختبار")
    description = models.TextField(verbose_name="وصف الاختبار")
    education_level = models.CharField(max_length=10, choices=Student.EDUCATION_LEVELS, verbose_name="المرحلة التعليمية")
    gender = models.CharField(max_length=6, choices=Student.GENDER_CHOICES, verbose_name="النوع")
    max_score = models.IntegerField(verbose_name="الدرجة القصوى")
    
    class Meta:
        verbose_name = "الاختبار"
        verbose_name_plural = "الاختبارات"
    
    def __str__(self):
        return f"{self.name} - {self.get_education_level_display()} - {self.get_gender_display()}"

class StudentTest(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name="الطالب")
    test = models.ForeignKey(Test, on_delete=models.CASCADE, verbose_name="الاختبار")
    score = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="الدرجة")
    notes = models.TextField(blank=True, verbose_name="ملاحظات")
    test_date = models.DateField(verbose_name="تاريخ الاختبار")
    
    class Meta:
        verbose_name = "اختبار الطالب"
        verbose_name_plural = "اختبارات الطلاب"
        unique_together = ['student', 'test']
    
    def __str__(self):
        return f"{self.student.name} - {self.test.name} - {self.score}"

class News(models.Model):
    title = models.CharField(max_length=200, verbose_name="العنوان")
    content = models.TextField(verbose_name="المحتوى")
    image = models.ImageField(upload_to='news/', blank=True, verbose_name="الصورة")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(default=True, verbose_name="منشور")
    
    class Meta:
        verbose_name = "الخبر"
        verbose_name_plural = "الأخبار"
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title

class Event(models.Model):
    title = models.CharField(max_length=200, verbose_name="العنوان")
    description = models.TextField(verbose_name="الوصف")
    start_date = models.DateTimeField(verbose_name="تاريخ البداية")
    end_date = models.DateTimeField(verbose_name="تاريخ النهاية")
    location = models.CharField(max_length=200, verbose_name="الموقع")
    image = models.ImageField(upload_to='events/', blank=True, verbose_name="الصورة")
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    
    class Meta:
        verbose_name = "الفعالية"
        verbose_name_plural = "الفعاليات"
        ordering = ['start_date']
    
    def __str__(self):
        return self.title

class Video(models.Model):
    title = models.CharField(max_length=200, verbose_name="العنوان")
    description = models.TextField(verbose_name="الوصف")
    video_url = models.URLField(verbose_name="رابط الفيديو")
    category = models.CharField(max_length=50, verbose_name="الفئة")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "الفيديو"
        verbose_name_plural = "الفيديوهات"
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title

class TrainingUnit(models.Model):
    title = models.CharField(max_length=200, verbose_name="العنوان")
    content = models.TextField(verbose_name="المحتوى")
    education_level = models.CharField(max_length=10, choices=Student.EDUCATION_LEVELS, verbose_name="المرحلة التعليمية")
    file = models.FileField(upload_to='training/', blank=True, verbose_name="الملف")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "الوحدة التدريبية"
        verbose_name_plural = "الوحدات التدريبية"
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title

class ExternalLink(models.Model):
    title = models.CharField(max_length=200, verbose_name="العنوان")
    url = models.URLField(verbose_name="الرابط")
    description = models.TextField(blank=True, verbose_name="الوصف")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "الرابط الخارجي"
        verbose_name_plural = "الروابط الخارجية"
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title 