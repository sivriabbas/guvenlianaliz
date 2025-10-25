#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Galatasaray Puan Durumu Test
"""

from real_time_data import get_team_by_name, get_team_current_season_stats

print("=" * 70)
print("GALATASARAY 2025 SEZON VERİLERİ TESTİ")
print("=" * 70)

# Galatasaray bilgilerini al
gs_info = get_team_by_name("Galatasaray")
if gs_info:
    print(f"\n✅ Takım Bulundu:")
    print(f"   ID: {gs_info['id']}")
    print(f"   İsim: {gs_info['name']}")
    print(f"   Ülke: {gs_info['country']}")
    print(f"   Stadyum: {gs_info['venue']}")
    
    # Sezon istatistiklerini al
    print(f"\n🔄 2025 Sezon verileri çekiliyor...")
    stats = get_team_current_season_stats(gs_info['id'])
    
    if stats:
        print(f"\n📊 GALATASARAY - {stats['season']} SEZONU")
        print(f"   Lig: {stats['league_name']}")
        print(f"   🏆 SIRA: {stats['position']}. sıra")
        print(f"   ⚽ PUAN: {stats['points']}")
        print(f"   📈 Oynanan: {stats['played']} maç")
        print(f"   ✅ Galibiyet: {stats['wins']}")
        print(f"   🤝 Beraberlik: {stats['draws']}")
        print(f"   ❌ Mağlubiyet: {stats['losses']}")
        print(f"   ⚽ Attığı Gol: {stats['goals_for']}")
        print(f"   🥅 Yediği Gol: {stats['goals_against']}")
        print(f"   📊 Gol Ortalaması: {stats['goals_per_game']}")
        print(f"   🏠 Ev Sahibi Galibiyeti: %{stats['home_win_rate']}")
        print(f"   ✈️ Deplasman Galibiyeti: %{stats['away_win_rate']}")
        print(f"   📝 Form: {stats['form']}")
    else:
        print("\n❌ İstatistikler alınamadı!")
else:
    print("\n❌ Galatasaray bulunamadı!")

# Fenerbahçe de test edelim
print("\n" + "=" * 70)
print("FENERBAHÇE 2025 SEZON VERİLERİ TESTİ")
print("=" * 70)

fb_info = get_team_by_name("Fenerbahçe")
if fb_info:
    print(f"\n✅ Takım Bulundu: {fb_info['name']} (ID: {fb_info['id']})")
    
    stats = get_team_current_season_stats(fb_info['id'])
    if stats:
        print(f"\n📊 FENERBAHÇE - {stats['season']} SEZONU")
        print(f"   🏆 SIRA: {stats['position']}. sıra")
        print(f"   ⚽ PUAN: {stats['points']}")
        print(f"   Oynanan: {stats['played']} maç")
