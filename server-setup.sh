#!/bin/bash
# ================================================
# NAMECHEAP FASTAPI DEPLOYMENT - SERVER SETUP
# Bu script'i sunucuda çalıştırın (SSH veya cPanel Terminal)
# ================================================

echo "================================================"
echo "  FASTAPI SERVER KURULUMU"
echo "================================================"
echo ""

# Renk kodları
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Ana dizine git
cd ~/public_html

echo -e "${YELLOW}[1/7] Python version kontrol...${NC}"
python3 --version
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Python3 bulundu${NC}"
else
    echo -e "${RED}❌ Python3 bulunamadı!${NC}"
    exit 1
fi

echo ""
echo -e "${YELLOW}[2/7] Virtual environment oluşturuluyor...${NC}"
if [ -d "venv" ]; then
    echo -e "${YELLOW}⚠️  Mevcut venv bulundu, temizleniyor...${NC}"
    rm -rf venv
fi

python3 -m venv venv
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Virtual environment oluşturuldu${NC}"
else
    echo -e "${RED}❌ Virtual environment oluşturulamadı!${NC}"
    exit 1
fi

echo ""
echo -e "${YELLOW}[3/7] Virtual environment aktive ediliyor...${NC}"
source venv/bin/activate
echo -e "${GREEN}✅ Virtual environment aktif${NC}"

echo ""
echo -e "${YELLOW}[4/7] Pip güncelleniyor...${NC}"
pip install --upgrade pip setuptools wheel
echo -e "${GREEN}✅ Pip güncellendi${NC}"

echo ""
echo -e "${YELLOW}[5/7] Python paketleri kuruluyor (bu birkaç dakika sürebilir)...${NC}"
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Tüm paketler kuruldu${NC}"
    else
        echo -e "${RED}❌ Paket kurulumu başarısız!${NC}"
        echo -e "${YELLOW}Minimal kurulum deneniyor...${NC}"
        pip install fastapi uvicorn jinja2 python-multipart asgiref requests pandas pyyaml python-jose passlib bcrypt
    fi
else
    echo -e "${RED}❌ requirements.txt bulunamadı!${NC}"
    exit 1
fi

echo ""
echo -e "${YELLOW}[6/7] Gerekli klasörler oluşturuluyor...${NC}"
mkdir -p logs
mkdir -p tmp
mkdir -p models
touch tmp/restart.txt
chmod 755 passenger_wsgi.py
chmod 644 .htaccess
chmod 600 .env 2>/dev/null || echo ".env bulunamadı - oluşturmanız gerekiyor"
echo -e "${GREEN}✅ Klasörler ve yetkiler ayarlandı${NC}"

echo ""
echo -e "${YELLOW}[7/7] Kurulum testi...${NC}"
echo "Python packages:"
pip list | head -n 20
echo ""
echo "Dizin yapısı:"
ls -lah | head -n 15

echo ""
echo "================================================"
echo -e "${GREEN}  ✅ KURULUM TAMAMLANDI${NC}"
echo "================================================"
echo ""
echo -e "${YELLOW}SONRAKI ADIMLAR:${NC}"
echo "1. .env dosyasını oluşturun ve doldurun:"
echo "   cp .env.example .env"
echo "   nano .env  # veya cPanel File Manager ile"
echo ""
echo "2. .htaccess'te [USERNAME] değiştirin"
echo ""
echo "3. Passenger'ı yeniden başlatın:"
echo "   touch ~/public_html/tmp/restart.txt"
echo ""
echo "4. Website'i test edin:"
echo "   https://xn--gvenlinaliz-dlb.com"
echo "   https://xn--gvenlinaliz-dlb.com/docs"
echo ""
echo "5. Logları kontrol edin:"
echo "   tail -f ~/public_html/logs/passenger_startup.log"
echo "   tail -f ~/public_html/logs/api.log"
echo ""
echo -e "${GREEN}Başarılar! 🚀${NC}"
echo ""
