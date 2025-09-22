# نظام إدارة المشروع القومي للياقة البدنية

نظام إدارة شامل للمشروع القومي للياقة البدنية للطلاب على مستوى الأزهر الشريف، مبني باستخدام Django.

## المميزات الرئيسية

### 🏗️ هيكل الإدارة
- **الإدارة العليا**: إدارة كاملة للمشروع
- **إدارة المنطقة**: إدارة المناطق والإدارات
- **إدارة الإدارة**: إدارة المعاهد والطلاب
- **إدارة المعهد**: تسجيل الطلاب وإدارة الاختبارات

### 👥 إدارة الطلاب
- تسجيل الطلاب مع البيانات الكاملة
- رفع الصور الشخصية ووثائق الميلاد
- تصنيف حسب النوع (بنين/فتيات)
- تصنيف حسب المرحلة التعليمية (ابتدائي/إعدادي/ثانوي)

### 📊 نظام التقييم
- اختبارات شاملة للطلاب
- تتبع الدرجات والتقدم
- إحصائيات مفصلة لكل مستوى
- تقارير تفصيلية

### 🏆 نظام التصعيد
- تصعيد تلقائي للطلاب المتفوقين
- مسابقات على مستوى المعهد
- مسابقات على مستوى الإدارة
- مسابقات على مستوى المنطقة
- لقاء القمة على مستوى الجمهورية

### 📰 المحتوى التعليمي
- أخبار المشروع
- فعاليات ومواعيد
- فيديوهات تعليمية
- وحدات تدريبية
- روابط خارجية

## التقنيات المستخدمة

- **Backend**: Django 4.2.7
- **Frontend**: Bootstrap 5
- **Database**: SQLite (قابل للتطوير لـ PostgreSQL)
- **Authentication**: Django Built-in
- **File Upload**: Pillow
- **Forms**: Django Crispy Forms
- **Rich Text**: CKEditor

## التثبيت والتشغيل

### المتطلبات
- Python 3.8+
- pip

### خطوات التثبيت

1. **استنساخ المشروع**
```bash
git clone <repository-url>
cd fitness_project
```

2. **إنشاء البيئة الافتراضية**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# أو
venv\Scripts\activate  # Windows
```

3. **تثبيت المتطلبات**
```bash
pip install -r requirements.txt
```

4. **إعداد قاعدة البيانات**
```bash
python manage.py makemigrations
python manage.py migrate
```

5. **إنشاء مستخدم مدير**
```bash
python manage.py createsuperuser
```

6. **تشغيل الخادم**
```bash
python manage.py runserver
```

7. **فتح المتصفح**
```
http://localhost:8000
```

## هيكل المشروع

```
fitness_project/
├── accounts/                 # إدارة الحسابات
│   ├── models.py            # نماذج المستخدمين
│   ├── views.py             # واجهات الحسابات
│   ├── forms.py             # نماذج التسجيل
│   └── urls.py              # روابط الحسابات
├── fitness_management/       # التطبيق الرئيسي
│   ├── models.py            # نماذج البيانات
│   ├── views.py             # واجهات النظام
│   ├── forms.py             # نماذج الإدخال
│   ├── admin.py             # إدارة Django Admin
│   └── urls.py              # روابط النظام
├── templates/               # قوالب HTML
│   ├── base.html           # القالب الأساسي
│   ├── accounts/           # قوالب الحسابات
│   └── fitness_management/ # قوالب النظام
├── static/                 # الملفات الثابتة
├── media/                  # الملفات المرفوعة
├── manage.py               # إدارة Django
└── requirements.txt        # متطلبات المشروع
```

## الصلاحيات والوظائف

### الإدارة العليا
- إدارة كاملة للمشروع
- إضافة المناطق
- إضافة مديري المناطق
- عرض جميع البيانات والتقارير

### إدارة المنطقة
- إدارة المنطقة المخصصة
- إضافة الإدارات
- إضافة مديري الإدارات
- اختيار طلاب المنطقة للمسابقات

### إدارة الإدارة
- إدارة الإدارة المخصصة
- إضافة المعاهد
- إضافة مديري المعاهد
- اختيار طلاب الإدارة للمسابقات

### إدارة المعهد
- تسجيل الطلاب
- إدارة الاختبارات
- اختيار طلاب المعهد للمسابقات

## النشر على الخادم

### Ubuntu Server
```bash
# تثبيت المتطلبات
sudo apt update
sudo apt install python3 python3-pip nginx

# إعداد المشروع
cd /var/www/
git clone <repository-url>
cd fitness_project

# إنشاء البيئة الافتراضية
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# إعداد قاعدة البيانات
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic

# إعداد Gunicorn
pip install gunicorn
gunicorn --bind 0.0.0.0:8000 fitness_project.wsgi:application
```

### Hostinger
1. رفع الملفات عبر FTP
2. إعداد قاعدة البيانات MySQL
3. تعديل إعدادات قاعدة البيانات
4. تشغيل الخادم

## الدعم والمساعدة

للمساعدة والدعم التقني، يرجى التواصل مع فريق التطوير.

## الترخيص

هذا المشروع مملوك للأزهر الشريف وجميع الحقوق محفوظة. 