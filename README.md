# NexaScience - Bilimsel Blog & Dosya Sunum Platformu

NexaScience; yüklenen herhangi bir araştırma dosyasını (PDF, Görsel, Veri Seti, Kod, Video, Ses vb.) kategorilendirerek dinamik olarak blog sayfasında sunan, **Python tabanlı, hafif, güvenli ve tüm hosting ortamlarına (cPanel, Plesk, VPS, Docker) tam uyumlu** modern bir web platformudur.

---

## 🌟 Temel Özellikler

1. **Sürükle & Bırak (Drag & Drop) Kolay Kullanım:**
   - Admin panelinde dosyayı doğrudan sürükleyip bırakarak hafızaya alma.
   - Anlık dosya adı, boyutu, formatı ve görsel önizlemesi.
   - Maksimum 100 MB dosya yükleme desteği (isteğe göre `config.py` üzerinden artırılabilir).

2. **Dinamik Kategori Sistemi:**
   - Dosya yüklenirken kategori seçimi (Biyoteknoloji, Yapay Zeka & Veri, Genomik, Kuantum vb.).
   - Panelden çıkmadan tek tıkla yeni kategori ekleme (AJAX destekli).
   - Blog ana sayfasında kategoriye özel renkli etiket rozetleri (`#Biyoteknoloji`, `#YapayZeka` vb.) ve tek tıkla kategoriye göre filtreleme.

3. **Akıllı Dosya Sunumu (Smart File Presentation):**
   - **Görseller (PNG, JPG, WebP, SVG):** Yüksek çözünürlüklü duyarlı görüntüleyici.
   - **PDF Belgeleri:** Sayfa içinde doğrudan gömülü PDF okuyucu (iframe) + yeni sekmede açma + doğrudan indirme.
   - **Veri & Kod (CSV, JSON, Python, Metin):** Sözdizimi vurgulamalı kod kutusunda anında önizleme.
   - **Video & Ses (MP4, MP3 vb.):** Dahili HTML5 medya oynatıcı.
   - **Arşiv & Diğer Dosyalar:** Dosya boyutu, formatı ve tek tıkla indirme kartı.

4. **Hafıza & Depolama Mimarisi (Storage & Memory):**
   - **Veritabanı Katmanı:** SQLAlchemy ORM (Varsayılan: Sıfır kurulumlu SQLite, hostingde tek tıkla MySQL'e çevrilebilir).
   - **Dosya Depolama:** Güvenli isim hash'leme (UUID) ve `static/uploads/` dizininde kategorize disk hafızası.
   - **Güvenlik:** `.php`, `.exe`, `.sh` gibi çalıştırılabilir zararlı uzantıların yüklenmesini engelleyen beyaz liste doğrulaması.
   - **Disk Temizliği:** Admin panelinden bir yazı silindiğinde ilişkili dosya diskten de otomatik silinir, hafızada çöp dosya kalmaz.

---

## 🚀 Yerel Olarak Çalıştırma (Local Development)

```bash
# 1. Bağımlılıkları yükleyin
pip install -r requirements.txt

# 2. Uygulamayı başlatın
python app.py
```

Tarayıcınızda açın:
* **Blog Ana Sayfası:** `http://127.0.0.1:5000`
* **Admin Paneli:** `http://127.0.0.1:5000/admin/giris`
  * **Varsayılan Kullanıcı Adı:** `admin`
  * **Varsayılan Şifre:** `nexascience123` *(config.py üzerinden değiştirilebilir)*

---

## 🌐 Hosting Kurulum Rehberi (cPanel & Shared Hosting)

cPanel'de Python destekli paylaşımlı hostinglerde (CloudLinux Phusion Passenger) çalıştırmak için proje hazır yapılandırılmıştır:

1. **Dosyaları Yükleyin:**
   - NexaScience klasöründeki dosyaları hostingdeki dosya yöneticisi ile sitenizin dizinine yükleyin.
2. **cPanel "Setup Python App" Menüsüne Girin:**
   - **Python Version:** `3.10` veya `3.11` seçin.
   - **Application Root:** Projenizin yüklendiği klasör yolu (örn: `nexascience`).
   - **Application URL:** Sitenizin adresi (örn: `blog.nexascience.com` veya `nexascience.com`).
   - **Application Startup File:** `passenger_wsgi.py`
   - **Application Entry Point:** `application`
3. **Bağımlılıkları Kurun:**
   - "Configuration files" alanına `requirements.txt` dosyasını belirtip **Run Pip Install** butonuna tıklayın.
4. **Hazır!** Siteniz artık yayında.

---

## 📁 Proje Dosya Yapısı

```
nexascience/
├── app.py                  # Ana uygulama rotaları (Blog, Admin, API)
├── config.py               # Yapılandırma, hafıza limitleri ve şifreler
├── models.py               # Kategori ve Post veritabanı modelleri
├── utils.py                # Sürükle-bırak dosya işleme ve güvenlik filtreleri
├── passenger_wsgi.py       # cPanel / Shared hosting WSGI adaptörü
├── requirements.txt        # Hafif ve kararlı Python bağımlılıkları
├── static/
│   ├── css/
│   │   └── style.css       # Bilimsel tema ve özel stiller
│   └── uploads/            # Hafızaya alınan fiziksel dosyalar
└── templates/
    ├── base.html           # Ortak tema ve gezinti çubuğu
    ├── index.html          # Blog ana sayfası (kategori filtreli, arama özellikli)
    ├── post_detail.html    # Akıllı dosya sunum sayfası (PDF/Görsel/Medya)
    └── admin/
        ├── login.html      # Admin giriş sayfası
        ├── dashboard.html  # İstatistikler, disk hafızası ve içerik tablosu
        └── new_post.html   # Sürükle-bırak yükleme ve kategori seçim sayfası
```
