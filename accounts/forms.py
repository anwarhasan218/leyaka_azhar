from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True, label='الاسم الأول')
    last_name = forms.CharField(max_length=30, required=True, label='اسم العائلة')
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
        labels = {
            'username': 'اسم المستخدم',
            'email': 'البريد الإلكتروني',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('user_type', 'phone_number', 'region', 'department', 'institute')
        labels = {
            'user_type': 'نوع المستخدم',
            'phone_number': 'رقم الهاتف',
            'region': 'المنطقة',
            'department': 'الإدارة',
            'institute': 'المعهد',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control' 