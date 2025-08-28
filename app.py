from flask import Flask, render_template, request, jsonify, send_from_directory
import requests
import base64
import os
import uuid
from datetime import datetime
import json
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from werkzeug.utils import secure_filename
import io

app = Flask(__name__)

# Configuration
API_BASE_URL = "https://api.infip.pro"
API_KEY = "infip-22a92ff3"
MEDIA_FOLDER = "media"

# AWS S3 Configuration
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_REGION = os.environ.get('AWS_REGION', 'us-east-1')
S3_BUCKET_NAME = os.environ.get('S3_BUCKET_NAME')
USE_S3 = os.environ.get('USE_S3', 'false').lower() == 'true'

# Ensure media folder exists for local storage
os.makedirs(MEDIA_FOLDER, exist_ok=True)

# Initialize S3 client if credentials are available
s3_client = None
if USE_S3 and AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY and S3_BUCKET_NAME:
    try:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=AWS_REGION
        )
        print(f"S3 client initialized. Using bucket: {S3_BUCKET_NAME}")
        print(f"S3 URL format: https://{S3_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/images/")
    except Exception as e:
        print(f"Failed to initialize S3 client: {str(e)}")
        s3_client = None
        USE_S3 = False
else:
    print("Using local storage (S3 not configured)")
    USE_S3 = False

def upload_to_s3(file_data, filename, content_type='image/png'):
    """Upload file data to S3 bucket with public read access"""
    if not s3_client or not S3_BUCKET_NAME:
        return None
    
    try:
        # Upload without ACL (rely on bucket policy for public access)
        s3_client.put_object(
            Bucket=S3_BUCKET_NAME,
            Key=f"images/{filename}",
            Body=file_data,
            ContentType=content_type
        )
        
        # Return the public URL
        s3_url = f"https://{S3_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/images/{filename}"
        print(f"Image uploaded to S3: {s3_url}")
        return s3_url
    except Exception as e:
        print(f"Error uploading to S3: {str(e)}")
        return None

def list_s3_images():
    """List all images from S3 bucket"""
    if not s3_client or not S3_BUCKET_NAME:
        return []
    
    try:
        response = s3_client.list_objects_v2(
            Bucket=S3_BUCKET_NAME,
            Prefix='images/'
        )
        
        images = []
        for obj in response.get('Contents', []):
            filename = obj['Key'].replace('images/', '')
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                images.append({
                    'filename': filename,
                    'url': f"https://{S3_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/images/{filename}",
                    'timestamp': obj['LastModified'].strftime("%Y-%m-%d %H:%M:%S"),
                    'size': obj['Size']
                })
        
        # Sort by modification time (newest first)
        images.sort(key=lambda x: x['timestamp'], reverse=True)
        return images
    except Exception as e:
        print(f"Error listing S3 images: {str(e)}")
        return []

def get_available_models():
    """Fetch available models from the API"""
    try:
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }
        response = requests.get(f"{API_BASE_URL}/v1/models", headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error fetching models: {response.status_code} - {response.text}")
            return {"data": []}
    except Exception as e:
        print(f"Error fetching models: {str(e)}")
        return {"data": []}

def generate_image(prompt, model_id, size="1024x1024", quality="standard", n=1):
    """Generate image using the Infip API"""
    try:
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model_id,
            "prompt": prompt,
            "size": size,
            "quality": quality,
            "n": n
        }
        
        response = requests.post(f"{API_BASE_URL}/v1/images/generations", 
                               headers=headers, 
                               json=payload)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error generating image: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Error generating image: {str(e)}")
        return None

def save_image_from_url(image_url, filename):
    """Download and save image from URL (local or S3)"""
    try:
        response = requests.get(image_url)
        if response.status_code == 200:
            if USE_S3:
                # Upload to S3
                s3_url = upload_to_s3(response.content, filename)
                if s3_url:
                    return s3_url
                else:
                    # Fallback to local storage if S3 fails
                    print("S3 upload failed, falling back to local storage")
            
            # Save locally
            filepath = os.path.join(MEDIA_FOLDER, filename)
            with open(filepath, 'wb') as f:
                f.write(response.content)
            return f'/media/{filename}'
        return None
    except Exception as e:
        print(f"Error saving image: {str(e)}")
        return None

def save_base64_image(base64_data, filename):
    """Save base64 encoded image (local or S3)"""
    try:
        # Remove data URL prefix if present
        if base64_data.startswith('data:image'):
            base64_data = base64_data.split(',')[1]
        
        image_data = base64.b64decode(base64_data)
        
        if USE_S3:
            # Upload to S3
            s3_url = upload_to_s3(image_data, filename)
            if s3_url:
                return s3_url
            else:
                # Fallback to local storage if S3 fails
                print("S3 upload failed, falling back to local storage")
        
        # Save locally
        filepath = os.path.join(MEDIA_FOLDER, filename)
        with open(filepath, 'wb') as f:
            f.write(image_data)
        return f'/media/{filename}'
    except Exception as e:
        print(f"Error saving base64 image: {str(e)}")
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/models')
def api_models():
    """API endpoint to get available models"""
    models = get_available_models()
    return jsonify(models)

@app.route('/api/generate', methods=['POST'])
def api_generate():
    """API endpoint to generate images"""
    try:
        data = request.get_json()
        prompt = data.get('prompt', '')
        model_id = data.get('model', 'img3')
        size = data.get('size', '1024x1024')
        quality = data.get('quality', 'standard')
        
        if not prompt:
            return jsonify({'error': 'Prompt is required'}), 400
        
        # Generate image
        result = generate_image(prompt, model_id, size, quality)
        
        if not result:
            return jsonify({'error': 'Failed to generate image'}), 500
        
        # Save images
        saved_images = []
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        for i, image_data in enumerate(result.get('data', [])):
            filename = f"{timestamp}_{uuid.uuid4().hex[:8]}_{i+1}.png"
            
            # Check if image is URL or base64
            if 'url' in image_data:
                image_url = save_image_from_url(image_data['url'], filename)
            elif 'b64_json' in image_data:
                image_url = save_base64_image(image_data['b64_json'], filename)
            else:
                continue
            
            if image_url:
                saved_images.append({
                    'filename': filename,
                    'url': image_url,
                    'prompt': prompt,
                    'model': model_id,
                    'timestamp': timestamp,
                    'storage': 'S3' if USE_S3 and image_url.startswith('https://') else 'Local'
                })
        
        return jsonify({
            'success': True,
            'images': saved_images,
            'message': f'Generated {len(saved_images)} image(s) successfully!'
        })
        
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/media/<filename>')
def serve_media(filename):
    """Serve media files"""
    return send_from_directory(MEDIA_FOLDER, filename)

@app.route('/gallery')
def gallery():
    """Display gallery of generated images"""
    try:
        images = []
        
        if USE_S3:
            # Get images from S3
            images = list_s3_images()
        else:
            # Get images from local storage
            if os.path.exists(MEDIA_FOLDER):
                for filename in os.listdir(MEDIA_FOLDER):
                    if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                        filepath = os.path.join(MEDIA_FOLDER, filename)
                        stat = os.stat(filepath)
                        images.append({
                            'filename': filename,
                            'url': f'/media/{filename}',
                            'timestamp': datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
                            'size': stat.st_size
                        })
            
            # Sort by modification time (newest first)
            images.sort(key=lambda x: x['timestamp'], reverse=True)
        
        storage_info = {
            'storage_type': 'AWS S3' if USE_S3 else 'Local Storage',
            'bucket_name': S3_BUCKET_NAME if USE_S3 else None,
            'total_images': len(images)
        }
        
        return render_template('gallery.html', images=images, storage_info=storage_info)
    except Exception as e:
        storage_info = {
            'storage_type': 'AWS S3' if USE_S3 else 'Local Storage',
            'bucket_name': S3_BUCKET_NAME if USE_S3 else None,
            'total_images': 0
        }
        return render_template('gallery.html', images=[], storage_info=storage_info, error=str(e))

@app.route('/api/storage-info')
def api_storage_info():
    """API endpoint to get storage information"""
    return jsonify({
        'storage_type': 'AWS S3' if USE_S3 else 'Local Storage',
        'bucket_name': S3_BUCKET_NAME if USE_S3 else None,
        'region': AWS_REGION if USE_S3 else None,
        's3_configured': bool(s3_client),
        'use_s3': USE_S3
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
