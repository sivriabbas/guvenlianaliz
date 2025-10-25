#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Maç Önem Derecesi ve Motivasyon Modülü
"""

from typing import Dict

def calculate_match_importance(
    team1_name: str,
    team2_name: str,
    team1_pos: int,
    team2_pos: int,
    team1_points: int,
    team2_points: int,
    league_name: str,
    total_teams: int = 20
) -> Dict:
    """
    Maç önem derecesini hesapla
    
    Faktörler:
    - Şampiyonluk yarışı
    - Avrupa kupası
    - Küme düşme
    - Derbi
    - Puan yakınlığı
    """
    
    importance_score = 50  # Base importance
    motivation_team1 = 100
    motivation_team2 = 100
    factors = []
    
    # 1. Derbi Kontrolü
    derbies = {
        'galatasaray-fenerbahce': 95,
        'fenerbahce-galatasaray': 95,
        'galatasaray-besiktas': 90,
        'besiktas-galatasaray': 90,
        'fenerbahce-besiktas': 90,
        'besiktas-fenerbahce': 90,
        'trabzonspor-fenerbahce': 85,
        'fenerbahce-trabzonspor': 85,
        'barcelona-real madrid': 95,
        'real madrid-barcelona': 95,
        'manchester united-liverpool': 90,
        'liverpool-manchester united': 90,
        'milan-inter': 90,
        'inter-milan': 90,
    }
    
    derby_key = f"{team1_name.lower()}-{team2_name.lower()}"
    if derby_key in derbies:
        importance_score = derbies[derby_key]
        motivation_team1 += 20
        motivation_team2 += 20
        factors.append("🔥 DERBİ MAÇI")
    
    # 2. Şampiyonluk Yarışı
    if team1_pos <= 3:
        importance_score += 15
        motivation_team1 += 15
        factors.append(f"🏆 {team1_name} Şampiyonluk yarışında")
    
    if team2_pos <= 3:
        importance_score += 15
        motivation_team2 += 15
        factors.append(f"🏆 {team2_name} Şampiyonluk yarışında")
    
    # 3. Avrupa Kupası Sıralaması (4-6. sıra)
    if 4 <= team1_pos <= 6:
        importance_score += 10
        motivation_team1 += 10
        factors.append(f"🌍 {team1_name} Avrupa kupası için")
    
    if 4 <= team2_pos <= 6:
        importance_score += 10
        motivation_team2 += 10
        factors.append(f"🌍 {team2_name} Avrupa kupası için")
    
    # 4. Küme Düşme Mücadelesi (Son 4)
    relegation_zone = total_teams - 3
    if team1_pos >= relegation_zone:
        importance_score += 20
        motivation_team1 += 18
        factors.append(f"⚠️ {team1_name} KÜME DÜŞME TEHLİKESİ")
    
    if team2_pos >= relegation_zone:
        importance_score += 20
        motivation_team2 += 18
        factors.append(f"⚠️ {team2_name} KÜME DÜŞME TEHLİKESİ")
    
    # 5. Puan Yakınlığı
    point_diff = abs(team1_points - team2_points)
    if point_diff <= 3:
        importance_score += 8
        motivation_team1 += 5
        motivation_team2 += 5
        factors.append("📊 Puanlar çok yakın")
    
    # 6. Kafa Kafaya Yarış (Sıra farkı)
    position_diff = abs(team1_pos - team2_pos)
    if position_diff <= 2:
        importance_score += 5
        factors.append("🎯 Sıra yarışı")
    
    # 7. Orta Sıra Takımlar (Düşük motivasyon)
    mid_table_start = 8
    mid_table_end = total_teams - 5
    
    if mid_table_start <= team1_pos <= mid_table_end and mid_table_start <= team2_pos <= mid_table_end:
        importance_score -= 10
        motivation_team1 -= 5
        motivation_team2 -= 5
        factors.append("😴 Orta sıra maçı (Düşük önem)")
    
    # Normalize
    importance_score = max(30, min(100, importance_score))
    motivation_team1 = max(80, min(130, motivation_team1))
    motivation_team2 = max(80, min(130, motivation_team2))
    
    # Kategori belirle
    if importance_score >= 85:
        category = "ÇOK YÜKSEK"
    elif importance_score >= 70:
        category = "YÜKSEK"
    elif importance_score >= 55:
        category = "ORTA"
    else:
        category = "DÜŞÜK"
    
    return {
        'importance_score': round(importance_score, 1),
        'category': category,
        'team1_motivation': round(motivation_team1, 1),
        'team2_motivation': round(motivation_team2, 1),
        'motivation_advantage': team1_name if motivation_team1 > motivation_team2 else team2_name if motivation_team2 > motivation_team1 else "Dengeli",
        'factors': factors,
        'is_derby': len([f for f in factors if 'DERBİ' in f]) > 0,
        'is_relegation_battle': len([f for f in factors if 'KÜME DÜŞME' in f]) > 0,
        'is_title_race': len([f for f in factors if 'Şampiyonluk' in f]) > 0
    }


if __name__ == "__main__":
    print("=" * 60)
    print("MAÇ ÖNEM DERECESİ TESTİ")
    print("=" * 60)
    
    # Test 1: Derbi
    result = calculate_match_importance(
        "Galatasaray", "Fenerbahçe",
        1, 3, 25, 19, "Süper Lig", 18
    )
    print(f"\n🔥 Galatasaray vs Fenerbahçe:")
    print(f"  Önem: {result['category']} ({result['importance_score']}/100)")
    print(f"  Motivasyon: GS {result['team1_motivation']}% - FB {result['team2_motivation']}%")
    print(f"  Faktörler: {', '.join(result['factors'])}")
    
    # Test 2: Küme düşme
    result = calculate_match_importance(
        "Karagümrük", "Eyüpspor",
        17, 18, 5, 3, "Süper Lig", 18
    )
    print(f"\n⚠️ Karagümrük vs Eyüpspor:")
    print(f"  Önem: {result['category']} ({result['importance_score']}/100)")
    print(f"  Motivasyon: KG {result['team1_motivation']}% - EY {result['team2_motivation']}%")
    print(f"  Faktörler: {', '.join(result['factors'])}")
