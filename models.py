from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy
import re

db = SQLAlchemy()

def utc_now():
    return datetime.now(timezone.utc)

def generate_slug(text):
    text = text.lower()
    # Türkçe karakter dönüşümü
    tr_map = {
        'ı': 'i', 'ğ': 'g', 'ü': 'u', 'ş': 's', 'ö': 'o', 'ç': 'c',
        'İ': 'i', 'Ğ': 'g', 'Ü': 'u', 'Ş': 's', 'Ö': 'o', 'Ç': 'c'
    }
    for tr_char, en_char in tr_map.items():
        text = text.replace(tr_char, en_char)
    # Alfanümerik haricindekileri tire yap
    text = re.sub(r'[^a-zA-Z0-9\s-]', '', text)
    text = re.sub(r'[\s-]+', '-', text).strip('-')
    return text or 'post'

class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False, unique=True)
    slug = db.Column(db.String(100), nullable=False, unique=True)
    color = db.Column(db.String(20), default='cyan')  # cyan, emerald, purple, blue, amber, rose
    created_at = db.Column(db.DateTime, default=utc_now)

    # İlişki
    posts = db.relationship('Post', backref='category', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Category {self.name}>'


class Post(db.Model):
    __tablename__ = 'posts'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(250), nullable=False, unique=True)
    summary = db.Column(db.Text, nullable=True)
    content = db.Column(db.Text, nullable=True)

    # Kategori İlişkisi
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)

    # Dosya / Hafıza Meta Verileri
    file_filename = db.Column(db.String(255), nullable=False)      # Sunucuda saklanan hash'li ad
    file_original_name = db.Column(db.String(255), nullable=False)  # Kullanıcının yüklediği ad
    file_type = db.Column(db.String(50), default='document')       # image, pdf, video, audio, data, code, doc
    file_extension = db.Column(db.String(20), default='')          # .pdf, .png vb.
    file_size = db.Column(db.BigInteger, default=0)                # Byte cinsinden

    # İstatistikler
    views = db.Column(db.Integer, default=0)
    downloads = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=utc_now)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)

    @property
    def formatted_size(self):
        size = self.file_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"

    @property
    def file_icon(self):
        icon_map = {
            'image': 'fa-regular fa-image',
            'pdf': 'fa-solid fa-file-pdf',
            'video': 'fa-solid fa-film',
            'audio': 'fa-solid fa-headphones',
            'data': 'fa-solid fa-chart-pie',
            'code': 'fa-solid fa-code',
            'document': 'fa-solid fa-file-lines',
            'archive': 'fa-solid fa-file-zipper'
        }
        return icon_map.get(self.file_type, 'fa-solid fa-file')

    def __repr__(self):
        return f'<Post {self.title}>'
