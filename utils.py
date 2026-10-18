import os
import uuid
from werkzeug.utils import secure_filename

def get_file_extension(filename):
    if '.' in filename:
        return filename.rsplit('.', 1)[1].lower()
    return ''

def detect_file_type(extension):
    ext = extension.lower()
    
    types = {
        'image': ['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg', 'bmp'],
        'pdf': ['pdf'],
        'video': ['mp4', 'webm', 'ogg', 'mov', 'mkv'],
        'audio': ['mp3', 'wav', 'ogg', 'm4a', 'flac'],
        'data': ['csv', 'json', 'tsv', 'xlsx', 'xls', 'parquet', 'xml'],
        'code': ['py', 'js', 'html', 'css', 'c', 'cpp', 'rs', 'go', 'java', 'sql', 'r', 'ipynb'],
        'document': ['doc', 'docx', 'ppt', 'pptx', 'odt', 'txt', 'md', 'rtf'],
        'archive': ['zip', 'tar', 'gz', '7z', 'rar']
    }

    for f_type, exts in types.items():
        if ext in exts:
            return f_type
    return 'document'

def is_safe_file(filename, disallowed_extensions):
    ext = get_file_extension(filename)
    if ext in disallowed_extensions:
        return False
    return True

def save_uploaded_file(file_storage, upload_folder, disallowed_extensions):
    """
    Dosyayı güvenli bir şekilde diskteki hafıza klasörüne kaydeder.
    Geriye meta verileri döner.
    """
    os.makedirs(upload_folder, exist_ok=True)
    
    orig_name = secure_filename(file_storage.filename) or "adsiz_dosya"
    ext = get_file_extension(orig_name)
    
    if not is_safe_file(orig_name, disallowed_extensions):
        raise ValueError(f"'{ext}' uzantılı dosyalar güvenlik nedeniyle yüklenemez.")

    # Çakışmaları önlemek için UUID öneki
    unique_prefix = uuid.uuid4().hex[:10]
    stored_filename = f"{unique_prefix}_{orig_name}"
    target_path = os.path.join(upload_folder, stored_filename)

    file_storage.save(target_path)
    file_size = os.path.getsize(target_path)
    file_type = detect_file_type(ext)

    return {
        'stored_filename': stored_filename,
        'original_name': orig_name,
        'file_type': file_type,
        'file_extension': f".{ext}" if ext else "",
        'file_size': file_size
    }

def remove_file(filename, upload_folder):
    """Post silindiğinde diski temizler."""
    if not filename:
        return
    try:
        path = os.path.join(upload_folder, filename)
        if os.path.exists(path):
            os.remove(path)
    except Exception as e:
        print(f"Dosya silinirken hata: {e}")
