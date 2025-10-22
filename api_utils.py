# -*- coding: utf-8 -*-
# api_utils.py

import requests
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime, date
import json
import os
import yaml

# Streamlit'i optional yap (GitHub Actions için)
try:
    import streamlit as st
    HAS_STREAMLIT = True
except ImportError:
    HAS_STREAMLIT = False
    # Dummy cache decorator for non-streamlit environments
    def cache_data(ttl=None):
        def decorator(func):
            return func
        return decorator
    
    class st:
        cache_data = staticmethod(cache_data)
        session_state = {}

# --- API LİMİT KONTROL MEKANİZMASI ---

USAGE_FILE = 'user_usage.json'
TIER_LIMITS = {
    'ücretli': 1500,
    'ücretsiz': 150
}

# Admin action log is stored inside the usage file under the key '_admin_log' as a list of entries
ADMIN_LOG_KEY = '_admin_log'

def get_api_limit_for_user(tier: str) -> int:
    """Kullanıcının seviyesine göre API limitini döner."""
    # Varsayılan olarak bilinmeyen bir tier için ücretsiz tier limiti uygulanır
    return TIER_LIMITS.get(tier, TIER_LIMITS['ücretsiz'])

def get_current_usage(username: str) -> Dict[str, Any]:
    """Kullanıcının mevcut API kullanım verisini dosyadan okur. CACHE YOK - Her zaman güncel veri."""
    today_str = str(date.today())
    month_str = date.today().strftime('%Y-%m')
    if not os.path.exists(USAGE_FILE):
        return {'date': today_str, 'count': 0, 'month': month_str, 'monthly_count': 0}

    try:
        with open(USAGE_FILE, 'r', encoding='utf-8') as f:
            usage_data = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        usage_data = {}

    user_data = usage_data.get(username, {})

    # Tarih değişti mi kontrol et (gece 00:00'da reset)
    if user_data.get('date') != today_str:
        # Günlük sayacı sıfırla ve dosyaya yaz
        user_data['date'] = today_str
        user_data['count'] = 0
        usage_data[username] = user_data
        _write_usage_file(usage_data)

    # Ay değişti mi kontrol et
    if user_data.get('month') != month_str:
        # Aylık sayacı sıfırla
        user_data['month'] = month_str
        user_data['monthly_count'] = 0
        usage_data[username] = user_data
        _write_usage_file(usage_data)

    user_data.setdefault('count', 0)
    user_data.setdefault('monthly_count', 0)
    user_data.setdefault('month', month_str)

    return user_data

def update_usage(username: str, current_data: Dict[str, Any]):
    """Kullanıcının API kullanım sayacını günceller ve dosyaya yazar."""
    try:
        with open(USAGE_FILE, 'r', encoding='utf-8') as f:
            usage_data = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        usage_data = {}

    # Preserve limit overrides containers if present
    limits = usage_data.get('_limits', {})
    monthly_limits = usage_data.get('_monthly_limits', {})

    usage_data[username] = current_data
    if limits:
        usage_data['_limits'] = limits
    if monthly_limits:
        usage_data['_monthly_limits'] = monthly_limits

    with open(USAGE_FILE, 'w', encoding='utf-8') as f:
        json.dump(usage_data, f, indent=4, ensure_ascii=False)


def _read_usage_file() -> Dict[str, Any]:
    try:
        with open(USAGE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {}


def _write_usage_file(data: Dict[str, Any]):
    with open(USAGE_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def get_pending_notification(username: str) -> Optional[Dict[str, str]]:
    """Kullanıcının bekleyen bildirimini getirir."""
    try:
        data = _read_usage_file()
        notifications = data.get('_pending_notifications', {})
        return notifications.get(username)
    except Exception:
        return None


def clear_pending_notification(username: str):
    """Kullanıcının bildirimini temizler."""
    try:
        data = _read_usage_file()
        notifications = data.get('_pending_notifications', {})
        if username in notifications:
            del notifications[username]
            data['_pending_notifications'] = notifications
            _write_usage_file(data)
    except Exception:
        pass


def ensure_user_limits(username: str, tier: str):
    """Ensure that a user has an explicit per-user daily limit in the usage file.
    If not present, set it to the tier default (ücretsiz/ücretli).
    Returns the effective daily limit that was set or already present.
    """
    data = _read_usage_file()
    limits = data.get('_limits', {})
    if username in limits:
        return limits[username]
    # assign default based on tier
    default = get_api_limit_for_user(tier)
    limits[username] = int(default)
    data['_limits'] = limits
    # ensure a usage record exists for the user so UI can show counts
    user = data.get(username, {})
    user.setdefault('date', str(date.today()))
    user.setdefault('count', 0)
    user.setdefault('month', date.today().strftime('%Y-%m'))
    user.setdefault('monthly_count', 0)
    data[username] = user
    _write_usage_file(data)
    return default


def set_user_daily_limit(username: str, limit: int):
    data = _read_usage_file()
    limits = data.get('_limits', {})
    prev_limit = limits.get(username)
    limits[username] = int(limit)
    data['_limits'] = limits
    
    # Kullanıcıya pending notification ekle
    if '_pending_notifications' not in data:
        data['_pending_notifications'] = {}
    data['_pending_notifications'][username] = {
        'message': f'⚠️ API haklarınızda değişiklik yapıldı! Yeni günlük limitiniz: {int(limit)}. Lütfen çıkış yapıp yeniden giriş yapın.',
        'type': 'limit_change'
    }
    
    # Eğer mevcut günlük sayaç limitin üzerinde ise clamp et
    user = data.get(username, {})
    if user:
        try:
            current_count = int(user.get('count', 0))
            if current_count > int(limit):
                user['count'] = int(limit)
                data[username] = user
        except Exception:
            pass
    _write_usage_file(data)
    # Log admin action (best-effort). If running inside Streamlit, read current admin username.
    try:
        admin_user = st.session_state.get('username') if HAS_STREAMLIT and hasattr(st, 'session_state') else 'system'
    except Exception:
        admin_user = 'system'
    try:
        log_admin_action(admin_user, 'set_user_daily_limit', username, {'prev_limit': prev_limit, 'new_limit': int(limit)})
    except Exception:
        pass


def set_user_monthly_limit(username: str, limit: int):
    data = _read_usage_file()
    mlimits = data.get('_monthly_limits', {})
    prev_mlimit = mlimits.get(username)
    mlimits[username] = int(limit)
    data['_monthly_limits'] = mlimits
    
    # Kullanıcıya pending notification ekle
    if '_pending_notifications' not in data:
        data['_pending_notifications'] = {}
    data['_pending_notifications'][username] = {
        'message': f'⚠️ API haklarınızda değişiklik yapıldı! Yeni aylık limitiniz: {int(limit)}. Lütfen çıkış yapıp yeniden giriş yapın.',
        'type': 'limit_change'
    }
    
    # Eğer mevcut aylık sayaç limitin üzerinde ise clamp et
    user = data.get(username, {})
    if user:
        try:
            current_monthly = int(user.get('monthly_count', 0))
            if current_monthly > int(limit):
                user['monthly_count'] = int(limit)
                data[username] = user
        except Exception:
            pass
    _write_usage_file(data)
    try:
        admin_user = st.session_state.get('username') if HAS_STREAMLIT and hasattr(st, 'session_state') else 'system'
    except Exception:
        admin_user = 'system'
    try:
        log_admin_action(admin_user, 'set_user_monthly_limit', username, {'prev_limit': prev_mlimit, 'new_limit': int(limit)})
    except Exception:
        pass


def log_admin_action(admin: str, action: str, target: str, details: Optional[Dict[str, Any]] = None):
    """Append an admin action entry into the usage file under '_admin_log'.
    Entry fields: ts (UTC iso), admin, action, target, details
    """
    try:
        data = _read_usage_file()
        log = data.get(ADMIN_LOG_KEY, [])
        entry = {
            'ts': datetime.utcnow().isoformat() + 'Z',
            'admin': admin or 'system',
            'action': action,
            'target': target,
            'details': details or {}
        }
        # prepend newest first
        log.insert(0, entry)
        data[ADMIN_LOG_KEY] = log
        _write_usage_file(data)
    except Exception:
        # Best-effort; ignore logging failures
        pass


def get_admin_log(limit: int = 50) -> List[Dict[str, Any]]:
    """Admin log'unu döner. Cache YOK."""
    data = _read_usage_file()
    log = data.get(ADMIN_LOG_KEY, [])
    return log[:limit]


def reset_daily_usage(username: str = None):
    """Sadece belirtilen kullanıcı için veya tüm kullanıcılar için günlük sayacı sıfırlar. Cache YOK."""
    data = _read_usage_file()
    today_str = str(date.today())
    if username:
        u = data.get(username, {})
        u['date'] = today_str
        u['count'] = 0
        data[username] = u
    else:
        for k, v in list(data.items()):
            if k.startswith('_'):
                continue
            v['date'] = today_str
            v['count'] = 0
            data[k] = v
    _write_usage_file(data)


def get_usage_summary() -> Dict[str, Dict[str, Any]]:
    """Tüm kullanıcıların günlük ve aylık kullanım özetini döner. Cache YOK - Her zaman güncel."""
    data = _read_usage_file()
    summary = {}
    for k, v in data.items():
        if k.startswith('_'):
            continue
        summary[k] = {
            'date': v.get('date'),
            'count': v.get('count', 0),
            'month': v.get('month'),
            'monthly_count': v.get('monthly_count', 0),
            'daily_limit': data.get('_limits', {}).get(k, None),
            'monthly_limit': data.get('_monthly_limits', {}).get(k, None),
        }
    return summary


def _get_ip_assignments() -> Dict[str, str]:
    """Return the mapping of IP -> username from the usage file (best-effort)."""
    data = _read_usage_file()
    return data.get('_ip_assignments', {})


def _set_ip_assignment(ip: str, username: str):
    """Assign an IP to a username (overwrites existing assignment)."""
    data = _read_usage_file()
    ipmap = data.get('_ip_assignments', {})
    ipmap[ip] = username
    data['_ip_assignments'] = ipmap
    _write_usage_file(data)


def register_ip_assignment(username: str, tier: str, ip: str) -> Tuple[bool, Optional[str]]:
    """Try to assign API access for `username` tied to `ip`."""
    if not ip:
        return False, 'IP belirtilmediği için atama yapılamadı.'
    data = _read_usage_file()
    ipmap = data.get('_ip_assignments', {})
    existing = ipmap.get(ip)
    if existing and existing != username:
        return False, f"Bu IP zaten '{existing}' kullanıcısına ait."
    # assign and ensure user has limits
    ipmap[ip] = username
    data['_ip_assignments'] = ipmap
    try:
        ensure_user_limits(username, tier)
    except Exception:
        pass
    _write_usage_file(data)
    return True, None


def get_client_ip() -> str:
    """Best-effort client IP detection."""
    try:
        import streamlit as _st
        qp = getattr(_st, 'query_params', None)
        if qp:
            v = qp.get('client_ip', [''])[0]
            if v:
                return v
    except Exception:
        pass

    for key in ('HTTP_X_FORWARDED_FOR', 'X_FORWARDED_FOR', 'HTTP_CLIENT_IP', 'REMOTE_ADDR'):
        v = os.environ.get(key) or os.environ.get(key.lower())
        if v:
            return v.split(',')[0].strip()

    try:
        r = requests.get('https://api.ipify.org?format=json', timeout=3)
        j = r.json()
        return j.get('ip', '')
    except Exception:
        return ''

def set_user_tier(username: str, tier: str) -> Tuple[bool, Optional[str]]:
    """
    Kullanıcının seviyesini (tier) hem config.yaml'de hem de günlük limitini user_usage.json'da günceller.
    """
    if tier not in TIER_LIMITS:
        return False, f"Geçersiz seviye: {tier}. Sadece 'ücretli' veya 'ücretsiz' olabilir."

    # Adım 1: config.yaml dosyasındaki tier'ı güncelle
    try:
        config_path = 'config.yaml'
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        if username in config['credentials']['usernames']:
            config['credentials']['usernames'][username]['tier'] = tier
            with open(config_path, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, allow_unicode=True)
        else:
            return False, f"Kullanıcı '{username}' config.yaml'de bulunamadı."
    except Exception as e:
        return False, f"config.yaml güncellenirken hata oluştu: {e}"

    # Adım 2: user_usage.json dosyasındaki günlük limiti yeni seviyeye göre ayarla
    try:
        new_limit = TIER_LIMITS[tier]
        set_user_daily_limit(username, new_limit)
    except Exception as e:
        return False, f"Günlük limit ayarlanırken hata oluştu: {e}"

    return True, f"Kullanıcı {username} başarıyla {tier} seviyesine geçirildi ve limiti {new_limit} olarak ayarlandı."

def check_api_limit() -> Tuple[bool, Optional[str]]:
    """API isteği yapmadan önce limiti kontrol eder. SAYACI ARTIRMAZ - sadece kontrol eder."""
    try:
        if not HAS_STREAMLIT:
            return True, None  # GitHub Actions için bypass
        if "authentication_status" not in st.session_state or not st.session_state["authentication_status"]:
            return False, "API isteği yapmak için giriş yapmalısınız."
    except Exception:
        # Eğer session_state erişimi başarısız olursa (ön yükleme sırasında), isteği geçir
        return True, None

    username = st.session_state.get('username')
    admin_users = st.session_state.get('admin_users', [])
    
    # Admin kullanıcılar için sınırsız erişim
    if username and username in admin_users:
        return True, None
    
    tier = st.session_state.get('tier', 'ücretsiz')
    
    data = _read_usage_file()
    per_user_limit = data.get('_limits', {}).get(username)
    
    # Eğer per_user_limit 0 ise varsayılana dön, değilse kullan
    if per_user_limit is not None and per_user_limit > 0:
        limit = per_user_limit
    else:
        limit = get_api_limit_for_user(tier)

    monthly_limit = data.get('_monthly_limits', {}).get(username)
    if monthly_limit is not None and monthly_limit == 0:
        monthly_limit = None  # 0 = limitsiz

    user_usage = get_current_usage(username)

    if user_usage['count'] >= limit:
        return False, f"Günlük API istek limitinize ({limit}) ulaştınız. Yarın tekrar deneyin."

    if monthly_limit is not None and user_usage.get('monthly_count', 0) >= monthly_limit:
        return False, f"Aylık API istek limitinize ({monthly_limit}) ulaştınız. Sonraki ay tekrar deneyin."

    # SADECE KONTROL ET, ARTIRMA!
    return True, None

def increment_api_usage() -> None:
    """API kullanım sayacını artırır - sadece gerçek HTTP isteği yapıldığında çağrılmalı."""
    try:
        if not HAS_STREAMLIT:
            return  # GitHub Actions için bypass
        if "authentication_status" not in st.session_state or not st.session_state["authentication_status"]:
            return
    except Exception:
        return

    username = st.session_state.get('username')
    admin_users = st.session_state.get('admin_users', [])
    
    # Admin için de sayacı artır ama limit kontrolü yapma
    if username:
        # Önce mevcut kullanımı al (tarih kontrolü yapılacak)
        user_usage = get_current_usage(username)
        
        # Sayacı artır
        user_usage['count'] = user_usage.get('count', 0) + 1
        user_usage['monthly_count'] = user_usage.get('monthly_count', 0) + 1
        
        # Dosyaya yaz
        update_usage(username, user_usage)
        
        # Debug: Konsola yazdır
        print(f"[API USAGE] {username}: Günlük={user_usage['count']}, Aylık={user_usage['monthly_count']}")

def make_api_request(api_key: str, base_url: str, endpoint: str, params: Dict[str, Any], skip_limit: bool = False) -> Tuple[Optional[Any], Optional[str]]:
    if not skip_limit:
        can_request, error_message = check_api_limit()
        if not can_request:
            return None, error_message

    headers = {'x-rapidapi-key': api_key, 'x-rapidapi-host': "v3.football.api-sports.io"}
    url = f"{base_url}/{endpoint}"
    try:
        response = requests.get(url, headers=headers, params=params, timeout=20)
        
        # GERÇEK HTTP İSTEĞİ YAPILDI - SAYACI ARTIR
        if not skip_limit:
            increment_api_usage()
        
        response.raise_for_status()
        api_data = response.json()
        if api_data.get('errors') and (isinstance(api_data['errors'], dict) and api_data['errors']) or (isinstance(api_data['errors'], list) and len(api_data['errors']) > 0):
            return None, f"API Hatası: {api_data['errors']}"
        return api_data.get('response', []), None
    except requests.exceptions.HTTPError as http_err:
        return None, f"HTTP Hatası: {http_err}. API Anahtarınızı veya aboneliğinizi kontrol edin."
    except requests.exceptions.RequestException as req_err:
        return None, f"Bağlantı Hatası: {req_err}"

@st.cache_data(ttl=86400)
def get_player_stats(api_key: str, base_url: str, player_id: int, season: int) -> Tuple[Optional[List[Dict[str, Any]]], Optional[str]]:
    return make_api_request(api_key, base_url, "players", {'id': player_id, 'season': season})

@st.cache_data(ttl=86400)
def get_fixture_details(api_key: str, base_url: str, fixture_id: int) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    response, error = make_api_request(api_key, base_url, "fixtures", {'id': fixture_id})
    if error:
        return None, error
    return (response[0], None) if response else (None, "Maç detayı bulunamadı.")

@st.cache_data(ttl=86400)
def get_referee_stats(api_key: str, base_url: str, referee_id: int, season: int) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    response, error = make_api_request(api_key, base_url, "referees", {'id': referee_id, 'season': season})
    if error:
        return None, error
    return (response[0], None) if response else (None, "Hakem istatistiği bulunamadı.")

@st.cache_data(ttl=86400)
def get_team_statistics(api_key: str, base_url: str, team_id: int, league_id: int, season: int) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    params = {'team': team_id, 'league': league_id, 'season': season}
    return make_api_request(api_key, base_url, "teams/statistics", params)

@st.cache_data(ttl=3600)
def get_team_last_matches_stats(api_key: str, base_url: str, team_id: int, limit: int = 10) -> Optional[List[Dict]]:
    params = {'team': team_id, 'last': limit, 'status': 'FT'}
    matches, error = make_api_request(api_key, base_url, "fixtures", params)
    if error or not matches:
        return None
    stats_list = []
    # API'den en yeni maçlar başta gelir, reversed() KULLANMA
    for match in matches:
        try:
            is_home = match['teams']['home']['id'] == team_id
            score_for = match['score']['fulltime']['home' if is_home else 'away']
            score_against = match['score']['fulltime']['away' if is_home else 'home']
            if score_for is None or score_against is None: continue
            stats_list.append({'location': 'home' if is_home else 'away', 'goals_for': score_for, 'goals_against': score_against})
        except (KeyError, TypeError):
            continue
    return stats_list

@st.cache_data(ttl=3600)
def get_fixture_odds(api_key: str, base_url: str, fixture_id: int) -> Tuple[Optional[List[Dict[str, Any]]], Optional[str]]:
    """1X2 oranlarını (Match Winner) çeker"""
    params = {'fixture': fixture_id, 'bet': 1}
    return make_api_request(api_key, base_url, "odds", params)

@st.cache_data(ttl=3600)
def get_fixture_detailed_odds(api_key: str, base_url: str, fixture_id: int) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """
    Tüm bahis türlerini çeker ve kategorize eder.
    Returns: {
        'match_winner': [...],  # 1X2
        'over_under': [...],    # 2.5 Üst/Alt
        'btts': [...],          # Karşılıklı Gol
        'handicap': [...],      # Handikap
        'first_half': [...],    # İlk Yarı
        'corners': [...],       # Kornerler
        'cards': [...]          # Kartlar
    }
    """
    # Tüm bahis türlerini çek (bet parametresi olmadan)
    params = {'fixture': fixture_id}
    response, error = make_api_request(api_key, base_url, "odds", params)
    
    if error:
        return None, f"API hatası: {error}"
    
    if not response:
        return None, "Bu maç için hiçbir bahis oranı bulunamadı."
    
    categorized_odds = {
        'match_winner': [],
        'over_under': [],
        'btts': [],
        'handicap': [],
        'first_half': [],
        'corners': [],
        'cards': []
    }
    
    try:
        if not response[0].get('bookmakers'):
            return None, "Bahis şirketleri verisi bulunamadı."
        
        bookmakers = response[0].get('bookmakers', [])
        total_bets_found = 0
        
        for bookmaker in bookmakers:
            bets = bookmaker.get('bets', [])
            
            for bet in bets:
                bet_name = bet.get('name', '').lower()
                total_bets_found += 1
                
                # Kategorizasyon (daha geniş pattern matching)
                if 'match winner' in bet_name or ('winner' in bet_name and 'half' not in bet_name):
                    categorized_odds['match_winner'].append({
                        'bookmaker': bookmaker.get('name'),
                        'bet_name': bet.get('name'),
                        'values': bet.get('values', [])
                    })
                elif 'over/under' in bet_name or 'goals over/under' in bet_name or 'total goals' in bet_name:
                    categorized_odds['over_under'].append({
                        'bookmaker': bookmaker.get('name'),
                        'bet_name': bet.get('name'),
                        'values': bet.get('values', [])
                    })
                elif 'both teams score' in bet_name or 'btts' in bet_name or 'gg/ng' in bet_name:
                    categorized_odds['btts'].append({
                        'bookmaker': bookmaker.get('name'),
                        'bet_name': bet.get('name'),
                        'values': bet.get('values', [])
                    })
                elif 'handicap' in bet_name or 'spread' in bet_name or 'asian handicap' in bet_name:
                    categorized_odds['handicap'].append({
                        'bookmaker': bookmaker.get('name'),
                        'bet_name': bet.get('name'),
                        'values': bet.get('values', [])
                    })
                elif '1st half' in bet_name or 'first half' in bet_name or 'half time' in bet_name or 'ht' in bet_name:
                    categorized_odds['first_half'].append({
                        'bookmaker': bookmaker.get('name'),
                        'bet_name': bet.get('name'),
                        'values': bet.get('values', [])
                    })
                elif 'corner' in bet_name:
                    categorized_odds['corners'].append({
                        'bookmaker': bookmaker.get('name'),
                        'bet_name': bet.get('name'),
                        'values': bet.get('values', [])
                    })
                elif 'card' in bet_name or 'yellow' in bet_name or 'booking' in bet_name:
                    categorized_odds['cards'].append({
                        'bookmaker': bookmaker.get('name'),
                        'bet_name': bet.get('name'),
                        'values': bet.get('values', [])
                    })
        
        # Debug bilgisi için
        debug_msg = f"Toplam {total_bets_found} bahis türü bulundu. "
        debug_msg += f"Kategoriler: "
        for cat, data in categorized_odds.items():
            if data:
                debug_msg += f"{cat}({len(data)}), "
        
        return categorized_odds, None
    
    except (KeyError, IndexError, TypeError) as e:
        return None, f"Oran verisi işlenirken hata: {str(e)}"

@st.cache_data(ttl=86400) 
def get_fixture_injuries(api_key: str, base_url: str, fixture_id: int) -> Tuple[Optional[List[Dict[str, Any]]], Optional[str]]:
    return make_api_request(api_key, base_url, "injuries", {'fixture': fixture_id})

@st.cache_data(ttl=86400)
def get_squad_player_stats(api_key: str, base_url: str, team_id: int, season: int) -> Tuple[Optional[List[Dict[str, Any]]], Optional[str]]:
    return make_api_request(api_key, base_url, "players", {'team': team_id, 'season': season})

@st.cache_data(ttl=86400)
def get_league_standings(api_key: str, base_url: str, league_id: int, season: int) -> Tuple[Optional[List[Dict[str, Any]]], Optional[str]]:
    response, error = make_api_request(api_key, base_url, "standings", {'league': league_id, 'season': season})
    if error: return None, error
    if response and response[0]['league']['standings']:
        return response[0]['league']['standings'][0], None
    return None, None

@st.cache_data(ttl=86400)
def get_all_current_leagues(api_key: str, base_url: str) -> Tuple[List[Dict[str, Any]], Optional[str]]:
    response, error = make_api_request(api_key, base_url, "leagues", {'current': 'true'}, skip_limit=True)
    if error or not response:
        return [], error

    leagues: List[Dict[str, Any]] = []
    seen_ids = set()
    for item in response:
        try:
            league_info = item.get('league') or {}
            league_id = league_info.get('id')
            league_name = league_info.get('name')
            if not league_id or not league_name or league_id in seen_ids:
                continue

            seasons = item.get('seasons') or []
            current_season = next((s.get('year') for s in seasons if s.get('current')), None)
            country_info = item.get('country') or {}
            country_name = country_info.get('name') or 'Uluslararası'

            leagues.append({
                'id': league_id,
                'name': league_name,
                'country': country_name,
                'type': league_info.get('type'),
                'season': current_season,
                'display': f"{country_name} - {league_name}"
            })
            seen_ids.add(league_id)
        except Exception:
            continue

    leagues.sort(key=lambda l: (l.get('country') or '', l.get('name') or ''))
    return leagues, None

@st.cache_data(ttl=86400)
def get_h2h_matches(api_key: str, base_url: str, team_a_id: int, team_b_id: int, limit: int) -> Tuple[Optional[List[Dict[str, Any]]], Optional[str]]:
    return make_api_request(api_key, base_url, "fixtures/headtohead", {'h2h': f"{team_a_id}-{team_b_id}", 'last': limit})

@st.cache_data(ttl=604800)
def get_teams_by_league(api_key: str, base_url: str, league_id: int, season: int) -> Tuple[Optional[List[Dict[str, Any]]], Optional[str]]:
    return make_api_request(api_key, base_url, "teams", {'league': league_id, 'season': season})

@st.cache_data(ttl=86400)
def get_team_form_sequence(api_key: str, base_url: str, team_id: int, limit: int = 10) -> Optional[List[Dict[str, str]]]:
    matches, error = make_api_request(api_key, base_url, "fixtures", {'team': team_id, 'last': limit, 'status': 'FT'})
    if error or not matches:
        return None
    form_data = []
    for match in reversed(matches):
        try:
            score_home = match['score']['fulltime']['home']
            score_away = match['score']['fulltime']['away']
            if score_home is None or score_away is None: continue
            is_home_team = match['teams']['home']['id'] == team_id
            opponent_name = match['teams']['away']['name'] if is_home_team else match['teams']['home']['name']
            score_str = f"{score_home}-{score_away}" if is_home_team else f"{score_away}-{score_home}"
            result = 'B'
            if (is_home_team and score_home > score_away) or (not is_home_team and score_away > score_home):
                result = 'G'
            elif (is_home_team and score_home < score_away) or (not is_home_team and score_away < score_home):
                result = 'M'
            form_data.append({'result': result, 'opponent': opponent_name, 'score': score_str})
        except (KeyError, TypeError):
            continue
    return form_data

@st.cache_data(ttl=86400)
def get_team_league_info(api_key: str, base_url: str, team_id: int) -> Optional[Dict[str, Any]]:
    response, error = make_api_request(api_key, base_url, "leagues", {'team': team_id, 'current': 'true'})
    if error or not response: return None
    league, seasons = response[0]['league'], response[0]['seasons']
    season = next((s['year'] for s in seasons if s['current']), seasons[-1]['year'])
    return {'league_id': league['id'], 'season': season}

def find_upcoming_fixture(api_key: str, base_url: str, team_a_id: int, team_b_id: int, season: int) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    fixtures, error = make_api_request(api_key, base_url, "fixtures", {'team': team_a_id, 'season': season, 'status': 'NS'})
    if error: return None, error
    if fixtures:
        for f in fixtures:
            if f['teams']['home']['id'] == team_b_id or f['teams']['away']['id'] == team_b_id:
                return f, None
    return None, None
    
def get_next_team_fixture(api_key: str, base_url: str, team_id: int) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """Belirtilen takımın sıradaki ilk maçını getirir."""
    response, error = make_api_request(api_key, base_url, "fixtures", {'team': team_id, 'next': 1})
    if error:
        return None, error
    return (response[0], None) if response else (None, "Takımın yaklaşan maçı bulunamadı.")

@st.cache_data(ttl=3600)  # 1 saat cache - aynı gün içinde tekrar API çağrısı yapma
def get_fixtures_by_date(api_key: str, base_url: str, selected_league_ids: List[int], selected_date: date, bypass_limit_check: bool = False) -> Tuple[List[Dict[str, Any]], Optional[str]]:
    all_fixtures, error_messages = [], []
    date_str = selected_date.strftime('%Y-%m-%d')
    season = selected_date.year if selected_date.month > 6 else selected_date.year - 1
    
    for league_id in selected_league_ids:
        # Status filtresi kullanma - sadece tarih ve lig bazlı çek
        params = {'date': date_str, 'league': league_id, 'season': season}
        response, error = make_api_request(api_key, base_url, "fixtures", params, skip_limit=bypass_limit_check)
        if error:
            error_messages.append(f"Lig ID {league_id}: {error}")
            continue
        if response:
            for f in response:
                try:
                    fixture_status = f['fixture']['status']['short']
                    fixture_data = {
                        'match_id': f['fixture']['id'], 
                        'time': datetime.fromtimestamp(f['fixture']['timestamp']).strftime('%H:%M'),
                        'home_name': f['teams']['home']['name'], 
                        'home_id': f['teams']['home']['id'],
                        'home_logo': f['teams']['home'].get('logo', ''),
                        'away_name': f['teams']['away']['name'], 
                        'away_id': f['teams']['away']['id'],
                        'away_logo': f['teams']['away'].get('logo', ''),
                        'league_name': f['league']['name']
                    }
                    # Biten maçlar için skor ekle
                    if fixture_status == 'FT' and f.get('score', {}).get('fulltime'):
                        fixture_data['actual_score'] = f"{f['score']['fulltime']['home']} - {f['score']['fulltime']['away']}"
                        fixture_data['winner_home'] = f['teams']['home']['winner']
                    all_fixtures.append(fixture_data)
                except (KeyError, TypeError): 
                    continue
    final_error = "\n".join(error_messages) if error_messages else None
    return sorted(all_fixtures, key=lambda x: (x['league_name'], x['time'])), final_error

def get_team_id(api_key: str, base_url: str, team_input: str) -> Optional[Dict[str, Any]]:
    response, error = make_api_request(api_key, base_url, "teams", {'search': team_input} if not team_input.isdigit() else {'id': team_input})
    if error:
        st.sidebar.error(error); return None
    if response:
        # Eğer birden fazla sonuç varsa, popüler takımları üste getir
        if len(response) > 1:
            # Popüler takım ID'leri (app.py'den)
            popular_teams = [
                645, 646, 644, 643, 3569,  # Türkiye
                33, 34, 40, 42, 47, 49, 50,  # İngiltere
                529, 530, 531, 532, 533,  # İspanya
                489, 487, 488, 492, 496, 500, 505,  # İtalya
                157, 165, 173, 168, 172,  # Almanya
                85, 79, 81, 80, 84,  # Fransa
            ]
            
            def get_priority(team_item):
                team_id = team_item['team']['id']
                if team_id in popular_teams:
                    return popular_teams.index(team_id)
                return 999
            
            # Popülerliğe göre sırala
            response.sort(key=get_priority)
        
        team = response[0]['team']
        st.sidebar.success(f"✅ Bulunan: {team['name']} ({team['id']})")
        return {'id': team['id'], 'name': team['name'], 'logo': team.get('logo')}
    st.sidebar.error(f"❌ Takım bulunamadı: '{team_input}'"); return None

@st.cache_data(ttl=18000)
def get_team_injuries(api_key: str, base_url: str, team_id: int, fixture_id: Optional[int] = None) -> Tuple[Optional[List[Dict[str, Any]]], Optional[str]]:
    """
    Takımın sakatlık ve ceza bilgilerini getirir.
    Returns: (injuries_list, error_message)
    """
    params = {'team': team_id}
    if fixture_id:
        params['fixture'] = fixture_id
    
    response, error = make_api_request(api_key, base_url, "injuries", params)
    if error:
        return None, error
    
    if not response:
        return [], None  # Sakatlık yok
    
    # Aktif sakatlıkları filtrele
    active_injuries = []
    for injury in response:
        player = injury.get('player', {})
        injury_type = injury.get('player', {}).get('type', 'Unknown')
        injury_reason = injury.get('player', {}).get('reason', 'N/A')
        
        active_injuries.append({
            'player_name': player.get('name', 'Unknown'),
            'player_id': player.get('id'),
            'type': injury_type,
            'reason': injury_reason
        })
    
    return active_injuries, None