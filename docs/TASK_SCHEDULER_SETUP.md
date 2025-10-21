# Windows Task Scheduler: daily_reset.py için Kurulum

Aşağıdaki adımlar `daily_reset.py` script'ini her gece 00:00'da çalıştırmak için Task Scheduler üzerinde bir görev oluşturur.

Ön Koşullar
- Python yüklü ve `python` komutu komut istemcisinden çalışıyor ya da `run_daily_reset.bat` içindeki `PYTHON_EXE` satırı ile tam yol verilmiş olmalıdır.
- Workspace dizini: `C:\Users\Mustafa\Desktop\yenianaliz`
- `run_daily_reset.bat` dosyası workspace içinde mevcut olmalıdır.

Adım adım (GUI yöntem)
1. Başlat menüsünden "Task Scheduler" (Görev Zamanlayıcı) uygulamasını açın.
2. Sağ taraftan "Create Basic Task..." seçeneğini tıklayın.
3. Görev adı verin: `yenianaliz_daily_reset` ve isteğe bağlı açıklama ekleyin.
4. "Trigger" kısmında "Daily" seçin ve Start time olarak 00:00 seçin.
5. "Action" kısmında "Start a program" seçin.
6. Program/script alanına `C:\Users\Mustafa\Desktop\yenianaliz\run_daily_reset.bat` dosyasının tam yolunu girin.
7. Finish ile görevi kaydedin.
8. Görevi seçip sağ tıklayarak "Run" ile elle test edebilirsiniz.

Komut satırı yöntemi (schtasks)
Aşağıdaki örnek, kullanıcı hesabınız altında günlük 00:00'da çalışan bir görev oluşturur. Komutu Yönetici olarak çalıştırmanız gerekir.

schtasks /Create /SC DAILY /TN "yenianaliz_daily_reset" /TR "C:\\Users\\Mustafa\\Desktop\\yenianaliz\\run_daily_reset.bat" /ST 00:00 /F

Notlar
- Eğer Python PATH'te değilse, `run_daily_reset.bat` içindeki yorum satırını düzenleyerek `PYTHON_EXE` ile tam python yolu verin.
- Görev, dosya yollarını değiştirmeden çalışması için kullanıcı hesabının ilgili klasöre erişimi ve yazma izinleri olmalıdır.
- İsteğe bağlı: `daily_reset.py --user <username>` kullanarak tek kullanıcı sıfırlaması yapmak için `/TR` argümanını değiştirin.
  Örnek: `"C:\\Users\\Mustafa\\Desktop\\yenianaliz\\run_daily_reset.bat" --user demo_user` (bu örnek .bat'inizi argümanları passtrough yapacak şekilde değiştirirseniz çalışır).

Sorun Giderme
- Görev çalışmıyorsa, "History" sekmesini kontrol edin ve hata iletilerini inceleyin.
- Python komutları için PATH veya sanal ortam kullanıyorsanız, .bat içine tam python.exe yolunu yazmak genellikle en güvenli çözümdür.

