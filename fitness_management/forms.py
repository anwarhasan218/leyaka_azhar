from django import forms
from .models import Student, StudentTest, News, Event, Video, TrainingUnit, ExternalLink, Region, Department, Institute

class StudentForm(forms.ModelForm):
    region = forms.ModelChoiceField(
        queryset=Region.objects.all(),
        empty_label="اختر المنطقة",
        label="المنطقة",
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    department = forms.ModelChoiceField(
        queryset=Department.objects.none(),
        empty_label="اختر الإدارة",
        label="الإدارة",
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = Student
        fields = [
            'name', 'national_id', 'gender', 'education_level', 'grade',
            'institute', 'academic_year', 'personal_photo', 'birth_certificate', 'phone_number'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'national_id': forms.TextInput(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'education_level': forms.Select(attrs={'class': 'form-control'}),
            'grade': forms.TextInput(attrs={'class': 'form-control'}),
            'institute': forms.Select(attrs={'class': 'form-control'}),
            'academic_year': forms.Select(attrs={'class': 'form-control'}),
            'personal_photo': forms.FileInput(attrs={'class': 'form-control'}),
            'birth_certificate': forms.FileInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        user_profile = kwargs.pop('user_profile', None)
        super().__init__(*args, **kwargs)
        
        if user_profile:
            # فلترة المناطق حسب صلاحيات المستخدم
            if user_profile.user_type == 'super_admin':
                self.fields['region'].queryset = Region.objects.all()
            elif user_profile.user_type == 'region_admin':
                self.fields['region'].queryset = Region.objects.filter(id=user_profile.region.id)
                self.fields['region'].initial = user_profile.region
                self.fields['region'].widget.attrs['readonly'] = True
            elif user_profile.user_type == 'department_admin':
                self.fields['region'].queryset = Region.objects.filter(id=user_profile.department.region.id)
                self.fields['region'].initial = user_profile.department.region
                self.fields['region'].widget.attrs['readonly'] = True
            else:  # institute_admin
                self.fields['region'].queryset = Region.objects.filter(id=user_profile.institute.department.region.id)
                self.fields['region'].initial = user_profile.institute.department.region
                self.fields['region'].widget.attrs['readonly'] = True
            
            # تعيين الإدارات حسب المنطقة الأولية
            if user_profile.user_type == 'region_admin':
                self.fields['department'].queryset = Department.objects.filter(region=user_profile.region)
            elif user_profile.user_type == 'department_admin':
                self.fields['department'].queryset = Department.objects.filter(id=user_profile.department.id)
                self.fields['department'].initial = user_profile.department
            elif user_profile.user_type == 'institute_admin':
                self.fields['department'].queryset = Department.objects.filter(id=user_profile.institute.department.id)
                self.fields['department'].initial = user_profile.institute.department
            else:
                # للمستخدمين العاديين، عرض جميع الإدارات
                self.fields['department'].queryset = Department.objects.all()
                
            # إذا كان هناك منطقة محددة مسبقاً، عرض إداراتها
            if self.fields['region'].initial:
                region = self.fields['region'].initial
                self.fields['department'].queryset = Department.objects.filter(region=region)
                
            # تعيين المعاهد حسب الإدارة الأولية
            if user_profile.user_type == 'institute_admin':
                self.fields['institute'].queryset = Institute.objects.filter(id=user_profile.institute.id)
                self.fields['institute'].initial = user_profile.institute
            else:
                # للمستخدمين الآخرين، عرض المعاهد حسب الإدارة المحددة
                if self.fields['department'].initial:
                    department = self.fields['department'].initial
                    self.fields['institute'].queryset = Institute.objects.filter(department=department)

class StudentTestForm(forms.ModelForm):
    class Meta:
        model = StudentTest
        fields = ['test', 'score', 'notes', 'test_date']
        widgets = {
            'test': forms.Select(attrs={'class': 'form-control'}),
            'score': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'test_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

class NewsForm(forms.ModelForm):
    class Meta:
        model = News
        fields = ['title', 'content', 'image', 'is_published']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'is_published': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'description', 'start_date', 'end_date', 'location', 'image', 'is_active']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'start_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'end_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class VideoForm(forms.ModelForm):
    class Meta:
        model = Video
        fields = ['title', 'description', 'video_url', 'category']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'video_url': forms.URLInput(attrs={'class': 'form-control'}),
            'category': forms.TextInput(attrs={'class': 'form-control'}),
        }

class TrainingUnitForm(forms.ModelForm):
    class Meta:
        model = TrainingUnit
        fields = ['title', 'content', 'education_level', 'file']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'education_level': forms.Select(attrs={'class': 'form-control'}),
            'file': forms.FileInput(attrs={'class': 'form-control'}),
        }

class ExternalLinkForm(forms.ModelForm):
    class Meta:
        model = ExternalLink
        fields = ['title', 'url', 'description']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'url': forms.URLInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class RegionForm(forms.ModelForm):
    class Meta:
        model = Region
        fields = ['name', 'code']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
        }

class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['name', 'region', 'code']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        user_profile = kwargs.pop('user_profile', None)
        super().__init__(*args, **kwargs)
        
        if user_profile:
            # فلترة المناطق حسب صلاحيات المستخدم
            if user_profile.user_type == 'super_admin':
                self.fields['region'].queryset = Region.objects.all()
            elif user_profile.user_type == 'region_admin':
                self.fields['region'].queryset = Region.objects.filter(id=user_profile.region.id)
                self.fields['region'].initial = user_profile.region
                self.fields['region'].widget.attrs['readonly'] = True
            else:
                self.fields['region'].queryset = Region.objects.none()

class InstituteForm(forms.ModelForm):
    region = forms.ModelChoiceField(
        queryset=Region.objects.all(),
        empty_label="اختر المنطقة",
        label="المنطقة",
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    department = forms.ModelChoiceField(
        queryset=Department.objects.none(),
        empty_label="اختر الإدارة",
        label="الإدارة",
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = Institute
        fields = ['name', 'code']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        user_profile = kwargs.pop('user_profile', None)
        super().__init__(*args, **kwargs)
        
        if user_profile:
            # فلترة المناطق حسب صلاحيات المستخدم
            if user_profile.user_type == 'super_admin':
                self.fields['region'].queryset = Region.objects.all()
            elif user_profile.user_type == 'region_admin':
                self.fields['region'].queryset = Region.objects.filter(id=user_profile.region.id)
                self.fields['region'].initial = user_profile.region
                self.fields['region'].widget.attrs['readonly'] = True
            elif user_profile.user_type == 'department_admin':
                self.fields['region'].queryset = Region.objects.filter(id=user_profile.department.region.id)
                self.fields['region'].initial = user_profile.department.region
                self.fields['region'].widget.attrs['readonly'] = True
            else:
                self.fields['region'].queryset = Region.objects.none()
            
            # تعيين الإدارات حسب المنطقة الأولية
            if user_profile.user_type == 'region_admin':
                self.fields['department'].queryset = Department.objects.filter(region=user_profile.region)
            elif user_profile.user_type == 'department_admin':
                self.fields['department'].queryset = Department.objects.filter(id=user_profile.department.id)
                self.fields['department'].initial = user_profile.department
            else:
                # للمستخدمين العاديين، عرض جميع الإدارات
                self.fields['department'].queryset = Department.objects.all()
                
            # إذا كان هناك منطقة محددة مسبقاً، عرض إداراتها
            if self.fields['region'].initial:
                region = self.fields['region'].initial
                self.fields['department'].queryset = Department.objects.filter(region=region)
    
    def save(self, commit=True):
        """حفظ المعهد مع التأكد من صحة العلاقة مع الإدارة"""
        institute = super().save(commit=False)
        
        # تعيين الإدارة المختارة
        if hasattr(self, 'cleaned_data') and 'department' in self.cleaned_data:
            institute.department = self.cleaned_data['department']
        
        # التأكد من أن الإدارة المختارة تنتمي للمنطقة المحددة
        if hasattr(self, 'cleaned_data') and 'region' in self.cleaned_data:
            region = self.cleaned_data['region']
            if institute.department and institute.department.region != region:
                # البحث عن إدارة في المنطقة المحددة
                department = Department.objects.filter(region=region).first()
                if department:
                    institute.department = department
        
        if commit:
            institute.save()
        return institute
    
    def clean(self):
        """تنظيف البيانات والتحقق من صحة العلاقات"""
        cleaned_data = super().clean()
        region = cleaned_data.get('region')
        department = cleaned_data.get('department')
        
        if region and department:
            if department.region != region:
                raise forms.ValidationError('الإدارة المختارة يجب أن تنتمي للمنطقة المحددة')
        
        return cleaned_data 