import json

with open('elo_ratings.json', 'r') as f:
    elo_data = json.load(f)

# Bilinen Türk takım ID'leri
turkish_team_ids = {
    '645': 'Galatasaray',
    '646': 'Fenerbahçe', 
    '644': 'Beşiktaş',
    '643': 'Trabzonspor',
    '619': 'Göztepe',  # Tahmin
    '618': 'Diğer',
    '1565': 'Göztepe SK'  # Alternatif
}

print('Türk Takımları ELO Puanları:')
print('=' * 40)

for team_id, team_name in turkish_team_ids.items():
    if team_id in elo_data:
        rating = elo_data[team_id]['rating']
        last_updated = elo_data[team_id]['last_updated']
        print(f'{team_name}: {rating} ELO (ID: {team_id})')
        print(f'  Son güncelleme: {last_updated}')
    else:
        print(f'{team_name}: ELO verisi yok (ID: {team_id})')

# En yüksek ELO'lu takımları bul
print('\n' + '=' * 40)
print('En Yüksek ELO Puanlı Takımlar:')
print('=' * 40)

# ELO değerlerine göre sırala
sorted_teams = sorted(elo_data.items(), key=lambda x: x[1]['rating'], reverse=True)

for i, (team_id, data) in enumerate(sorted_teams[:20]):
    rating = data['rating']
    print(f'{i+1:2d}. ID {team_id}: {rating} ELO')