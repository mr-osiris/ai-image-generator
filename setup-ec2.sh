#!/bin/bash

# Simple EC2 Setup Script for AI Image Generator
# Run this script on your EC2 instance after cloning from GitHub

echo "🚀 Setting up AI Image Generator on EC2..."

# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3 and pip
sudo apt install -y python3 python3-pip python3-venv git nginx

# Create application directory
sudo mkdir -p /var/www/ai-image-generator
sudo chown $USER:$USER /var/www/ai-image-generator
cd /var/www/ai-image-generator

# Clone from GitHub
echo "📥 Setting up GitHub repository..."
echo "Please provide your GitHub repository details:"
read -p "Enter your GitHub username: " GITHUB_USER
read -p "Enter repository name (default: ai-image-generator): " REPO_NAME
REPO_NAME=${REPO_NAME:-ai-image-generator}

echo "📥 Cloning repository from GitHub..."
git clone https://github.com/$GITHUB_USER/$REPO_NAME.git .

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Create environment file
echo "🔧 Creating environment configuration..."
echo "Please provide your AWS and API configuration:"

read -p "Enter your AWS Access Key ID: " AWS_KEY
read -p "Enter your AWS Secret Access Key: " AWS_SECRET
read -p "Enter your S3 Bucket Name: " S3_BUCKET
read -p "Enter AWS Region (default: us-east-1): " AWS_REGION
AWS_REGION=${AWS_REGION:-us-east-1}

echo "Creating .env file..."
cat > .env << EOF
# S3 Configuration
USE_S3=true
AWS_ACCESS_KEY_ID=$AWS_KEY
AWS_SECRET_ACCESS_KEY=$AWS_SECRET
AWS_REGION=$AWS_REGION
S3_BUCKET_NAME=$S3_BUCKET

# API Configuration
API_BASE_URL=https://api.infip.pro
API_KEY=infip-22a92ff3
EOF

echo "⚠️  IMPORTANT: Edit .env file with your AWS credentials!"
echo "   nano .env"

# Create systemd service
echo "🔧 Creating systemd service..."
sudo tee /etc/systemd/system/ai-image-generator.service > /dev/null << EOF
[Unit]
Description=AI Image Generator Flask App
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=/var/www/ai-image-generator
Environment=PATH=/var/www/ai-image-generator/venv/bin
EnvironmentFile=/var/www/ai-image-generator/.env
ExecStart=/var/www/ai-image-generator/venv/bin/gunicorn --bind 127.0.0.1:5000 --workers 4 app:app
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Create nginx configuration
echo "🔧 Creating nginx configuration..."
sudo tee /etc/nginx/sites-available/ai-image-generator > /dev/null << EOF
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /static {
        alias /var/www/ai-image-generator/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    location /media {
        alias /var/www/ai-image-generator/media;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
EOF

# Enable nginx site
sudo ln -sf /etc/nginx/sites-available/ai-image-generator /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Test nginx configuration
sudo nginx -t

# Enable and start services
sudo systemctl enable ai-image-generator
sudo systemctl enable nginx

echo "✅ Setup completed!"
echo ""
echo "📋 Next Steps:"
echo "1. Edit environment file: nano .env"
echo "2. Add your AWS credentials and S3 bucket name"
echo "3. Start the services:"
echo "   sudo systemctl start ai-image-generator"
echo "   sudo systemctl start nginx"
echo ""
echo "4. Check status:"
echo "   sudo systemctl status ai-image-generator"
echo "   sudo systemctl status nginx"
echo ""
echo "5. View logs:"
echo "   sudo journalctl -u ai-image-generator -f"
echo ""
echo "🌐 Your app will be available at: http://YOUR_EC2_PUBLIC_IP"
echo ""
echo "🔧 To update your app:"
echo "   cd /var/www/ai-image-generator"
echo "   git pull"
echo "   sudo systemctl restart ai-image-generator"
