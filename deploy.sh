#!/bin/bash

# Deployment script for Fitness Project
# Usage: ./deploy.sh

set -e

echo "🚀 Starting deployment..."

# Update system
echo "📦 Updating system packages..."
sudo apt update
sudo apt upgrade -y

# Install required packages
echo "🔧 Installing required packages..."
sudo apt install -y python3 python3-pip python3-venv nginx postgresql postgresql-contrib

# Create project directory
echo "📁 Setting up project directory..."
sudo mkdir -p /var/www/fitness_project
sudo chown $USER:$USER /var/www/fitness_project

# Copy project files (assuming you're in the project directory)
echo "📋 Copying project files..."
cp -r . /var/www/fitness_project/

# Create virtual environment
echo "🐍 Creating virtual environment..."
cd /var/www/fitness_project
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo "📚 Installing Python dependencies..."
pip install -r requirements.txt
pip install gunicorn psycopg2-binary

# Set up environment variables
echo "🔐 Setting up environment variables..."
cat > .env << EOF
SECRET_KEY=$(python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')
DEBUG=False
DB_NAME=fitness_project
DB_USER=fitness_user
DB_PASSWORD=$(openssl rand -base64 32)
DB_HOST=localhost
DB_PORT=5432
EOF

# Set up PostgreSQL
echo "🗄️ Setting up PostgreSQL..."
sudo -u postgres psql << EOF
CREATE DATABASE fitness_project;
CREATE USER fitness_user WITH PASSWORD '$(grep DB_PASSWORD .env | cut -d '=' -f2)';
GRANT ALL PRIVILEGES ON DATABASE fitness_project TO fitness_user;
EOF

# Run migrations
echo "🔄 Running database migrations..."
python manage.py makemigrations
python manage.py migrate

# Create superuser
echo "👤 Creating superuser..."
python manage.py createsuperuser --noinput --username admin --email admin@example.com

# Collect static files
echo "📦 Collecting static files..."
python manage.py collectstatic --noinput

# Set up systemd service
echo "⚙️ Setting up systemd service..."
sudo cp fitness_project.service /etc/systemd/system/
sudo cp fitness_project.socket /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable fitness_project.socket
sudo systemctl enable fitness_project.service

# Set up Nginx
echo "🌐 Setting up Nginx..."
sudo cp nginx_fitness_project /etc/nginx/sites-available/fitness_project
sudo ln -sf /etc/nginx/sites-available/fitness_project /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Test Nginx configuration
sudo nginx -t

# Set permissions
echo "🔒 Setting permissions..."
sudo chown -R www-data:www-data /var/www/fitness_project
sudo chmod -R 755 /var/www/fitness_project

# Start services
echo "🚀 Starting services..."
sudo systemctl start fitness_project.socket
sudo systemctl start fitness_project.service
sudo systemctl restart nginx

# Set up SSL (optional)
echo "🔒 Setting up SSL certificate..."
read -p "Do you want to set up SSL certificate with Let's Encrypt? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    sudo apt install -y certbot python3-certbot-nginx
    read -p "Enter your domain name: " domain_name
    sudo certbot --nginx -d $domain_name
fi

echo "✅ Deployment completed successfully!"
echo "🌐 Your application should be available at: http://$(hostname -I | awk '{print $1}')"
echo "📊 Check service status with: sudo systemctl status fitness_project"
echo "📝 Check logs with: sudo journalctl -u fitness_project" 