"""
FAKTÖR AĞIRLIK YÖNETİCİSİ
17 faktör için optimize edilmiş ağırlıklar
"""
import json
import os
from typing import Dict, List, Tuple
from datetime import datetime

# Varsayılan ağırlıklar (eşit başlangıç)
DEFAULT_WEIGHTS = {
    # BASE FACTORS (8 faktör)
    'elo_diff': 1.0,
    'league_position': 1.0,
    'form': 1.0,
    'h2h': 1.0,
    'home_advantage': 1.0,
    'motivation': 1.0,
    'fatigue': 1.0,
    'recent_performance': 1.0,
    
    # PHASE 1 FACTORS (3 faktör)
    'injuries': 1.0,
    'match_importance': 1.0,
    'xg_performance': 1.0,
    
    # PHASE 2 FACTORS (3 faktör)
    'weather': 1.0,
    'referee': 1.0,
    'betting_odds': 1.0,
    
    # PHASE 3 FACTORS (3 faktör)
    'tactical_matchup': 1.0,
    'transfer_impact': 1.0,
    'squad_experience': 1.0
}

# Lig bazlı ağırlık profilleri
LEAGUE_PROFILES = {
    'Süper Lig': {
        'home_advantage': 1.3,  # Türkiye'de ev sahibi avantajı yüksek
        'motivation': 1.2,      # Derbiler çok önemli
        'referee': 1.1,         # Hakem faktörü önemli
        'tactical_matchup': 0.9 # Taktiksel disiplin daha az
    },
    'Premier League': {
        'form': 1.2,           # Form çok önemli
        'xg_performance': 1.2, # xG verisi güvenilir
        'squad_experience': 1.1,
        'weather': 0.8         # Hava durumu daha az etkili
    },
    'La Liga': {
        'tactical_matchup': 1.3,  # Taktik çok önemli
        'elo_diff': 1.2,          # Kalite farkı belirleyici
        'home_advantage': 1.1
    },
    'Bundesliga': {
        'form': 1.3,              # Form en önemli
        'xg_performance': 1.2,
        'squad_experience': 1.1
    },
    'Serie A': {
        'tactical_matchup': 1.4,  # En taktiksel lig
        'home_advantage': 1.2,
        'elo_diff': 1.1
    }
}

# Maç tipi bazlı ağırlıklar
MATCH_TYPE_PROFILES = {
    'derby': {
        'motivation': 1.5,     # Derbi motivasyonu kritik
        'h2h': 1.3,           # Geçmiş performans önemli
        'home_advantage': 1.2,
        'form': 0.8,          # Form daha az önemli
        'elo_diff': 0.7       # Kalite farkı silinir
    },
    'title_race': {
        'form': 1.4,          # Form kritik
        'match_importance': 1.3,
        'injuries': 1.2,      # Sakatlıklar çok önemli
        'squad_experience': 1.2
    },
    'relegation': {
        'motivation': 1.4,    # Düşme korkusu
        'match_importance': 1.3,
        'home_advantage': 1.2,
        'form': 1.1
    },
    'mid_table': {
        'form': 1.2,
        'elo_diff': 1.1,
        'home_advantage': 1.1
    }
}


class FactorWeightManager:
    """
    Faktör ağırlıklarını yöneten sınıf
    """
    
    def __init__(self, weights_file: str = "factor_weights.json"):
        self.weights_file = weights_file
        self.weights = self.load_weights()
        self.history = []
    
    def load_weights(self) -> Dict[str, float]:
        """Ağırlıkları dosyadan yükle veya varsayılanları kullan"""
        if os.path.exists(self.weights_file):
            try:
                with open(self.weights_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('weights', DEFAULT_WEIGHTS.copy())
            except Exception as e:
                print(f"⚠️ Ağırlıklar yüklenemedi: {e}")
                return DEFAULT_WEIGHTS.copy()
        return DEFAULT_WEIGHTS.copy()
    
    def save_weights(self):
        """Ağırlıkları dosyaya kaydet"""
        try:
            data = {
                'weights': self.weights,
                'last_updated': datetime.now().isoformat(),
                'version': '1.0'
            }
            with open(self.weights_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"✅ Ağırlıklar kaydedildi: {self.weights_file}")
        except Exception as e:
            print(f"❌ Ağırlıklar kaydedilemedi: {e}")
    
    def get_weights(self, league: str = None, match_type: str = None) -> Dict[str, float]:
        """
        Lig ve maç tipine göre optimize edilmiş ağırlıklar
        """
        # Başlangıç ağırlıkları
        weights = self.weights.copy()
        
        # Lig bazlı ayarlamalar
        if league and league in LEAGUE_PROFILES:
            profile = LEAGUE_PROFILES[league]
            for factor, multiplier in profile.items():
                if factor in weights:
                    weights[factor] *= multiplier
        
        # Maç tipi bazlı ayarlamalar
        if match_type and match_type in MATCH_TYPE_PROFILES:
            profile = MATCH_TYPE_PROFILES[match_type]
            for factor, multiplier in profile.items():
                if factor in weights:
                    weights[factor] *= multiplier
        
        return weights
    
    def normalize_weights(self, weights: Dict[str, float]) -> Dict[str, float]:
        """Ağırlıkları normalize et (toplam = faktör sayısı)"""
        total = sum(weights.values())
        factor_count = len(weights)
        
        if total > 0:
            normalized = {k: (v / total) * factor_count for k, v in weights.items()}
            return normalized
        return weights
    
    def update_weight(self, factor: str, new_weight: float):
        """Tek bir faktörün ağırlığını güncelle"""
        if factor in self.weights:
            old_weight = self.weights[factor]
            self.weights[factor] = new_weight
            
            # Geçmişe kaydet
            self.history.append({
                'timestamp': datetime.now().isoformat(),
                'factor': factor,
                'old_weight': old_weight,
                'new_weight': new_weight
            })
            
            print(f"✅ {factor}: {old_weight:.2f} → {new_weight:.2f}")
        else:
            print(f"❌ Bilinmeyen faktör: {factor}")
    
    def update_multiple_weights(self, weight_updates: Dict[str, float]):
        """Birden fazla ağırlığı güncelle"""
        for factor, weight in weight_updates.items():
            self.update_weight(factor, weight)
        self.save_weights()
    
    def get_factor_importance(self) -> List[Tuple[str, float]]:
        """Faktörleri önem sırasına göre listele"""
        sorted_weights = sorted(
            self.weights.items(),
            key=lambda x: x[1],
            reverse=True
        )
        return sorted_weights
    
    def print_weights(self, league: str = None, match_type: str = None):
        """Ağırlıkları güzel formatta yazdır"""
        weights = self.get_weights(league, match_type)
        
        print("\n" + "="*70)
        print("⚖️ FAKTÖR AĞIRLIKLARI")
        if league:
            print(f"📍 Lig: {league}")
        if match_type:
            print(f"🎯 Maç Tipi: {match_type}")
        print("="*70)
        
        # Kategorilere ayır
        categories = {
            'BASE FACTORS': [k for k in DEFAULT_WEIGHTS.keys() if k in ['elo_diff', 'league_position', 'form', 'h2h', 'home_advantage', 'motivation', 'fatigue', 'recent_performance']],
            'PHASE 1': [k for k in DEFAULT_WEIGHTS.keys() if k in ['injuries', 'match_importance', 'xg_performance']],
            'PHASE 2': [k for k in DEFAULT_WEIGHTS.keys() if k in ['weather', 'referee', 'betting_odds']],
            'PHASE 3': [k for k in DEFAULT_WEIGHTS.keys() if k in ['tactical_matchup', 'transfer_impact', 'squad_experience']]
        }
        
        for category, factors in categories.items():
            print(f"\n📊 {category}:")
            for factor in factors:
                if factor in weights:
                    weight = weights[factor]
                    bar = "█" * int(weight * 10)
                    print(f"  {factor:20s} {weight:5.2f} {bar}")
        
        print("\n" + "="*70)
    
    def detect_match_type(self, team1_pos: int, team2_pos: int, 
                          league_total_teams: int = 20) -> str:
        """
        Maç tipini otomatik tespit et
        """
        # Derby kontrolü (aynı şehir - basit version)
        # Gerçek implementasyonda takım isimlerinden tespit edilir
        
        # Şampiyonluk yarışı (ilk 4)
        if team1_pos <= 4 and team2_pos <= 4:
            return 'title_race'
        
        # Düşme mücadelesi (son 4)
        relegation_zone = league_total_teams - 3
        if team1_pos >= relegation_zone or team2_pos >= relegation_zone:
            return 'relegation'
        
        # Orta sıra
        return 'mid_table'
    
    def suggest_weights_for_match(self, league: str, team1_pos: int, 
                                  team2_pos: int) -> Dict[str, float]:
        """
        Belirli bir maç için optimize edilmiş ağırlıklar öner
        """
        match_type = self.detect_match_type(team1_pos, team2_pos)
        weights = self.get_weights(league, match_type)
        
        return {
            'weights': weights,
            'match_type': match_type,
            'league': league
        }


# Singleton instance
_weight_manager = None

def get_weight_manager() -> FactorWeightManager:
    """Global weight manager instance"""
    global _weight_manager
    if _weight_manager is None:
        _weight_manager = FactorWeightManager()
    return _weight_manager


# Test
if __name__ == "__main__":
    print("="*70)
    print("🧪 FAKTÖR AĞIRLIK SİSTEMİ TEST")
    print("="*70)
    
    manager = get_weight_manager()
    
    # Test 1: Varsayılan ağırlıklar
    print("\n1️⃣ VARSAYILAN AĞIRLIKLAR")
    manager.print_weights()
    
    # Test 2: Süper Lig ağırlıkları
    print("\n2️⃣ SÜPER LİG AĞIRLIKLARI")
    manager.print_weights(league='Süper Lig')
    
    # Test 3: Derbi maçı
    print("\n3️⃣ DERBİ MAÇI AĞIRLIKLARI")
    manager.print_weights(league='Süper Lig', match_type='derby')
    
    # Test 4: Şampiyonluk yarışı
    print("\n4️⃣ ŞAMPİYONLUK YARIŞI (Premier League)")
    manager.print_weights(league='Premier League', match_type='title_race')
    
    # Test 5: Maç tipi tespiti
    print("\n5️⃣ MAÇ TİPİ TESPİTİ")
    print("-"*70)
    
    test_matches = [
        (1, 2, "1. vs 2. → Şampiyonluk"),
        (18, 19, "18. vs 19. → Düşme"),
        (8, 12, "8. vs 12. → Orta sıra"),
    ]
    
    for pos1, pos2, desc in test_matches:
        match_type = manager.detect_match_type(pos1, pos2)
        print(f"  {desc}: {match_type}")
    
    # Test 6: Önem sıralaması
    print("\n6️⃣ FAKTÖR ÖNEM SIRALAMASI (Süper Lig, Derbi)")
    print("-"*70)
    weights = manager.get_weights('Süper Lig', 'derby')
    sorted_factors = sorted(weights.items(), key=lambda x: x[1], reverse=True)
    
    for i, (factor, weight) in enumerate(sorted_factors[:10], 1):
        print(f"  {i:2d}. {factor:20s} {weight:5.2f}")
    
    print("\n" + "="*70)
    print("✅ TEST TAMAMLANDI!")
    print("="*70)
