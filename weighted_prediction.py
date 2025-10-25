"""
AĞIRLIKLI SKOR HESAPLAYICI
17 faktörü ağırlıklarla birleştir
"""
from typing import Dict, Tuple
from factor_weights import get_weight_manager


def calculate_weighted_score(factors: Dict[str, float], 
                             league: str = None,
                             match_type: str = None) -> Tuple[float, Dict[str, float]]:
    """
    Faktörleri ağırlıklarla çarparak toplam skor hesapla
    
    Args:
        factors: Faktör değerleri (her biri 0-1 arası normalize edilmiş)
        league: Lig adı (opsiyonel)
        match_type: Maç tipi (opsiyonel)
    
    Returns:
        (toplam_skor, faktör_detayları)
    """
    weight_manager = get_weight_manager()
    weights = weight_manager.get_weights(league, match_type)
    
    # Her faktörün ağırlıklı katkısını hesapla
    weighted_contributions = {}
    total_score = 0.0
    
    for factor_name, factor_value in factors.items():
        if factor_name in weights:
            weight = weights[factor_name]
            contribution = factor_value * weight
            weighted_contributions[factor_name] = contribution
            total_score += contribution
    
    return total_score, weighted_contributions


def normalize_factor_value(value: float, min_val: float = 0.0, 
                          max_val: float = 100.0) -> float:
    """
    Faktör değerini 0-1 arasına normalize et
    """
    if max_val == min_val:
        return 0.5
    
    normalized = (value - min_val) / (max_val - min_val)
    return max(0.0, min(1.0, normalized))


def calculate_win_probability(team1_score: float, team2_score: float) -> Tuple[float, float, float]:
    """
    İki takımın skorundan kazanma olasılıklarını hesapla
    
    Returns:
        (team1_win_prob, draw_prob, team2_win_prob)
    """
    total = team1_score + team2_score
    
    if total == 0:
        return (0.33, 0.34, 0.33)
    
    # Basit oran hesabı
    team1_ratio = team1_score / total
    team2_ratio = team2_score / total
    
    # Kazanma olasılıkları (beraberlik %20-30 arası)
    draw_prob = 0.25  # Sabit beraberlik olasılığı
    
    remaining = 1.0 - draw_prob
    team1_win = team1_ratio * remaining
    team2_win = team2_ratio * remaining
    
    return (
        round(team1_win * 100, 1),
        round(draw_prob * 100, 1),
        round(team2_win * 100, 1)
    )


def explain_weighted_prediction(team1_name: str, team2_name: str,
                                team1_factors: Dict[str, float],
                                team2_factors: Dict[str, float],
                                league: str = None,
                                match_type: str = None) -> Dict:
    """
    Ağırlıklı tahmin açıklaması
    """
    # Skorları hesapla
    team1_score, team1_contributions = calculate_weighted_score(
        team1_factors, league, match_type
    )
    team2_score, team2_contributions = calculate_weighted_score(
        team2_factors, league, match_type
    )
    
    # Kazanma olasılıkları
    team1_win, draw, team2_win = calculate_win_probability(team1_score, team2_score)
    
    # Tahmin
    if team1_win > team2_win:
        prediction = team1_name
        confidence = team1_win
    elif team2_win > team1_win:
        prediction = team2_name
        confidence = team2_win
    else:
        prediction = "Beraberlik"
        confidence = draw
    
    # En etkili faktörler
    all_contributions = {}
    for factor in team1_contributions.keys():
        diff = team1_contributions.get(factor, 0) - team2_contributions.get(factor, 0)
        all_contributions[factor] = diff
    
    top_factors = sorted(
        all_contributions.items(),
        key=lambda x: abs(x[1]),
        reverse=True
    )[:5]
    
    return {
        'prediction': prediction,
        'confidence': confidence,
        'probabilities': {
            'team1_win': team1_win,
            'draw': draw,
            'team2_win': team2_win
        },
        'scores': {
            'team1': round(team1_score, 2),
            'team2': round(team2_score, 2)
        },
        'top_factors': [
            {
                'name': factor,
                'impact': round(impact, 3),
                'favors': team1_name if impact > 0 else team2_name
            }
            for factor, impact in top_factors
        ],
        'league': league,
        'match_type': match_type
    }


# Test
if __name__ == "__main__":
    print("="*70)
    print("🧪 AĞIRLIKLI SKOR HESAPLAMA TEST")
    print("="*70)
    
    # Örnek faktör değerleri (0-1 arası normalize)
    galatasaray_factors = {
        'elo_diff': 0.75,  # GS daha güçlü
        'league_position': 0.9,  # 1. sıra
        'form': 0.85,
        'h2h': 0.6,
        'home_advantage': 1.0,  # Ev sahibi
        'motivation': 0.8,
        'fatigue': 0.7,
        'recent_performance': 0.8,
        'injuries': 0.9,  # Az sakatlık
        'match_importance': 0.95,  # Derbi
        'xg_performance': 0.8,
        'weather': 0.5,
        'referee': 0.5,
        'betting_odds': 0.7,
        'tactical_matchup': 0.75,
        'transfer_impact': 0.8,
        'squad_experience': 0.85
    }
    
    fenerbahce_factors = {
        'elo_diff': 0.25,  # FB daha zayıf (bu faktörde)
        'league_position': 0.8,  # 2. sıra
        'form': 0.75,
        'h2h': 0.4,
        'home_advantage': 0.0,  # Deplasman
        'motivation': 0.9,  # Yüksek motivasyon
        'fatigue': 0.6,
        'recent_performance': 0.7,
        'injuries': 0.7,
        'match_importance': 0.95,
        'xg_performance': 0.75,
        'weather': 0.5,
        'referee': 0.5,
        'betting_odds': 0.3,
        'tactical_matchup': 0.7,
        'transfer_impact': 0.75,
        'squad_experience': 0.8
    }
    
    # Test 1: Normal ağırlıklar
    print("\n1️⃣ NORMAL AĞIRLIKLAR")
    print("-"*70)
    result = explain_weighted_prediction(
        "Galatasaray", "Fenerbahce",
        galatasaray_factors, fenerbahce_factors
    )
    
    print(f"🏆 Tahmin: {result['prediction']}")
    print(f"📊 Güven: %{result['confidence']}")
    print(f"📈 Olasılıklar:")
    print(f"   GS: %{result['probabilities']['team1_win']}")
    print(f"   X:  %{result['probabilities']['draw']}")
    print(f"   FB: %{result['probabilities']['team2_win']}")
    print(f"⚖️ Skorlar: GS {result['scores']['team1']} - FB {result['scores']['team2']}")
    
    print(f"\n🔝 En Etkili Faktörler:")
    for i, factor in enumerate(result['top_factors'], 1):
        print(f"   {i}. {factor['name']:20s} {factor['impact']:+.3f} → {factor['favors']}")
    
    # Test 2: Süper Lig + Derbi ağırlıkları
    print("\n2️⃣ SÜPER LİG + DERBİ AĞIRLIKLARI")
    print("-"*70)
    result2 = explain_weighted_prediction(
        "Galatasaray", "Fenerbahce",
        galatasaray_factors, fenerbahce_factors,
        league="Süper Lig",
        match_type="derby"
    )
    
    print(f"🏆 Tahmin: {result2['prediction']}")
    print(f"📊 Güven: %{result2['confidence']}")
    print(f"📈 Olasılıklar:")
    print(f"   GS: %{result2['probabilities']['team1_win']}")
    print(f"   X:  %{result2['probabilities']['draw']}")
    print(f"   FB: %{result2['probabilities']['team2_win']}")
    print(f"⚖️ Skorlar: GS {result2['scores']['team1']} - FB {result2['scores']['team2']}")
    
    print(f"\n🔝 En Etkili Faktörler (Derbi):")
    for i, factor in enumerate(result2['top_factors'], 1):
        print(f"   {i}. {factor['name']:20s} {factor['impact']:+.3f} → {factor['favors']}")
    
    # Farkı göster
    print("\n3️⃣ AĞIRLIK SİSTEMİNİN ETKİSİ")
    print("-"*70)
    print(f"Normal Tahmin: {result['prediction']} (%{result['confidence']})")
    print(f"Derbi Tahmin:  {result2['prediction']} (%{result2['confidence']})")
    print(f"\nFark: Güven %{abs(result2['confidence'] - result['confidence']):.1f} değişti")
    
    print("\n" + "="*70)
    print("✅ TEST TAMAMLANDI!")
    print("="*70)
