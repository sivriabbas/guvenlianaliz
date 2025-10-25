#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Transfer Etki Analiz Modülü
Yeni transferler, adaptasyon süreci, takım kimyası etkisi
"""

import requests
from typing import Dict, Optional, List
from datetime import datetime, timedelta

# Cache sistemi
try:
    from api_cache_wrapper import get_team_transfers_cached, cache
    CACHE_ENABLED = True
except:
    CACHE_ENABLED = False

API_KEY = "6336fb21e17dea87880d3b133132a13f"
BASE_URL = "https://v3.football.api-sports.io"

def get_team_transfers(team_id: int, season: int = 2025) -> Optional[List[Dict]]:
    """
    Takımın sezon başı transferlerini çek (CACHE'Lİ)
    """
    # Cache varsa kullan
    if CACHE_ENABLED:
        try:
            cached = cache.get('transfers', team_id=team_id, season=season)
            if cached:
                return cached
        except:
            pass
    
    headers = {'x-apisports-key': API_KEY}
    
    try:
        url = f"{BASE_URL}/transfers?team={team_id}"
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            transfers = []
            for transfer_data in data.get('response', []):
                for transfer in transfer_data.get('transfers', []):
                    # Sadece gelen transferler
                    if transfer['teams']['in']['id'] == team_id:
                        try:
                            # API farklı formatlar kullanabiliyor
                            transfer_date_str = transfer['date']
                            if len(transfer_date_str) == 6:  # DDMMYY format
                                day = int(transfer_date_str[0:2])
                                month = int(transfer_date_str[2:4])
                                year = 2000 + int(transfer_date_str[4:6])
                                transfer_date = datetime(year, month, day)
                            else:
                                transfer_date = datetime.strptime(transfer_date_str, '%Y-%m-%d')
                        except:
                            # Tarih parse edilemezse 30 gün önce varsay
                            transfer_date = datetime.now() - timedelta(days=30)
                        
                        # Son 6 ay içindeki transferler
                        if (datetime.now() - transfer_date).days <= 180:
                            transfers.append({
                                'player': transfer_data['player']['name'],
                                'date': transfer['date'],
                                'from_team': transfer['teams']['out']['name'],
                                'type': transfer['type'],
                                'days_since': (datetime.now() - transfer_date).days
                            })
            
            # Cache'e kaydet (24 saat)
            if CACHE_ENABLED and transfers:
                try:
                    cache.set('transfers', transfers, 86400, team_id=team_id, season=season)
                except:
                    pass
            
            return transfers
            
    except Exception as e:
        print(f"Transfer verisi hatası: {e}")
    
    return None


def calculate_transfer_impact(team_name: str, team_id: int = None, 
                              recent_form: float = 50.0) -> Dict:
    """
    Transfer etkisini hesapla
    
    Faktörler:
    - Transfer sayısı (çok transfer = adaptasyon sorunu)
    - Adaptasyon süresi (yeni oyuncular hala uyum sağlıyor mu?)
    - Form durumu (yeni kadro iyi oynuyor mu?)
    """
    
    # Gerçek transfer verisi
    transfers = None
    if team_id:
        transfers = get_team_transfers(team_id)
    
    # Transfer analizi
    if transfers and len(transfers) > 0:
        total_transfers = len(transfers)
        recent_transfers = len([t for t in transfers if t['days_since'] <= 60])  # Son 2 ay
        adapting_transfers = len([t for t in transfers if 30 <= t['days_since'] <= 120])  # 1-4 ay arası
        
        impact_score = 0
        factors = []
        
        # 1. Transfer Sayısı Etkisi
        if total_transfers >= 6:
            impact_score -= 5
            factors.append(f"⚠️ Çok fazla transfer ({total_transfers}) - Takım kimyası etkilenebilir")
        elif total_transfers >= 4:
            impact_score -= 2
            factors.append(f"📝 Yüksek transfer sayısı ({total_transfers})")
        elif total_transfers <= 2:
            impact_score += 2
            factors.append(f"✅ Dengeli transfer politikası ({total_transfers})")
        
        # 2. Adaptasyon Süreci
        if recent_transfers >= 3:
            impact_score -= 4
            factors.append(f"🆕 {recent_transfers} çok yeni transfer - Uyum süreci devam ediyor")
        elif adapting_transfers >= 3:
            impact_score -= 2
            factors.append(f"🔄 {adapting_transfers} oyuncu hala adaptasyon sürecinde")
        
        # 3. Form Bazlı Değerlendirme
        # Çok transfer olmasına rağmen form iyiyse = başarılı entegrasyon
        if total_transfers >= 4 and recent_form > 65:
            impact_score += 4
            factors.append(f"✅ Yeni transferler hızlı adapte olmuş (Form: %{recent_form:.0f})")
        elif total_transfers >= 4 and recent_form < 45:
            impact_score -= 3
            factors.append(f"⚠️ Transferler henüz etkili değil (Form: %{recent_form:.0f})")
        
        # Transfer detayları
        transfer_list = []
        for t in transfers[:5]:  # İlk 5 transfer
            days_text = f"{t['days_since']} gün önce"
            transfer_list.append(f"• {t['player']} ({t['from_team']}) - {days_text}")
        
        category = "POZİTİF" if impact_score > 0 else "NEGATİF" if impact_score < -3 else "NÖTR"
        
        return {
            'available': True,
            'total_transfers': total_transfers,
            'recent_transfers': recent_transfers,
            'adapting_transfers': adapting_transfers,
            'impact_score': impact_score,
            'category': category,
            'factors': factors,
            'transfer_list': transfer_list,
            'prediction_impact': round(impact_score * 0.6, 1)  # -3% ile +2.4% arası
        }
    
    # Transfer verisi yoksa simülasyon
    else:
        # Form bazlı basit tahmin
        if recent_form > 70:
            impact_score = 2
            category = "İSTİKRARLI"
            note = "Transfer detayları yok - Form iyi, kadro stabil görünüyor"
        elif recent_form < 45:
            impact_score = -2
            category = "İSTİKRARSIZ"
            note = "Transfer detayları yok - Form kötü, kadro değişimleri olabilir"
        else:
            impact_score = 0
            category = "NORMAL"
            note = "Transfer detayları yok - Normal kadro istikrarı varsayılıyor"
        
        return {
            'available': False,
            'total_transfers': 0,
            'recent_transfers': 0,
            'adapting_transfers': 0,
            'impact_score': impact_score,
            'category': category,
            'factors': [note],
            'transfer_list': [],
            'prediction_impact': round(impact_score * 0.6, 1)
        }


def compare_transfer_situations(home_team: str, away_team: str,
                                home_team_id: int = None, away_team_id: int = None,
                                home_form: float = 50.0, away_form: float = 50.0) -> Dict:
    """
    İki takımın transfer durumlarını karşılaştır
    """
    
    home_transfer = calculate_transfer_impact(home_team, home_team_id, home_form)
    away_transfer = calculate_transfer_impact(away_team, away_team_id, away_form)
    
    # Avantaj hesapla
    impact_diff = home_transfer['impact_score'] - away_transfer['impact_score']
    
    if impact_diff > 3:
        advantage = home_team
        advantage_desc = f"{home_team} kadrosu daha istikrarlı ve entegre"
    elif impact_diff < -3:
        advantage = away_team
        advantage_desc = f"{away_team} kadrosu daha istikrarlı ve entegre"
    else:
        advantage = "Dengeli"
        advantage_desc = "Her iki takım da benzer kadro istikrarına sahip"
    
    return {
        'home_transfer': home_transfer,
        'away_transfer': away_transfer,
        'advantage': advantage,
        'advantage_description': advantage_desc,
        'impact_difference': impact_diff,
        'prediction_impact': round(impact_diff * 0.5, 1)  # -2.5% ile +2.5% arası
    }


if __name__ == "__main__":
    print("=" * 70)
    print("TRANSFER ETKİ ANALİZ TESTİ")
    print("=" * 70)
    
    # Test 1: Galatasaray (team_id: 645)
    print("\n📋 Galatasaray Transfer Analizi:")
    analysis = calculate_transfer_impact("Galatasaray", 645, 75.0)
    
    if analysis['available']:
        print(f"  Toplam Transfer: {analysis['total_transfers']}")
        print(f"  Son 2 Aydaki Transferler: {analysis['recent_transfers']}")
        print(f"  Adaptasyon Sürecindeki Oyuncular: {analysis['adapting_transfers']}")
        print(f"  Kategori: {analysis['category']}")
        print(f"  Etki Skoru: {analysis['impact_score']}/10")
        print(f"  Tahmin Etkisi: {analysis['prediction_impact']}%")
        
        if analysis['transfer_list']:
            print(f"\n  Son Transferler:")
            for transfer in analysis['transfer_list']:
                print(f"    {transfer}")
        
        if analysis['factors']:
            print(f"\n  Faktörler:")
            for factor in analysis['factors']:
                print(f"    {factor}")
    else:
        print(f"  Durum: {analysis['category']}")
        print(f"  Not: {analysis['factors'][0]}")
    
    # Test 2: Fenerbahçe (team_id: 611)
    print("\n" + "=" * 70)
    print("📋 Fenerbahçe Transfer Analizi:")
    analysis = calculate_transfer_impact("Fenerbahçe", 611, 65.0)
    
    if analysis['available']:
        print(f"  Toplam Transfer: {analysis['total_transfers']}")
        print(f"  Kategori: {analysis['category']}")
        print(f"  Etki Skoru: {analysis['impact_score']}/10")
    
    # Test 3: Karşılaştırma
    print("\n" + "=" * 70)
    print("⚖️ Galatasaray vs Fenerbahçe Transfer Karşılaştırması:")
    comparison = compare_transfer_situations("Galatasaray", "Fenerbahçe", 645, 611, 75.0, 65.0)
    
    print(f"\n  Avantaj: {comparison['advantage']}")
    print(f"  Açıklama: {comparison['advantage_description']}")
    print(f"  Etki Farkı: {comparison['impact_difference']}")
    print(f"  Tahmin Etkisi: {comparison['prediction_impact']}%")
