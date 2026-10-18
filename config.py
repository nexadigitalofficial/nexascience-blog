import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    # Güvenlik Anahtarı (Ortam değişkeninden veya varsayılan)
    SECRET_KEY = os.environ.get('SECRET_KEY', 'nexascience-super-secret-key-2026')

    # Veritabanı (Varsayılan: SQLite, cPanel veya VPS'te tek tıkla MySQL'e çevrilebilir)
    # Örnek MySQL: mysql+pymysql://kullanici:sifre@localhost/nexascience_db
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL', 
        f'sqlite:///{os.path.join(BASE_DIR, "nexascience.db")}'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Dosya Yükleme / Hafıza Ayarları
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
    
    # Maksimum Yükleme Boyutu: 100 MB (İhtiyaca göre artırılabilir)
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024

    # Güvenlik: Çalıştırılabilir ve riskli uzantıları engelle
    DISALLOWED_EXTENSIONS = {'exe', 'php', 'sh', 'bat', 'cmd', 'cgi', 'pl'}

    # Admin Paneli Giriş Şifresi
    ADMIN_USERNAME = os.environ.get('ADMIN_USER', 'admin')
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASS', 'nexascience123')
