#!/bin/bash

# ==========================================
# NAMECHEAP SHARED HOSTING DEPLOYMENT SCRIPT
# ==========================================
# Bu script SSH/Terminal erişimi olan Namecheap shared hosting için hazırlanmıştır
# cPanel Terminal'den çalıştırabilirsiniz

set -e  # Exit on error

echo "=========================================="
echo "Güvenilir Analiz - Namecheap Deployment"
echo "=========================================="

# ==========================================
# 1. ENVIRONMENT CHECK
# ==========================================
echo ""
echo "1️⃣  Environment kontrol ediliyor..."

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | grep -oP '\d+\.\d+')
echo "✓ Python version: $PYTHON_VERSION"

if (( $(echo "$PYTHON_VERSION < 3.8" | bc -l) )); then
    echo "❌ Hata: Python 3.8+ gerekli. cPanel → Python Selector'dan yükseltin."
    exit 1
fi

# Check current directory
if [[ ! -d "app" ]]; then
    echo "❌ Hata: 'app' klasörü bulunamadı. Lütfen public_html dizininde olduğunuzdan emin olun."
    echo "Konum: cd ~/public_html"
    exit 1
fi

# ==========================================
# 2. BACKUP EXISTING FILES
# ==========================================
echo ""
echo "2️⃣  Mevcut dosyalar yedekleniyor..."

BACKUP_DIR="backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

if [[ -f ".env" ]]; then
    cp .env "$BACKUP_DIR/.env"
    echo "✓ .env yedeklendi"
fi

if [[ -d "venv" ]]; then
    echo "⚠️  Mevcut virtual environment bulundu - yeniden oluşturulacak"
    rm -rf venv
fi

# ==========================================
# 3. VIRTUAL ENVIRONMENT
# ==========================================
echo ""
echo "3️⃣  Virtual environment oluşturuluyor..."

python3 -m venv venv
echo "✓ Virtual environment oluşturuldu"

source venv/bin/activate
echo "✓ Virtual environment aktif"

# ==========================================
# 4. UPGRADE PIP
# ==========================================
echo ""
echo "4️⃣  pip güncelleniyor..."

pip install --upgrade pip setuptools wheel
echo "✓ pip güncellendi"

# ==========================================
# 5. INSTALL DEPENDENCIES
# ==========================================
echo ""
echo "5️⃣  Dependencies yükleniyor..."
echo "⏳ Bu işlem 5-10 dakika sürebilir..."

if [[ -f "requirements-shared-hosting.txt" ]]; then
    pip install --no-cache-dir -r requirements-shared-hosting.txt
    echo "✓ Shared hosting dependencies yüklendi"
elif [[ -f "app/requirements.txt" ]]; then
    echo "⚠️  requirements-shared-hosting.txt bulunamadı, app/requirements.txt kullanılıyor"
    pip install --no-cache-dir -r app/requirements.txt
else
    echo "❌ Hata: requirements dosyası bulunamadı"
    exit 1
fi

# ==========================================
# 6. ENVIRONMENT FILE
# ==========================================
echo ""
echo "6️⃣  Environment dosyası kontrol ediliyor..."

if [[ ! -f "app/.env" ]]; then
    if [[ -f ".env.shared_hosting" ]]; then
        cp .env.shared_hosting app/.env
        echo "✓ .env.shared_hosting → app/.env kopyalandı"
        echo "⚠️  UYARI: app/.env dosyasını düzenleyip database credentials ekleyin!"
    else
        echo "❌ Hata: .env dosyası bulunamadı"
        echo "Lütfen .env.shared_hosting dosyasını düzenleyip app/.env olarak kaydedin"
        exit 1
    fi
else
    echo "✓ app/.env mevcut"
fi

# ==========================================
# 7. DATABASE CHECK
# ==========================================
echo ""
echo "7️⃣  Database bağlantısı kontrol ediliyor..."

# Try to import and test database
python3 << EOF
import sys
sys.path.insert(0, 'app')

try:
    from config import get_settings
    settings = get_settings()
    print(f"✓ Database Config: {settings.DB_TYPE}://{settings.DB_USER}@{settings.DB_HOST}/{settings.DB_NAME}")
    
    # Test connection
    if settings.DB_TYPE == 'mysql':
        import pymysql
        conn = pymysql.connect(
            host=settings.DB_HOST,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            database=settings.DB_NAME
        )
        conn.close()
        print("✓ Database bağlantısı başarılı")
    else:
        print("⚠️  SQLite kullanılıyor - production için MySQL önerilir")
        
except Exception as e:
    print(f"❌ Database bağlantı hatası: {e}")
    print("Lütfen app/.env dosyasındaki database credentials'ı kontrol edin")
    sys.exit(1)
EOF

if [[ $? -ne 0 ]]; then
    echo ""
    echo "Database yapılandırması gerekli:"
    echo "1. cPanel → MySQL Databases"
    echo "2. Database ve user oluşturun"
    echo "3. app/.env dosyasına credentials ekleyin"
    exit 1
fi

# ==========================================
# 8. INITIALIZE DATABASE
# ==========================================
echo ""
echo "8️⃣  Database initialize ediliyor..."

python3 << EOF
import sys
sys.path.insert(0, 'app')

try:
    # Import initialization functions
    from elo_utils import init_database
    from update_elo import update_all_elo_ratings
    
    # Initialize database
    print("⏳ Database tables oluşturuluyor...")
    init_database()
    print("✓ Database initialized")
    
    # Update ELO ratings
    print("⏳ ELO ratings güncelleniyor...")
    update_all_elo_ratings()
    print("✓ ELO ratings updated")
    
except Exception as e:
    print(f"⚠️  Initialization warning: {e}")
    print("Database daha sonra manuel olarak initialize edilebilir")
EOF

# ==========================================
# 9. CREATE DIRECTORIES
# ==========================================
echo ""
echo "9️⃣  Gerekli klasörler oluşturuluyor..."

mkdir -p tmp
mkdir -p logs
mkdir -p backups
mkdir -p models

echo "✓ Klasörler oluşturuldu"

# ==========================================
# 10. SET PERMISSIONS
# ==========================================
echo ""
echo "🔟 Dosya izinleri ayarlanıyor..."

chmod 755 passenger_wsgi.py
chmod -R 755 app/
chmod 644 .htaccess
chmod 600 app/.env

echo "✓ İzinler ayarlandı"

# ==========================================
# 11. PASSENGER RESTART
# ==========================================
echo ""
echo "1️⃣1️⃣  Passenger yeniden başlatılıyor..."

touch tmp/restart.txt
echo "✓ Passenger restart signal gönderildi"

# ==========================================
# 12. DEPLOYMENT INFO
# ==========================================
echo ""
echo "=========================================="
echo "✅ DEPLOYMENT TAMAMLANDI!"
echo "=========================================="
echo ""
echo "📋 Deployment Bilgileri:"
echo "  - Virtual env: ~/public_html/venv"
echo "  - App location: ~/public_html/app"
echo "  - WSGI entry: ~/public_html/passenger_wsgi.py"
echo "  - Logs: ~/public_html/logs"
echo ""
echo "🌐 URL'ler:"
echo "  - Ana Sayfa: https://xn--gvenlinaliz-dlb.com"
echo "  - API Docs: https://xn--gvenlinaliz-dlb.com/docs"
echo "  - Health: https://xn--gvenlinaliz-dlb.com/api/ml/health"
echo ""
echo "🔧 Sonraki Adımlar:"
echo "  1. app/.env dosyasını kontrol edin"
echo "  2. Database credentials'ı doğrulayın"
echo "  3. URL'lere erişim test edin"
echo "  4. Error logs kontrol edin: cPanel → Errors"
echo ""
echo "🔄 Restart Komutu:"
echo "  touch ~/public_html/tmp/restart.txt"
echo ""
echo "📚 Daha fazla bilgi:"
echo "  - NAMECHEAP_DEPLOYMENT.md"
echo "  - DEPLOYMENT_GUIDE.md"
echo ""
echo "=========================================="

# ==========================================
# 13. HEALTH CHECK
# ==========================================
echo ""
echo "1️⃣2️⃣  Health check yapılıyor..."
sleep 3

# Try to check if app is running
if command -v curl &> /dev/null; then
    echo "⏳ API kontrol ediliyor..."
    
    # Local health check
    if curl -s http://localhost:8000/api/ml/health > /dev/null 2>&1; then
        echo "✅ Local API çalışıyor"
    else
        echo "⚠️  Local API henüz yanıt vermiyor (normal, birkaç saniye bekleyin)"
    fi
else
    echo "ℹ️  curl yüklü değil - manuel test yapın"
fi

echo ""
echo "🎉 Deployment script tamamlandı!"
echo ""
