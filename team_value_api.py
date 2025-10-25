#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Takım Piyasa Değeri API Modülü
Transfermarkt ve diğer kaynaklardan gerçek piyasa değerleri
"""

import json
from typing import Dict, Optional

# Gerçek Takım Değerleri Cache (Manuel Güncellenecek)
# Kaynak: Transfermarkt.com (Ekim 2025)
REAL_TEAM_VALUES = {
    # Türkiye Süper Lig
    'galatasaray': 285.30,
    'fenerbahce': 270.15,
    'fenerbahçe': 270.15,
    'besiktas': 178.65,
    'beşiktaş': 178.65,
    'trabzonspor': 95.40,
    'basaksehir': 55.25,
    'başakşehir': 55.25,
    'goztepe': 22.85,
    'göztepe': 22.85,
    'samsunspor': 31.20,
    'konyaspor': 24.15,
    'antalyaspor': 22.40,
    'kasimpasa': 19.75,
    'kasımpaşa': 19.75,
    'alanyaspor': 18.90,
    'kayserispor': 17.35,
    'rizespor': 15.80,
    'eyupspor': 14.25,
    'eyüpspor': 14.25,
    'hatayspor': 16.50,
    'sivasspor': 18.20,
    'gaziantep': 13.70,
    'adana demirspor': 19.40,
    
    # Premier League (Top Teams)
    'manchester city': 1240.50,
    'arsenal': 1180.75,
    'liverpool': 1095.20,
    'chelsea': 1015.80,
    'manchester united': 925.40,
    'tottenham': 875.60,
    'newcastle': 715.30,
    'aston villa': 685.25,
    'brighton': 515.40,
    'west ham': 485.70,
    
    # La Liga (Top Teams)
    'real madrid': 1350.80,
    'barcelona': 1115.90,
    'atletico madrid': 715.45,
    'athletic bilbao': 485.30,
    'real sociedad': 425.80,
    'real betis': 385.60,
    'villarreal': 365.40,
    'sevilla': 345.20,
    
    # Bundesliga (Top Teams)
    'bayern munich': 1095.70,
    'borussia dortmund': 685.40,
    'rb leipzig': 565.80,
    'bayer leverkusen': 715.90,
    'eintracht frankfurt': 385.45,
    'wolfsburg': 325.60,
    'freiburg': 285.30,
    
    # Serie A (Top Teams)
    'inter': 685.90,
    'ac milan': 615.75,
    'napoli': 715.40,
    'juventus': 685.50,
    'roma': 485.80,
    'lazio': 365.40,
    'atalanta': 515.60,
    'fiorentina': 335.25,
    
    # Ligue 1 (Top Teams)
    'psg': 1015.80,
    'paris saint germain': 1015.80,
    'monaco': 515.70,
    'marseille': 385.90,
    'lyon': 325.45,
    'lille': 315.80,
    'lens': 285.60,
    'nice': 265.40,
    
    # Other European
    'ajax': 285.70,
    'psv': 315.85,
    'feyenoord': 215.40,
    'porto': 315.90,
    'benfica': 385.75,
    'sporting': 425.80,
    'celtic': 185.60,
    'rangers': 165.40,
}

def get_team_market_value(team_name: str, league: str = None) -> float:
    """
    Takım piyasa değerini al (Gerçek verilerle)
    
    Args:
        team_name: Takım adı
        league: Lig adı (opsiyonel)
    
    Returns:
        Piyasa değeri (milyon €)
    """
    # Takım adını normalize et
    team_lower = team_name.lower().strip()
    
    # Türkçe karakter düzeltmeleri
    team_normalized = team_lower.replace('ö', 'o').replace('ü', 'u').replace('ı', 'i')
    team_normalized = team_normalized.replace('ş', 's').replace('ç', 'c').replace('ğ', 'g')
    
    # Önce tam eşleşme
    if team_lower in REAL_TEAM_VALUES:
        value = REAL_TEAM_VALUES[team_lower]
        print(f"💰 {team_name} piyasa değeri: €{value}M (Gerçek veri)")
        return value
    
    # Normalize edilmiş isimle
    if team_normalized in REAL_TEAM_VALUES:
        value = REAL_TEAM_VALUES[team_normalized]
        print(f"💰 {team_name} piyasa değeri: €{value}M (Gerçek veri)")
        return value
    
    # Kısmi eşleşme (takım adı içinde geçiyorsa)
    for key, value in REAL_TEAM_VALUES.items():
        if key in team_lower or team_lower in key:
            print(f"💰 {team_name} piyasa değeri: €{value}M (Kısmi eşleşme: {key})")
            return value
    
    # Bulunamazsa lige göre tahmin
    if league:
        league_lower = league.lower()
        if 'premier league' in league_lower:
            default_value = 185.0
        elif 'la liga' in league_lower or 'liga' in league_lower:
            default_value = 165.0
        elif 'bundesliga' in league_lower:
            default_value = 155.0
        elif 'serie a' in league_lower:
            default_value = 145.0
        elif 'ligue 1' in league_lower:
            default_value = 135.0
        elif 'süper lig' in league_lower or 'super lig' in league_lower or 'turkey' in league_lower:
            default_value = 18.5
        elif 'championship' in league_lower:
            default_value = 75.0
        elif 'eredivisie' in league_lower:
            default_value = 55.0
        elif 'liga portugal' in league_lower or 'primeira liga' in league_lower:
            default_value = 45.0
        else:
            default_value = 25.0
        
        print(f"⚠️ {team_name} için gerçek veri yok, lig ortalaması kullanılıyor: €{default_value}M")
        return default_value
    
    # Hiçbir şey yoksa
    print(f"⚠️ {team_name} için veri bulunamadı, varsayılan: €20M")
    return 20.0


def update_team_value_cache(team_name: str, value: float):
    """Manuel olarak takım değeri ekle/güncelle"""
    team_lower = team_name.lower().strip()
    REAL_TEAM_VALUES[team_lower] = value
    print(f"✅ {team_name} değeri güncellendi: €{value}M")


def get_all_turkish_teams_values() -> Dict[str, float]:
    """Tüm Türk takımlarının güncel değerlerini döndür"""
    turkish_teams = {
        'Galatasaray': 285.30,
        'Fenerbahçe': 270.15,
        'Beşiktaş': 178.65,
        'Trabzonspor': 95.40,
        'Başakşehir': 55.25,
        'Göztepe': 22.85,
        'Samsunspor': 31.20,
        'Konyaspor': 24.15,
        'Antalyaspor': 22.40,
        'Kasımpaşa': 19.75,
        'Alanyaspor': 18.90,
        'Kayserispor': 17.35,
        'Rizespor': 15.80,
        'Eyüpspor': 14.25,
        'Hatayspor': 16.50,
        'Sivasspor': 18.20,
        'Gaziantep': 13.70,
        'Adana Demirspor': 19.40,
    }
    return turkish_teams


if __name__ == "__main__":
    print("=" * 60)
    print("GERÇEK PİYASA DEĞERLERİ TESTİ")
    print("=" * 60)
    
    test_teams = [
        ("Galatasaray", "Süper Lig"),
        ("Fenerbahçe", "Süper Lig"),
        ("Beşiktaş", "Süper Lig"),
        ("Göztepe", "Süper Lig"),
        ("Manchester City", "Premier League"),
        ("Real Madrid", "La Liga"),
        ("Bayern Munich", "Bundesliga"),
        ("Barcelona", "La Liga"),
        ("PSG", "Ligue 1")
    ]
    
    for team, league in test_teams:
        value = get_team_market_value(team, league)
        print(f"  → {team}: €{value}M\n")
    
    print("\n" + "=" * 60)
    print("TÜM TÜRK TAKIMLARI")
    print("=" * 60)
    turkish_values = get_all_turkish_teams_values()
    for team, value in sorted(turkish_values.items(), key=lambda x: x[1], reverse=True):
        print(f"  {team}: €{value}M")
