Daily reset scripti (Windows Task Scheduler)

1) Komut örneği (cmd.exe için):

   python "C:\Users\Mustafa\Desktop\yenianaliz\daily_reset.py"

   veya tek kullanıcı sıfırlama için:

   python "C:\Users\Mustafa\Desktop\yenianaliz\daily_reset.py" --user demo_user

2) Windows Task Scheduler adımları (özet):
   - Task Scheduler açın -> Create Basic Task
   - Name: "yenianaliz_daily_reset"
   - Trigger: Daily, Recur every 1 day, Start: 00:00
   - Action: Start a program
       Program/script: C:\Windows\System32\cmd.exe
       Add arguments: /c python "C:\Users\Mustafa\Desktop\yenianaliz\daily_reset.py"
   - Finish

Not: Eğer virtualenv kullanıyorsanız, `python` komutunu virtualenv'in python.exe yoluyla değiştirin veya bir .bat dosyası yazıp onu çalıştırın.
