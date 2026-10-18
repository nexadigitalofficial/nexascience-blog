import os
from datetime import datetime
from functools import wraps
from flask import (
    Flask, render_template, request, redirect, url_for, 
    flash, session, send_from_directory, jsonify, abort
)
from config import Config
from models import db, Category, Post, generate_slug
from utils import save_uploaded_file, remove_file

app = Flask(__name__)
app.config.from_object(Config)

# Veritabanını başlat
db.init_app(app)

@app.context_processor
def inject_globals():
    return {'now': datetime.utcnow()}


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            flash('Bu sayfayı görüntülemek için giriş yapmalısınız.', 'warning')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

# Veritabanını oluştur ve varsayılan kategorileri ekle
def init_db():
    with app.app_context():
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        db.create_all()
        
        # Eğer hiç kategori yoksa bilimsel başlangıç kategorilerini oluştur
        if Category.query.count() == 0:
            default_categories = [
                ('Biyoteknoloji', 'emerald'),
                ('Yapay Zeka & Veri', 'cyan'),
                ('Genomik & Biyoinformatik', 'purple'),
                ('Kuantum & Fizik', 'blue'),
                ('Çevre & Enerji', 'amber'),
                ('Genel Bilim', 'rose')
            ]
            for name, color in default_categories:
                slug = generate_slug(name)
                db.session.add(Category(name=name, slug=slug, color=color))
            db.session.commit()

# ==========================================
# PUBLIC / BLOG ROTALARI
# ==========================================

@app.route('/')
def index():
    category_slug = request.args.get('kategori')
    search_query = request.args.get('q')

    query = Post.query

    active_category = None
    if category_slug:
        active_category = Category.query.filter_by(slug=category_slug).first()
        if active_category:
            query = query.filter_by(category_id=active_category.id)

    if search_query:
        search_fmt = f"%{search_query}%"
        query = query.filter(
            (Post.title.ilike(search_fmt)) | 
            (Post.summary.ilike(search_fmt)) |
            (Post.content.ilike(search_fmt)) |
            (Post.file_original_name.ilike(search_fmt))
        )

    posts = query.order_by(Post.created_at.desc()).all()
    categories = Category.query.order_by(Category.name.asc()).all()

    return render_template(
        'index.html', 
        posts=posts, 
        categories=categories, 
        active_category=active_category,
        search_query=search_query
    )


@app.route('/yazi/<slug>')
def post_detail(slug):
    post = Post.query.filter_by(slug=slug).first_or_404()
    
    # Görüntülenme sayısını artır
    post.views += 1
    db.session.commit()

    # İlgili kategorideki diğer yazılar
    related_posts = Post.query.filter(
        Post.category_id == post.category_id, 
        Post.id != post.id
    ).order_by(Post.created_at.desc()).limit(3).all()

    # Eğer metin/kod/csv dosyasıysa ve içeriği okumak istenirse
    preview_content = None
    if post.file_type in ['code', 'data', 'document'] and post.file_size < 100 * 1024:
        try:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], post.file_filename)
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    preview_content = f.read()
        except Exception:
            preview_content = None

    return render_template(
        'post_detail.html', 
        post=post, 
        related_posts=related_posts,
        preview_content=preview_content
    )


@app.route('/indir/<int:post_id>')
def download_file(post_id):
    post = db.get_or_404(Post, post_id)
    post.downloads += 1
    db.session.commit()
    return send_from_directory(
        app.config['UPLOAD_FOLDER'],
        post.file_filename,
        as_attachment=True,
        download_name=post.file_original_name
    )


# ==========================================
# ADMIN PANELİ ROTALARI
# ==========================================

@app.route('/admin/giris', methods=['GET', 'POST'])
def admin_login():
    if session.get('admin_logged_in'):
        return redirect(url_for('admin_dashboard'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if (username == app.config['ADMIN_USERNAME'] and 
            password == app.config['ADMIN_PASSWORD']):
            session['admin_logged_in'] = True
            flash('Yönetim paneline başarıyla giriş yaptınız.', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Hatalı kullanıcı adı veya şifre!', 'danger')

    return render_template('admin/login.html')


@app.route('/admin/cikis')
def admin_logout():
    session.pop('admin_logged_in', None)
    flash('Güvenli çıkış yapıldı.', 'info')
    return redirect(url_for('admin_login'))


@app.route('/admin')
@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    posts = Post.query.order_by(Post.created_at.desc()).all()
    categories = Category.query.all()

    # Toplam kullanılan disk hafızası hesabı
    total_storage_bytes = sum(p.file_size for p in posts)
    
    # Boyut biçimlendirme
    size = total_storage_bytes
    formatted_total_size = "0 B"
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024.0:
            formatted_total_size = f"{size:.1f} {unit}"
            break
        size /= 1024.0

    stats = {
        'total_posts': len(posts),
        'total_categories': len(categories),
        'total_storage': formatted_total_size,
        'total_views': sum(p.views for p in posts),
        'total_downloads': sum(p.downloads for p in posts)
    }

    return render_template('admin/dashboard.html', posts=posts, categories=categories, stats=stats)


@app.route('/admin/yeni-yazi', methods=['GET', 'POST'])
@admin_required
def admin_new_post():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        category_id = request.form.get('category_id')
        summary = request.form.get('summary', '').strip()
        content = request.form.get('content', '').strip()
        file = request.files.get('file')

        if not title:
            flash('Lütfen bir başlık girin.', 'danger')
            return redirect(request.url)

        if not category_id:
            flash('Lütfen bir kategori seçin.', 'danger')
            return redirect(request.url)

        if not file or not file.filename:
            flash('Lütfen blogda sunulacak dosyayı yükleyin (sürükleyip bırakabilir veya seçebilirsiniz).', 'danger')
            return redirect(request.url)

        try:
            # Dosyayı diske / hafızaya kaydet
            meta = save_uploaded_file(
                file_storage=file,
                upload_folder=app.config['UPLOAD_FOLDER'],
                disallowed_extensions=app.config['DISALLOWED_EXTENSIONS']
            )

            # Benzersiz slug oluştur
            base_slug = generate_slug(title)
            slug = base_slug
            counter = 1
            while Post.query.filter_by(slug=slug).first():
                slug = f"{base_slug}-{counter}"
                counter += 1

            post = Post(
                title=title,
                slug=slug,
                summary=summary,
                content=content,
                category_id=int(category_id),
                file_filename=meta['stored_filename'],
                file_original_name=meta['original_name'],
                file_type=meta['file_type'],
                file_extension=meta['file_extension'],
                file_size=meta['file_size']
            )

            db.session.add(post)
            db.session.commit()

            flash(f"'{title}' başarıyla yayınlandı ve dosya hafızaya kaydedildi!", 'success')
            return redirect(url_for('admin_dashboard'))

        except Exception as e:
            flash(f"Hata oluştu: {str(e)}", 'danger')
            return redirect(request.url)

    categories = Category.query.order_by(Category.name.asc()).all()
    return render_template('admin/new_post.html', categories=categories)


@app.route('/admin/kategori/ekle', methods=['POST'])
@admin_required
def admin_add_category():
    name = request.form.get('name', '').strip()
    color = request.form.get('color', 'cyan')

    if not name:
        return jsonify({'success': False, 'message': 'Kategori adı boş olamaz.'}), 400

    slug = generate_slug(name)
    existing = Category.query.filter((Category.name == name) | (Category.slug == slug)).first()
    if existing:
        return jsonify({'success': False, 'message': 'Bu kategori zaten mevcut.'}), 400

    cat = Category(name=name, slug=slug, color=color)
    db.session.add(cat)
    db.session.commit()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.is_json:
        return jsonify({
            'success': True,
            'category': {
                'id': cat.id,
                'name': cat.name,
                'slug': cat.slug,
                'color': cat.color
            }
        })

    flash(f"'{name}' kategorisi oluşturuldu.", 'success')
    return redirect(url_for('admin_dashboard'))


@app.route('/admin/sil/<int:post_id>', methods=['POST'])
@admin_required
def admin_delete_post(post_id):
    post = db.get_or_404(Post, post_id)
    # Fiziksel dosyayı diskten temizle
    remove_file(post.file_filename, app.config['UPLOAD_FOLDER'])
    
    db.session.delete(post)
    db.session.commit()
    flash(f"'{post.title}' ve ilişkili dosya diskten tamamen silindi.", 'info')
    return redirect(url_for('admin_dashboard'))


# ==========================================
# UYGULAMA BAŞLATICI
# ==========================================

init_db()

if __name__ == '__main__':
    # Local test çalıştırması
    app.run(debug=True, host='127.0.0.1', port=5000)
