from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator

class UserProfile(models.Model):
    USER_TYPES = [
        ('super_admin', 'إدارة عليا'),
        ('region_admin', 'إدارة منطقة'),
        ('department_admin', 'إدارة إدارة'),
        ('institute_admin', 'إدارة معهد'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_type = models.CharField(max_length=20, choices=USER_TYPES)
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="رقم الهاتف يجب أن يكون بالصيغة: '+999999999'. يسمح حتى 15 رقم."
    )
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    
    # العلاقات الإدارية
    region = models.ForeignKey('fitness_management.Region', on_delete=models.CASCADE, null=True, blank=True)
    department = models.ForeignKey('fitness_management.Department', on_delete=models.CASCADE, null=True, blank=True)
    institute = models.ForeignKey('fitness_management.Institute', on_delete=models.CASCADE, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "ملف المستخدم"
        verbose_name_plural = "ملفات المستخدمين"
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.get_user_type_display()}"
    
    def get_full_name(self):
        return self.user.get_full_name()
    
    def get_username(self):
        return self.user.username 