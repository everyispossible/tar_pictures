from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from PIL import Image
import io
import os
import uuid

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
COMPRESSED_FOLDER = 'compressed'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(COMPRESSED_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/api/compress', methods=['POST'])
def compress_image():
    if 'image' not in request.files:
        return jsonify({'error': '没有上传图片'}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': '没有选择文件'}), 400
    
    quality = request.form.get('quality', 80, type=int)
    format_type = request.form.get('format', 'original')
    
    try:
        # 先读取文件内容到内存
        file_content = file.read()
        original_size = len(file_content)
        # 重置文件指针
        file.stream.seek(0)
        # 从内存中创建图像对象
        image = Image.open(io.BytesIO(file_content))
        original_format = image.format
        
        output = io.BytesIO()
        
        if format_type == 'jpeg' or (format_type == 'original' and original_format in ['JPEG', 'JPG']):
            if image.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', image.size, (255, 255, 255))
                background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                image = background
            image.save(output, format='JPEG', quality=quality, optimize=True)
            mime_type = 'image/jpeg'
        elif format_type == 'png' or (format_type == 'original' and original_format == 'PNG'):
            image.save(output, format='PNG', optimize=True)
            mime_type = 'image/png'
        elif format_type == 'webp':
            image.save(output, format='WEBP', quality=quality, method=6)
            mime_type = 'image/webp'
        else:
            image.save(output, format=original_format, quality=quality, optimize=True)
            mime_type = f'image/{original_format.lower()}'
        
        output.seek(0, io.SEEK_END)
        compressed_size = output.tell()
        output.seek(0)
        output.seek(0)
        
        compression_ratio = ((original_size - compressed_size) / original_size) * 100
        
        file_id = str(uuid.uuid4())
        
        return send_file(
            output,
            mimetype=mime_type,
            as_attachment=True,
            download_name=f'compressed_{file.filename}'
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/compress/info', methods=['POST'])
def compress_image_info():
    if 'image' not in request.files:
        return jsonify({'error': '没有上传图片'}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': '没有选择文件'}), 400
    
    quality = request.form.get('quality', 80, type=int)
    format_type = request.form.get('format', 'original')
    
    try:
        # 先读取文件内容到内存
        file_content = file.read()
        original_size = len(file_content)
        # 重置文件指针
        file.stream.seek(0)
        # 从内存中创建图像对象
        image = Image.open(io.BytesIO(file_content))
        original_format = image.format
        original_width, original_height = image.size
        
        output = io.BytesIO()
        
        if format_type == 'jpeg' or (format_type == 'original' and original_format in ['JPEG', 'JPG']):
            if image.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', image.size, (255, 255, 255))
                background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                image = background
            image.save(output, format='JPEG', quality=quality, optimize=True)
            mime_type = 'image/jpeg'
        elif format_type == 'png' or (format_type == 'original' and original_format == 'PNG'):
            image.save(output, format='PNG', optimize=True)
            mime_type = 'image/png'
        elif format_type == 'webp':
            image.save(output, format='WEBP', quality=quality, method=6)
            mime_type = 'image/webp'
        else:
            image.save(output, format=original_format, quality=quality, optimize=True)
            mime_type = f'image/{original_format.lower()}'
        
        output.seek(0, io.SEEK_END)
        compressed_size = output.tell()
        output.seek(0)
        
        compression_ratio = ((original_size - compressed_size) / original_size) * 100 if original_size > 0 else 0
        
        import base64
        preview_base64 = base64.b64encode(output.getvalue()).decode('utf-8')
        
        return jsonify({
            'success': True,
            'original_size': original_size,
            'compressed_size': compressed_size,
            'compression_ratio': round(compression_ratio, 2),
            'original_width': original_width,
            'original_height': original_height,
            'preview': f'data:{mime_type};base64,{preview_base64}'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
