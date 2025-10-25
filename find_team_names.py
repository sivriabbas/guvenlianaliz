"""
API'DE DOĞRU TAKIM İSİMLERİNİ BUL
"""
import requests

API_KEY = "6336fb21e17dea87880d3b133132a13f"
BASE_URL = "https://v3.football.api-sports.io"

headers = {
    'x-rapidapi-host': 'v3.football.api-sports.io',
    'x-rapidapi-key': API_KEY
}

# Galatasaray ara
print("🔍 Galatasaray arıyorum...")
response = requests.get(f"{BASE_URL}/teams?search=Galatasaray", headers=headers)
if response.status_code == 200:
    data = response.json()
    teams = data.get('response', [])
    print(f"  Bulunan takımlar ({len(teams)} adet):")
    for team in teams[:5]:
        print(f"    • ID: {team['team']['id']}, İsim: {team['team']['name']}")

# Fenerbahçe ara
print("\n🔍 Fenerbahçe arıyorum...")
response = requests.get(f"{BASE_URL}/teams?search=Fenerbahce", headers=headers)
if response.status_code == 200:
    data = response.json()
    teams = data.get('response', [])
    print(f"  Bulunan takımlar ({len(teams)} adet):")
    for team in teams[:5]:
        print(f"    • ID: {team['team']['id']}, İsim: {team['team']['name']}")
