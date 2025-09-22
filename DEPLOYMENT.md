# دليل النشر - نظام إدارة المشروع القومي للياقة البدنية

## النشر على Ubuntu Server

### المتطلبات الأساسية
- Ubuntu 20.04 LTS أو أحدث
- وصول sudo
- اتصال بالإنترنت

### خطوات النشر السريع

1. **استنساخ المشروع**
```bash
git clone <repository-url>
cd fitness_project
```

2. **تشغيل سكريبت النشر**
```bash
chmod +x deploy.sh
./deploy.sh
```

### النشر اليدوي

#### 1. إعداد النظام
```bash
# تحديث النظام
sudo apt update && sudo apt upgrade -y

# تثبيت المتطلبات
sudo apt install -y python3 python3-pip python3-venv nginx postgresql postgresql-contrib
```

#### 2. إعداد المشروع
```bash
# إنشاء مجلد المشروع
sudo mkdir -p /var/www/fitness_project
sudo chown $USER:$USER /var/www/fitness_project

# نسخ الملفات
cp -r . /var/www/fitness_project/
cd /var/www/fitness_project

# إنشاء البيئة الافتراضية
python3 -m venv venv
source venv/bin/activate

# تثبيت المتطلبات
pip install -r requirements_production.txt
```

#### 3. إعداد قاعدة البيانات
```bash
# إنشاء قاعدة البيانات
sudo -u postgres psql << EOF
CREATE DATABASE fitness_project;
CREATE USER fitness_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE fitness_project TO fitness_user;
EOF
```

#### 4. إعداد المتغيرات البيئية
```bash
# إنشاء ملف .env
cat > .env << EOF
SECRET_KEY=$(python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')
DEBUG=False
DB_NAME=fitness_project
DB_USER=fitness_user
DB_PASSWORD=your_secure_password
DB_HOST=localhost
DB_PORT=5432
EOF
```

#### 5. تشغيل الهجرات
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic --noinput
```

#### 6. إعداد systemd
```bash
# نسخ ملفات الخدمة
sudo cp fitness_project.service /etc/systemd/system/
sudo cp fitness_project.socket /etc/systemd/system/

# إعادة تحميل systemd
sudo systemctl daemon-reload

# تفعيل الخدمات
sudo systemctl enable fitness_project.socket
sudo systemctl enable fitness_project.service
```

#### 7. إعداد Nginx
```bash
# نسخ إعدادات Nginx
sudo cp nginx_fitness_project /etc/nginx/sites-available/fitness_project
sudo ln -sf /etc/nginx/sites-available/fitness_project /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# اختبار الإعدادات
sudo nginx -t
```

#### 8. تشغيل الخدمات
```bash
# تعيين الصلاحيات
sudo chown -R www-data:www-data /var/www/fitness_project
sudo chmod -R 755 /var/www/fitness_project

# تشغيل الخدمات
sudo systemctl start fitness_project.socket
sudo systemctl start fitness_project.service
sudo systemctl restart nginx
```

## النشر على Hostinger

### 1. رفع الملفات
- استخدم FTP أو File Manager لرفع جميع ملفات المشروع
- تأكد من رفع جميع الملفات والمجلدات

### 2. إعداد قاعدة البيانات
- اذهب إلى cPanel > MySQL Databases
- أنشئ قاعدة بيانات جديدة
- أنشئ مستخدم جديد واربطه بقاعدة البيانات

### 3. تعديل الإعدادات
```python
# في fitness_project/settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'your_database_name',
        'USER': 'your_database_user',
        'PASSWORD': 'your_database_password',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

### 4. تشغيل الهجرات
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic --noinput
```

### 5. إنشاء مستخدم مدير
```bash
python manage.py createsuperuser
```

## إعداد SSL

### باستخدام Let's Encrypt
```bash
# تثبيت Certbot
sudo apt install -y certbot python3-certbot-nginx

# الحصول على شهادة SSL
sudo certbot --nginx -d your-domain.com
```

### تجديد الشهادة تلقائياً
```bash
# إضافة إلى crontab
sudo crontab -e

# إضافة السطر التالي
0 12 * * * /usr/bin/certbot renew --quiet
```

## مراقبة النظام

### فحص حالة الخدمات
```bash
# حالة الخدمة
sudo systemctl status fitness_project

# سجلات الخدمة
sudo journalctl -u fitness_project -f

# سجلات Nginx
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### إعادة تشغيل الخدمات
```bash
# إعادة تشغيل التطبيق
sudo systemctl restart fitness_project

# إعادة تشغيل Nginx
sudo systemctl restart nginx

# إعادة تشغيل قاعدة البيانات
sudo systemctl restart postgresql
```

## النسخ الاحتياطي

### قاعدة البيانات
```bash
# إنشاء نسخة احتياطية
pg_dump fitness_project > backup_$(date +%Y%m%d_%H%M%S).sql

# استعادة نسخة احتياطية
psql fitness_project < backup_file.sql
```

### الملفات
```bash
# نسخ احتياطي للملفات
tar -czf media_backup_$(date +%Y%m%d_%H%M%S).tar.gz media/
```

## الأمان

### تحديث النظام
```bash
sudo apt update && sudo apt upgrade -y
```

### جدار الحماية
```bash
# تثبيت UFW
sudo apt install ufw

# إعداد القواعد
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw enable
```

### مراقبة الأمان
```bash
# فحص الملفات المشبوهة
sudo find /var/www -type f -exec grep -l "eval(" {} \;

# فحص الصلاحيات
sudo find /var/www -type f -perm -o+w
```

## استكشاف الأخطاء

### مشاكل شائعة

1. **خطأ في قاعدة البيانات**
   - تأكد من صحة بيانات الاتصال
   - تحقق من حالة خدمة PostgreSQL

2. **خطأ في الملفات الثابتة**
   - تشغيل `python manage.py collectstatic`
   - التحقق من صلاحيات المجلد

3. **خطأ في Nginx**
   - فحص إعدادات Nginx: `sudo nginx -t`
   - مراجعة السجلات: `sudo tail -f /var/log/nginx/error.log`

4. **خطأ في Gunicorn**
   - فحص حالة الخدمة: `sudo systemctl status fitness_project`
   - مراجعة السجلات: `sudo journalctl -u fitness_project`

### أوامر مفيدة
```bash
# فحص استخدام الذاكرة
free -h

# فحص استخدام القرص
df -h

# فحص العمليات
ps aux | grep gunicorn

# فحص المنافذ المفتوحة
sudo netstat -tlnp
```

## الدعم

للمساعدة والدعم التقني، يرجى التواصل مع فريق التطوير. 