#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Elo Güncelleme Monitoring Scripti
Bu script Elo güncellemesinin düzgün çalışıp çalışmadığını kontrol eder
"""

import json
import os
from datetime import datetime, timedelta, date

def check_elo_update_status():
    """Elo güncellemesinin son durumunu kontrol eder"""
    
    print("🔍 Elo Güncelleme Durumu Kontrolü")
    print("=" * 50)
    
    # Elo ratings dosyasını kontrol et
    elo_file = 'elo_ratings.json'
    if not os.path.exists(elo_file):
        print("❌ Elo ratings dosyası bulunamadı!")
        return False
    
    try:
        with open(elo_file, 'r', encoding='utf-8') as f:
            ratings = json.load(f)
    except Exception as e:
        print(f"❌ Elo ratings dosyası okunamadı: {e}")
        return False
    
    print(f"📊 Toplam takım sayısı: {len(ratings)}")
    
    # Son güncelleme tarihlerini kontrol et
    recent_updates = {}
    yesterday = (date.today() - timedelta(days=1)).strftime('%Y-%m-%d')
    today = date.today().strftime('%Y-%m-%d')
    
    for team_id, data in ratings.items():
        if team_id.startswith('_'):  # Meta veriler
            continue
            
        last_updated = data.get('last_updated', '')
        if last_updated:
            update_date = last_updated[:10]  # YYYY-MM-DD kısmını al
            if update_date in recent_updates:
                recent_updates[update_date] += 1
            else:
                recent_updates[update_date] = 1
    
    print("\n📅 Son günlerdeki güncellemeler:")
    for update_date in sorted(recent_updates.keys(), reverse=True)[:7]:
        count = recent_updates[update_date]
        print(f"  {update_date}: {count} takım güncellendi")
    
    # Dünkü güncellemeleri kontrol et
    yesterday_updates = recent_updates.get(yesterday, 0)
    today_updates = recent_updates.get(today, 0)
    
    print(f"\n🎯 Kritik Kontroller:")
    print(f"  Dün ({yesterday}): {yesterday_updates} takım güncellendi")
    print(f"  Bugün ({today}): {today_updates} takım güncellendi")
    
    if yesterday_updates > 0:
        print("✅ Dünkü maçlar için Elo güncellemesi yapıldı!")
        return True
    else:
        print("⚠️  Dünkü maçlar için Elo güncellemesi yapılmamış olabilir")
        print("   Bu durum şu nedenlerle olabilir:")
        print("   - Dün maç olmadı")
        print("   - Otomatik güncelleme çalışmadı")
        print("   - API problemi yaşandı")
        return False

def main():
    """Ana fonksiyon"""
    print(f"🕐 Kontrol zamanı: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    status = check_elo_update_status()
    
    print("\n" + "=" * 50)
    if status:
        print("✅ Elo güncelleme sistemi düzgün çalışıyor!")
    else:
        print("⚠️  Elo güncelleme sistemi kontrol edilmeli!")
        print("\n💡 Manuel güncelleme için:")
        print("   python update_elo.py")
        print("\n💡 Otomatik güncelleme için:")
        print("   https://www.güvenlianaliz.com?action=run_tasks&secret=Elam1940*")
    
    return status

if __name__ == '__main__':
    main()