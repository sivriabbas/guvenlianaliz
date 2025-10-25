#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hava Durumu Analiz Modülü
OpenWeatherMap API entegrasyonu ile maç günü hava koşulları analizi
"""

import requests
from typing import Dict, Optional
from datetime import datetime

# OpenWeatherMap API (Ücretsiz - günde 1000 istek)
# Gerçek key için: https://openweathermap.org/api (5 dakikada ücretsiz kayıt)
API_KEY = None  # Buraya key eklenebilir
BASE_URL = "http://api.openweathermap.org/data/2.5/weather"

# Simülasyon modu (API key yoksa gerçekçi mevsim/şehir bazlı tahmin)
SIMULATION_MODE = True

# Stadyum lokasyonları (Lat, Lon)
STADIUM_LOCATIONS = {
    # Türkiye Süper Lig
    'galatasaray': {'lat': 41.1039, 'lon': 29.0100, 'city': 'İstanbul'},
    'fenerbahçe': {'lat': 40.9890, 'lon': 29.0350, 'city': 'İstanbul'},
    'fenerbahce': {'lat': 40.9890, 'lon': 29.0350, 'city': 'İstanbul'},
    'beşiktaş': {'lat': 41.0390, 'lon': 29.0080, 'city': 'İstanbul'},
    'besiktas': {'lat': 41.0390, 'lon': 29.0080, 'city': 'İstanbul'},
    'trabzonspor': {'lat': 40.9950, 'lon': 39.7663, 'city': 'Trabzon'},
    'başakşehir': {'lat': 41.0745, 'lon': 28.8094, 'city': 'İstanbul'},
    'basaksehir': {'lat': 41.0745, 'lon': 28.8094, 'city': 'İstanbul'},
    
    # Premier League
    'manchester city': {'lat': 53.4831, 'lon': -2.2004, 'city': 'Manchester'},
    'manchester united': {'lat': 53.4631, 'lon': -2.2913, 'city': 'Manchester'},
    'liverpool': {'lat': 53.4308, 'lon': -2.9608, 'city': 'Liverpool'},
    'arsenal': {'lat': 51.5549, 'lon': -0.1084, 'city': 'London'},
    'chelsea': {'lat': 51.4817, 'lon': -0.1910, 'city': 'London'},
    'tottenham': {'lat': 51.6042, 'lon': -0.0665, 'city': 'London'},
    
    # La Liga
    'real madrid': {'lat': 40.4530, 'lon': -3.6883, 'city': 'Madrid'},
    'barcelona': {'lat': 41.3809, 'lon': 2.1228, 'city': 'Barcelona'},
    'atletico madrid': {'lat': 40.4362, 'lon': -3.5995, 'city': 'Madrid'},
    
    # Bundesliga
    'bayern munich': {'lat': 48.2188, 'lon': 11.6247, 'city': 'Munich'},
    'borussia dortmund': {'lat': 51.4925, 'lon': 7.4517, 'city': 'Dortmund'},
    
    # Serie A
    'juventus': {'lat': 45.1097, 'lon': 7.6410, 'city': 'Turin'},
    'inter': {'lat': 45.4781, 'lon': 9.1240, 'city': 'Milan'},
    'ac milan': {'lat': 45.4781, 'lon': 9.1240, 'city': 'Milan'},
}

def get_weather_data(team_name: str) -> Optional[Dict]:
    """
    Takımın stadyumu için hava durumu verisi al (Gerçek API veya Simülasyon)
    """
    team_lower = team_name.lower()
    
    # Stadyum lokasyonunu bul
    location = STADIUM_LOCATIONS.get(team_lower)
    
    if not location:
        print(f"⚠️ {team_name} için stadyum lokasyonu bulunamadı!")
        return None
    
    # API key varsa gerçek veri çek
    if API_KEY and not SIMULATION_MODE:
        try:
            params = {
                'lat': location['lat'],
                'lon': location['lon'],
                'appid': API_KEY,
                'units': 'metric',
                'lang': 'tr'
            }
            
            response = requests.get(BASE_URL, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                return {
                    'city': location['city'],
                    'temperature': round(data['main']['temp'], 1),
                    'feels_like': round(data['main']['feels_like'], 1),
                    'humidity': data['main']['humidity'],
                    'weather_main': data['weather'][0]['main'],
                    'weather_description': data['weather'][0]['description'],
                    'wind_speed': round(data['wind']['speed'] * 3.6, 1),
                    'clouds': data['clouds']['all'],
                    'rain': data.get('rain', {}).get('1h', 0),
                    'snow': data.get('snow', {}).get('1h', 0),
                    'visibility': data.get('visibility', 10000) / 1000
                }
                
        except Exception as e:
            print(f"API hatası, simülasyon moduna geçiliyor: {e}")
    
    # Simülasyon: Gerçekçi mevsim ve şehir bazlı tahmin
    import random
    current_month = datetime.now().month
    
    # Şehir bazlı iklim profilleri
    climate_profiles = {
        'İstanbul': {'base_temp': 15, 'rain_prob': 0.3, 'seasonal_var': 15},
        'Trabzon': {'base_temp': 14, 'rain_prob': 0.5, 'seasonal_var': 12},
        'Manchester': {'base_temp': 10, 'rain_prob': 0.6, 'seasonal_var': 10},
        'London': {'base_temp': 11, 'rain_prob': 0.5, 'seasonal_var': 10},
        'Madrid': {'base_temp': 16, 'rain_prob': 0.2, 'seasonal_var': 18},
        'Barcelona': {'base_temp': 17, 'rain_prob': 0.2, 'seasonal_var': 15},
        'Munich': {'base_temp': 9, 'rain_prob': 0.4, 'seasonal_var': 16},
        'Dortmund': {'base_temp': 10, 'rain_prob': 0.45, 'seasonal_var': 14},
        'Turin': {'base_temp': 13, 'rain_prob': 0.3, 'seasonal_var': 17},
        'Milan': {'base_temp': 14, 'rain_prob': 0.3, 'seasonal_var': 16},
        'Liverpool': {'base_temp': 10, 'rain_prob': 0.65, 'seasonal_var': 9},
    }
    
    city = location['city']
    profile = climate_profiles.get(city, {'base_temp': 15, 'rain_prob': 0.3, 'seasonal_var': 15})
    
    # Mevsimsel ayarlama (Ekim ayı)
    season_adjust = {1: -10, 2: -8, 3: -3, 4: 2, 5: 7, 6: 12, 
                     7: 15, 8: 14, 9: 8, 10: 3, 11: -2, 12: -7}
    
    temp_adjust = season_adjust.get(current_month, 0)
    temperature = profile['base_temp'] + temp_adjust + random.uniform(-3, 3)
    
    # Yağmur tahmini
    rain = 0
    if random.random() < profile['rain_prob']:
        rain = random.uniform(0.5, 5.0)
    
    # Rüzgar
    wind_speed = random.uniform(5, 25)
    
    # Nem (yağmur varsa yüksek)
    humidity = 60 + (rain * 5) + random.randint(-10, 10)
    humidity = max(40, min(95, humidity))
    
    weather_conditions = ['açık', 'parçalı bulutlu', 'bulutlu', 'hafif yağmurlu'] if rain < 2 else ['yağmurlu', 'sağanak yağışlı']
    
    return {
        'city': city,
        'temperature': round(temperature, 1),
        'feels_like': round(temperature - (wind_speed / 10), 1),
        'humidity': int(humidity),
        'weather_main': 'Rain' if rain > 0 else 'Clear',
        'weather_description': random.choice(weather_conditions),
        'wind_speed': round(wind_speed, 1),
        'clouds': int(rain * 20) if rain > 0 else random.randint(10, 60),
        'rain': round(rain, 1),
        'snow': 0,
        'visibility': 10 if rain < 2 else max(3, 10 - rain)
    }


def calculate_weather_impact(home_team: str, away_team: str) -> Dict:
    """
    Hava durumu etkisini hesapla
    """
    
    # Ev sahibi stadyum havasını al
    weather = get_weather_data(home_team)
    
    if not weather:
        return {
            'available': False,
            'impact': 0,
            'note': 'Hava durumu verisi yok'
        }
    
    impact_factors = []
    total_impact = 0
    
    # 1. Sıcaklık Etkisi
    temp = weather['temperature']
    if temp < 0:
        total_impact -= 5
        impact_factors.append(f"❄️ Çok soğuk ({temp}°C) - Oyun kalitesi düşer")
    elif temp < 10:
        total_impact -= 2
        impact_factors.append(f"🥶 Soğuk ({temp}°C) - Hafif olumsuz etki")
    elif temp > 35:
        total_impact -= 4
        impact_factors.append(f"🔥 Aşırı sıcak ({temp}°C) - Yorgunluk artar")
    elif 15 <= temp <= 25:
        total_impact += 2
        impact_factors.append(f"☀️ İdeal sıcaklık ({temp}°C)")
    else:
        impact_factors.append(f"🌡️ Normal sıcaklık ({temp}°C)")
    
    # 2. Yağmur Etkisi
    rain = weather['rain']
    if rain > 5:
        total_impact -= 8
        impact_factors.append(f"🌧️ Şiddetli yağmur ({rain} mm/h) - Pas kalitesi düşer")
    elif rain > 2:
        total_impact -= 4
        impact_factors.append(f"🌦️ Yağmurlu ({rain} mm/h) - Zemin kaygan")
    elif rain > 0:
        total_impact -= 2
        impact_factors.append(f"☔ Hafif yağmur ({rain} mm/h)")
    
    # 3. Kar Etkisi
    snow = weather['snow']
    if snow > 0:
        total_impact -= 10
        impact_factors.append(f"❄️ Karlı hava ({snow} mm/h) - Ciddi etki!")
    
    # 4. Rüzgar Etkisi
    wind_speed = weather['wind_speed']
    if wind_speed > 50:
        total_impact -= 6
        impact_factors.append(f"🌪️ Fırtına ({wind_speed} km/h) - Top kontrolü zor")
    elif wind_speed > 30:
        total_impact -= 3
        impact_factors.append(f"💨 Rüzgarlı ({wind_speed} km/h)")
    elif wind_speed < 10:
        impact_factors.append(f"🍃 Sakin hava ({wind_speed} km/h)")
    
    # 5. Görüş Mesafesi
    visibility = weather['visibility']
    if visibility < 1:
        total_impact -= 7
        impact_factors.append(f"🌫️ Sisli ({visibility} km) - Görüş kısıtlı")
    elif visibility < 5:
        total_impact -= 3
        impact_factors.append(f"🌁 Hafif sisli ({visibility} km)")
    
    # 6. Nem Oranı
    humidity = weather['humidity']
    if humidity > 85:
        total_impact -= 2
        impact_factors.append(f"💧 Yüksek nem (%{humidity}) - Zorlu koşullar")
    
    # Normalize (-10 ile +5 arası)
    total_impact = max(-10, min(5, total_impact))
    
    # Kategori belirle
    if total_impact <= -7:
        category = "ÇOK KÖTÜ"
        advantage = "Ev sahibi avantajı azalır"
    elif total_impact <= -3:
        category = "KÖTÜ"
        advantage = "Teknik takım dezavantajlı"
    elif total_impact <= 0:
        category = "ORTA"
        advantage = "Nötr etki"
    else:
        category = "İYİ"
        advantage = "Kaliteli futbol beklenir"
    
    return {
        'available': True,
        'city': weather['city'],
        'temperature': weather['temperature'],
        'feels_like': weather['feels_like'],
        'weather': weather['weather_description'].title(),
        'rain': weather['rain'],
        'snow': weather['snow'],
        'wind_speed': weather['wind_speed'],
        'humidity': weather['humidity'],
        'visibility': weather['visibility'],
        'impact_score': total_impact,
        'category': category,
        'advantage': advantage,
        'factors': impact_factors,
        'prediction_impact': round(total_impact / 2, 1)  # Tahmine etkisi (%0-5 arası)
    }


if __name__ == "__main__":
    print("=" * 70)
    print("HAVA DURUMU ANALİZ TESTİ")
    print("=" * 70)
    
    # Test 1: İstanbul (Galatasaray)
    print("\n🌤️ Galatasaray Stadyumu (İstanbul):")
    weather = get_weather_data("Galatasaray")
    if weather:
        print(f"  Sıcaklık: {weather['temperature']}°C (Hissedilen: {weather['feels_like']}°C)")
        print(f"  Hava: {weather['weather_description']}")
        print(f"  Rüzgar: {weather['wind_speed']} km/h")
        print(f"  Nem: {weather['humidity']}%")
        print(f"  Yağış: {weather['rain']} mm/h")
    
    # Test 2: Manchester
    print("\n🌧️ Manchester City (Manchester):")
    weather = get_weather_data("Manchester City")
    if weather:
        print(f"  Sıcaklık: {weather['temperature']}°C")
        print(f"  Hava: {weather['weather_description']}")
        print(f"  Rüzgar: {weather['wind_speed']} km/h")
    
    # Test 3: Etki Analizi
    print("\n📊 Galatasaray vs Fenerbahçe - Hava Etkisi:")
    impact = calculate_weather_impact("Galatasaray", "Fenerbahçe")
    if impact['available']:
        print(f"  Kategori: {impact['category']}")
        print(f"  Etki Skoru: {impact['impact_score']}/10")
        print(f"  Tahmin Etkisi: {impact['prediction_impact']}%")
        print(f"  Faktörler:")
        for factor in impact['factors']:
            print(f"    - {factor}")
