# AI Image Generator - Simple EC2 Deployment

A stunning Flask web application that generates AI images using the Infip Pro API with AWS S3 storage.

## 🚀 Quick EC2 Deployment

### 1. Upload to GitHub
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/mihir0209/ai-image-generator.git
git push -u origin main
```

### 2. Setup S3 Bucket
Follow the guide in `S3_SETUP.md` to:
- Create S3 bucket
- Configure public read access
- Create IAM user and get access keys

### 3. Deploy to EC2
```bash
# SSH to your EC2 instance
ssh -i your-key.pem ubuntu@your-ec2-ip

# Run setup script
curl -sSL https://raw.githubusercontent.com/YOUR_USERNAME/ai-image-generator/main/setup-ec2.sh | bash

# Edit environment file
nano /var/www/ai-image-generator/.env

# Start services
sudo systemctl start ai-image-generator
sudo systemctl start nginx
```

### 4. Configure Environment
Edit `/var/www/ai-image-generator/.env`:
```bash
USE_S3=true
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=us-east-1
S3_BUCKET_NAME=your-bucket-name
```

## 📁 Project Structure

```
ai-image-generator/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── setup-ec2.sh          # EC2 setup script
├── S3_SETUP.md           # S3 configuration guide
├── templates/            # HTML templates
│   ├── index.html        # Main page
│   └── gallery.html      # Gallery page
├── static/               # CSS, JS, images
│   ├── css/style.css     # Styling
│   └── js/               # JavaScript files
└── media/                # Local image storage (fallback)
```

## ⚙️ Features

- 🎨 Beautiful responsive UI with animations
- 🤖 AI image generation using Infip Pro API
- ☁️ AWS S3 storage with public access
- 📱 Mobile-friendly gallery
- 🔄 Automatic fallback to local storage
- 📥 One-click image downloads

## 🔧 Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export USE_S3=false

# Run the application
python app.py
```

Visit `http://localhost:5000`

## 🌐 Production URLs

- **App**: `http://your-ec2-public-ip`
- **Gallery**: `http://your-ec2-public-ip/gallery`
- **API**: `http://your-ec2-public-ip/api/models`

## 🔍 Troubleshooting

### Check Service Status
```bash
sudo systemctl status ai-image-generator
sudo systemctl status nginx
```

### View Logs
```bash
sudo journalctl -u ai-image-generator -f
sudo tail -f /var/log/nginx/error.log
```

### Restart Services
```bash
sudo systemctl restart ai-image-generator
sudo systemctl restart nginx
```

### Test S3 Access
```bash
# Check if S3 is working
curl http://your-ec2-ip/api/storage-info
```

## 📋 EC2 Requirements

- **Instance Type**: t2.micro or larger
- **OS**: Ubuntu 20.04 LTS
- **Security Group**: 
  - HTTP (80) from 0.0.0.0/0
  - SSH (22) from your IP
- **Storage**: 8GB minimum

## 💰 Cost Estimate

- **EC2 t2.micro**: ~$8.50/month
- **S3 Storage**: ~$0.023/GB
- **Data Transfer**: ~$0.09/GB

**Total**: ~$10-15/month for moderate usage

## 🔄 Updates

```bash
cd /var/www/ai-image-generator
git pull
sudo systemctl restart ai-image-generator
```

## 📞 Support

If you encounter issues:
1. Check the logs
2. Verify S3 credentials
3. Test network connectivity
4. Check EC2 security groups

**Happy generating!** 🎨✨

https://chat.infip.pro/

this was also a part

