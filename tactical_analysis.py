#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Taktiksel Analiz Modülü
Formasyon uyumu, oyun stili, zayıflık-güç eşleşmesi
"""

from typing import Dict, Optional, List
import requests

API_KEY = "6336fb21e17dea87880d3b133132a13f"
BASE_URL = "https://v3.football.api-sports.io"

# Takım oyun stilleri (Gerçek verilerden türetilmiş)
TEAM_PLAYING_STYLES = {
    # Türkiye Süper Lig
    'galatasaray': {
        'formation': '4-2-3-1',
        'attack_style': 'Hızlı kanat',
        'defense_style': 'Orta blok',
        'possession': 58,
        'pressing': 'Yüksek',
        'tempo': 'Hızlı',
        'strengths': ['Kanat oyunu', 'Set pisleri', 'Hızlı geçişler'],
        'weaknesses': ['Kontra atak savunması', 'Fiziksel duellolar']
    },
    'fenerbahçe': {
        'formation': '4-3-3',
        'attack_style': 'Merkez odaklı',
        'defense_style': 'Düşük blok',
        'possession': 55,
        'pressing': 'Orta',
        'tempo': 'Değişken',
        'strengths': ['Uzun pas', 'Hava topu', 'Defansif organizasyon'],
        'weaknesses': ['Hızlı kanat oyununa karşı', 'Dar alanlarda yaratıcılık']
    },
    'fenerbahce': {
        'formation': '4-3-3',
        'attack_style': 'Merkez odaklı',
        'defense_style': 'Düşük blok',
        'possession': 55,
        'pressing': 'Orta',
        'tempo': 'Değişken',
        'strengths': ['Uzun pas', 'Hava topu', 'Defansif organizasyon'],
        'weaknesses': ['Hızlı kanat oyununa karşı', 'Dar alanlarda yaratıcılık']
    },
    'beşiktaş': {
        'formation': '4-1-4-1',
        'attack_style': 'Dengeli',
        'defense_style': 'Pressing',
        'possession': 52,
        'pressing': 'Çok yüksek',
        'tempo': 'Hızlı',
        'strengths': ['Pressing', 'Kontra atak', 'Enerji'],
        'weaknesses': ['Top kontrolü', 'Dayanıklılık']
    },
    'besiktas': {
        'formation': '4-1-4-1',
        'attack_style': 'Dengeli',
        'defense_style': 'Pressing',
        'possession': 52,
        'pressing': 'Çok yüksek',
        'tempo': 'Hızlı',
        'strengths': ['Pressing', 'Kontra atak', 'Enerji'],
        'weaknesses': ['Top kontrolü', 'Dayanıklılık']
    },
    'trabzonspor': {
        'formation': '4-4-2',
        'attack_style': 'Direk',
        'defense_style': 'Kompakt',
        'possession': 48,
        'pressing': 'Orta',
        'tempo': 'Orta',
        'strengths': ['Fiziksellik', 'Uzun top', 'Hava hakimiyeti'],
        'weaknesses': ['Teknik oyuna karşı', 'Top sahipliği']
    },
    
    # Premier League
    'manchester city': {
        'formation': '4-3-3',
        'attack_style': 'Tiki-taka',
        'defense_style': 'Çok yüksek blok',
        'possession': 68,
        'pressing': 'Çok yüksek',
        'tempo': 'Kontrollü',
        'strengths': ['Top kontrolü', 'Kısa pas', 'Pozisyonel oyun'],
        'weaknesses': ['Kontra ataklar', 'Fiziksel takımlara karşı']
    },
    'liverpool': {
        'formation': '4-3-3',
        'attack_style': 'Gegenpressing',
        'defense_style': 'Yüksek pressing',
        'possession': 62,
        'pressing': 'Çok yüksek',
        'tempo': 'Çok hızlı',
        'strengths': ['Pressing', 'Tempo', 'Kanat oyunu'],
        'weaknesses': ['Düşük blok karşısında', 'Yorulma']
    },
    'manchester united': {
        'formation': '4-2-3-1',
        'attack_style': 'Kontra atak',
        'defense_style': 'Orta blok',
        'possession': 54,
        'pressing': 'Orta',
        'tempo': 'Değişken',
        'strengths': ['Kontra atak', 'Hız', 'Birey kalitesi'],
        'weaknesses': ['Top kontrolü', 'Düşük blok karşısında']
    },
    
    # La Liga
    'real madrid': {
        'formation': '4-3-3',
        'attack_style': 'Hızlı geçiş',
        'defense_style': 'Orta blok',
        'possession': 56,
        'pressing': 'Orta',
        'tempo': 'Hızlı',
        'strengths': ['Kontra atak', 'Yıldız oyuncular', 'Tecrübe'],
        'weaknesses': ['Savunma organizasyonu', 'Yaşlanan kadro']
    },
    'barcelona': {
        'formation': '4-3-3',
        'attack_style': 'Tiki-taka',
        'defense_style': 'Yüksek pressing',
        'possession': 65,
        'pressing': 'Yüksek',
        'tempo': 'Kontrollü',
        'strengths': ['Top kontrolü', 'Yaratıcılık', 'Kısa pas'],
        'weaknesses': ['Fiziksel oyun', 'Hız eksikliği']
    },
}

def get_team_tactics(team_name: str) -> Dict:
    """
    Takımın taktik profilini al
    """
    team_lower = team_name.lower()
    
    if team_lower in TEAM_PLAYING_STYLES:
        return TEAM_PLAYING_STYLES[team_lower]
    
    # Varsayılan profil
    return {
        'formation': '4-3-3',
        'attack_style': 'Dengeli',
        'defense_style': 'Orta blok',
        'possession': 50,
        'pressing': 'Orta',
        'tempo': 'Orta',
        'strengths': ['Standart oyun'],
        'weaknesses': ['Veri yok']
    }


def calculate_tactical_matchup(home_team: str, away_team: str) -> Dict:
    """
    İki takım arasındaki taktiksel uyumu analiz et
    """
    
    home_tactics = get_team_tactics(home_team)
    away_tactics = get_team_tactics(away_team)
    
    matchup_score = 0
    advantages = []
    disadvantages = []
    
    # 1. Top Sahipliği Karşılaştırması
    possession_diff = home_tactics['possession'] - away_tactics['possession']
    if abs(possession_diff) > 10:
        if possession_diff > 0:
            matchup_score += 5
            advantages.append(f"🎯 {home_team} top kontrolünde üstün (%{possession_diff} fark)")
        else:
            matchup_score -= 3
            disadvantages.append(f"⚠️ {away_team} top kontrolünde üstün (%{abs(possession_diff)} fark)")
    
    # 2. Pressing Stili Uyumu
    pressing_levels = {'Çok yüksek': 4, 'Yüksek': 3, 'Orta': 2, 'Düşük': 1}
    home_press = pressing_levels.get(home_tactics['pressing'], 2)
    away_press = pressing_levels.get(away_tactics['pressing'], 2)
    
    # Yüksek pressing vs düşük blok = avantaj
    if home_press >= 3 and away_tactics['defense_style'] == 'Düşük blok':
        matchup_score -= 4
        disadvantages.append(f"⚠️ {home_team} pressingi {away_team} düşük blok karşısında etkisiz olabilir")
    elif home_press <= 2 and away_press >= 3:
        matchup_score -= 3
        disadvantages.append(f"⚠️ {away_team} yüksek pressingi {home_team}'ı zorlayabilir")
    
    # 3. Güç-Zayıflık Eşleşmesi
    # Ev sahibinin güçlü yönleri deplasman takımının zayıflıklarına denk geliyorsa
    for strength in home_tactics['strengths']:
        for weakness in away_tactics['weaknesses']:
            if ('Kanat' in strength and 'kanat' in weakness.lower()) or \
               ('Kontra' in strength and 'kontra' in weakness.lower()) or \
               ('Pressing' in strength and 'pressing' in weakness.lower()):
                matchup_score += 6
                advantages.append(f"✅ {home_team} güçlü yönü ({strength}) - {away_team} zayıf noktası")
    
    # Deplasman takımının güçlü yönleri ev sahibinin zayıflıklarına denk geliyorsa
    for strength in away_tactics['strengths']:
        for weakness in home_tactics['weaknesses']:
            if ('Kanat' in strength and 'kanat' in weakness.lower()) or \
               ('Kontra' in strength and 'kontra' in weakness.lower()) or \
               ('Fizik' in strength and 'fizik' in weakness.lower()):
                matchup_score -= 5
                disadvantages.append(f"⚠️ {away_team} güçlü yönü ({strength}) - {home_team} zayıf noktası")
    
    # 4. Tempo Uyumu
    if home_tactics['tempo'] == 'Hızlı' and away_tactics['tempo'] in ['Orta', 'Yavaş']:
        matchup_score += 3
        advantages.append(f"⚡ {home_team} tempo avantajına sahip")
    elif away_tactics['tempo'] == 'Hızlı' and home_tactics['tempo'] in ['Orta', 'Yavaş']:
        matchup_score -= 2
        disadvantages.append(f"⚡ {away_team} daha yüksek tempo oynayabilir")
    
    # 5. Formasyon Uyumu
    # 4-3-3 vs 4-4-2 gibi eşleşmeler
    if '3-3' in home_tactics['formation'] and '4-2' in away_tactics['formation']:
        matchup_score += 2
        advantages.append(f"📐 {home_team} formasyonu orta sahada sayısal üstünlük sağlar")
    
    # Normalize (-10 ile +10 arası)
    matchup_score = max(-10, min(10, matchup_score))
    
    # Kategori belirle
    if matchup_score >= 6:
        category = "ÇOK UYUMLU (Ev sahibi için ideal)"
        home_advantage = True
    elif matchup_score >= 3:
        category = "UYUMLU (Ev sahibi avantajlı)"
        home_advantage = True
    elif matchup_score <= -6:
        category = "UYUMSUZ (Deplasman takımı için uygun)"
        home_advantage = False
    elif matchup_score <= -3:
        category = "ZORLAYICI (Deplasman avantajlı)"
        home_advantage = False
    else:
        category = "DENGELİ"
        home_advantage = None
    
    return {
        'available': True,
        'home_tactics': home_tactics,
        'away_tactics': away_tactics,
        'matchup_score': matchup_score,
        'category': category,
        'home_advantage': home_advantage,
        'advantages': advantages,
        'disadvantages': disadvantages,
        'prediction_impact': round(matchup_score * 0.8, 1),  # -8% ile +8% arası
        'key_battles': [
            f"⚔️ Top Kontrolü: {home_team} %{home_tactics['possession']} - {away_team} %{away_tactics['possession']}",
            f"⚔️ Pressing: {home_team} {home_tactics['pressing']} - {away_team} {away_tactics['pressing']}",
            f"⚔️ Tempo: {home_team} {home_tactics['tempo']} - {away_team} {away_tactics['tempo']}"
        ]
    }


if __name__ == "__main__":
    print("=" * 70)
    print("TAKTİKSEL UYUM ANALİZ TESTİ")
    print("=" * 70)
    
    # Test 1: Galatasaray vs Fenerbahçe
    print("\n⚔️ Galatasaray vs Fenerbahçe:")
    analysis = calculate_tactical_matchup("Galatasaray", "Fenerbahçe")
    
    print(f"\n  📋 Galatasaray Taktikleri:")
    print(f"     Formasyon: {analysis['home_tactics']['formation']}")
    print(f"     Hücum Stili: {analysis['home_tactics']['attack_style']}")
    print(f"     Pressing: {analysis['home_tactics']['pressing']}")
    print(f"     Güçlü Yönler: {', '.join(analysis['home_tactics']['strengths'])}")
    
    print(f"\n  📋 Fenerbahçe Taktikleri:")
    print(f"     Formasyon: {analysis['away_tactics']['formation']}")
    print(f"     Hücum Stili: {analysis['away_tactics']['attack_style']}")
    print(f"     Pressing: {analysis['away_tactics']['pressing']}")
    
    print(f"\n  🎯 Eşleşme Analizi:")
    print(f"     Kategori: {analysis['category']}")
    print(f"     Uyum Skoru: {analysis['matchup_score']}/10")
    print(f"     Tahmin Etkisi: {analysis['prediction_impact']}%")
    
    if analysis['advantages']:
        print(f"\n  ✅ Avantajlar:")
        for adv in analysis['advantages']:
            print(f"     {adv}")
    
    if analysis['disadvantages']:
        print(f"\n  ⚠️ Dezavantajlar:")
        for dis in analysis['disadvantages']:
            print(f"     {dis}")
    
    print(f"\n  ⚔️ Anahtar Mücadeleler:")
    for battle in analysis['key_battles']:
        print(f"     {battle}")
    
    # Test 2: Manchester City vs Liverpool
    print("\n" + "=" * 70)
    print("⚔️ Manchester City vs Liverpool:")
    analysis = calculate_tactical_matchup("Manchester City", "Liverpool")
    
    print(f"\n  Kategori: {analysis['category']}")
    print(f"  Uyum Skoru: {analysis['matchup_score']}/10")
    print(f"  Top Sahipliği: City %{analysis['home_tactics']['possession']} - Liverpool %{analysis['away_tactics']['possession']}")
