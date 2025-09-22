#!/usr/bin/env python
"""
سكريبت إنشاء UserProfile للمستخدم الحالي
"""

import os
import django

# إعداد Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fitness_project.settings')
django.setup()

from django.contrib.auth.models import User
from accounts.models import UserProfile

def create_userprofile_for_admin():
    """إنشاء UserProfile للمستخدم admin"""
    
    # البحث عن المستخدم admin
    try:
        admin_user = User.objects.get(username='admin')
    except User.DoesNotExist:
        print("لم يتم العثور على مستخدم باسم 'admin'")
        print("الرجاء إدخال اسم المستخدم:")
        username = input().strip()
        try:
            admin_user = User.objects.get(username=username)
        except User.DoesNotExist:
            print(f"لم يتم العثور على مستخدم باسم '{username}'")
            return
    
    # التحقق من وجود UserProfile
    try:
        profile = admin_user.userprofile
        print(f"UserProfile موجود بالفعل للمستخدم {admin_user.username}")
        print(f"نوع المستخدم: {profile.get_user_type_display()}")
    except UserProfile.DoesNotExist:
        # إنشاء UserProfile
        profile = UserProfile.objects.create(
            user=admin_user,
            user_type='super_admin',
            phone_number=''
        )
        print(f"تم إنشاء UserProfile للمستخدم {admin_user.username}")
        print(f"نوع المستخدم: {profile.get_user_type_display()}")
    
    print("تم إكمال العملية بنجاح!")

if __name__ == '__main__':
    create_userprofile_for_admin()
