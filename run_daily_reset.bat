@echo off
REM Bu .bat dosyası daily_reset.py script'ini workspace klasöründen çalıştırır.
REM Gerekirse tam python.exe yolunu ayarlayın (ör. C:\Users\Mustafa\Envs\venv\Scripts\python.exe)

REM Çalışma dizinini .bat dosyasının bulunduğu klasöre ayarla
cd /d "%~dp0"

REM Varsayılan python yürütücüsü
set "PYTHON_EXE=python"

REM python komutunun çalışıp çalışmadığını kontrol et
%PYTHON_EXE% -V >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Python bulunamadı veya PATH'te kayıtlı değil. Lütfen run_daily_reset.bat içindeki PYTHON_EXE değişkenini tam python.exe yolu ile güncelleyin.
    exit /b 1
)

REM Argümanları daily_reset.py'ye geçir
%PYTHON_EXE% "%~dp0daily_reset.py" %*
exit /b %ERRORLEVEL%