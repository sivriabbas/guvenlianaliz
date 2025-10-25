from fastapi import FastAPI, Request, Form, Depends, HTTPException, status, Cookie
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import os
import json
import toml
from datetime import date, datetime
from typing import Optional, Dict, Any, List
import secrets

# Mevcut modüllerinizi import edin
import api_utils
import analysis_logic
import elo_utils
# from comprehensive_analysis import comprehensive_match_analysis

def load_secrets():
    """Secrets.toml dosyasından API anahtarını yükle"""
    try:
        # Railway environment'dan önce dene
        api_key = os.environ.get('API_KEY')
        if api_key:
            return api_key
            
        # Sonra secrets.toml dosyasından dene
        secrets_path = ".streamlit/secrets.toml"
        if os.path.exists(secrets_path):
            with open(secrets_path, 'r', encoding='utf-8') as f:
                secrets_data = toml.load(f)
                return secrets_data.get('API_KEY')
    except Exception as e:
        print(f"Secrets yükleme hatası: {e}")
    return None

app = FastAPI(title="Güvenilir Analiz", description="Futbol Analiz Platformu")

# Static files ve templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Simple session store
active_sessions = {}

def create_session(username: str) -> str:
    """Create a new session"""
    session_id = secrets.token_urlsafe(32)
    active_sessions[session_id] = username
    return session_id

def get_current_user(session_id: str = Cookie(None, alias="session_id")):
    """Get current user from session"""
    if session_id and session_id in active_sessions:
        return active_sessions[session_id]
    return None

def verify_credentials(username: str, password: str) -> bool:
    """Verify user credentials"""
    import yaml
    import bcrypt
    
    try:
        with open('config.yaml', 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        users = config.get('credentials', {}).get('usernames', {})
        user = users.get(username)
        
        if user:
            stored_password = user.get('password', '')
            if stored_password.startswith('$2b$'):
                # bcrypt hash
                return bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8'))
            else:
                # plaintext
                return stored_password == password
    except Exception as e:
        print(f"Auth error: {e}")
    
    return False

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Login page"""
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    """Handle login"""
    if verify_credentials(username, password):
        session_id = create_session(username)
        response = RedirectResponse(url="/", status_code=303)
        response.set_cookie(key="session_id", value=session_id, httponly=True)
        return response
    else:
        return templates.TemplateResponse("login.html", {
            "request": request, 
            "error": "Kullanıcı adı veya şifre hatalı!"
        })

@app.get("/logout")
async def logout():
    """Handle logout"""
    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie(key="session_id")
    return response

@app.get("/", response_class=HTMLResponse)
async def home(request: Request, session_id: str = Cookie(None, alias="session_id")):
    """Ana sayfa"""
    username = get_current_user(session_id)
    if not username:
        return RedirectResponse(url="/login")
    
    # Kullanıcı bilgilerini al
    user_info = {"username": username, "tier": "test", "daily_usage": 0, "monthly_usage": 0}
    
    # Günün maçlarını al (gerçek API)
    today_fixtures = []
    try:
        api_key = load_secrets()
        if api_key:
            fixtures, error = api_utils.get_fixtures_by_date(
                api_key, 
                "https://v3.football.api-sports.io",
                [39, 140, 203],  # Premier, La Liga, Süper Lig
                date.today(),
                bypass_limit_check=True
            )
            today_fixtures = fixtures[:10] if fixtures and not error else []
        
        # API'den veri alamazsak mock data kullan
        if not today_fixtures:
            today_fixtures = [
                {
                    "fixture": {
                        "id": 98765,
                        "date": f"{date.today()}T19:00:00+00:00",
                        "status": {"short": "NS", "long": "Not Started"}
                    },
                    "league": {"name": "Süper Lig", "country": "Turkey"},
                    "teams": {
                        "home": {"name": "Galatasaray", "logo": ""},
                        "away": {"name": "Beşiktaş", "logo": ""}
                    },
                    "goals": {"home": None, "away": None}
                }
            ]
    except Exception as e:
        print(f"Fixture alım hatası: {e}")
        # Hata durumunda mock data
        today_fixtures = [
            {
                "fixture": {
                    "id": 98765,
                    "date": f"{date.today()}T19:00:00+00:00",
                    "status": {"short": "NS", "long": "Not Started"}
                },
                "league": {"name": "Demo Liga", "country": "Demo"},
                "teams": {
                    "home": {"name": "Takım A", "logo": ""},
                    "away": {"name": "Takım B", "logo": ""}
                },
                "goals": {"home": None, "away": None}
            }
        ]
    
    return templates.TemplateResponse("home.html", {
        "request": request,
        "username": username,
        "user_info": user_info,
        "fixtures": today_fixtures
    })

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, session_id: str = Cookie(None, alias="session_id")):
    """Maç panosu"""
    username = get_current_user(session_id)
    if not username:
        return RedirectResponse(url="/login")
        
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "username": username,
        "date": date
    })

@app.post("/analyze")
async def analyze_match(request: Request, team1: str = Form(...), team2: str = Form(...)):
    """Maç analizi endpoint'i"""
    try:
        # Geçici basit analiz
        analysis_result = {
            'success': True,
            'team1': team1,
            'team2': team2,
            'team1_elo': 1500,
            'team2_elo': 1500,
            'team1_form': 'İyi',
            'team2_form': 'Orta',
            'final_prediction': f'{team1} kazanma olasılığı %55',
            'confidence': 0.75
        }
            
        return templates.TemplateResponse("analysis.html", {
            "request": request,
            "analysis_result": analysis_result
        })
        
    except Exception as e:
        print(f"Analiz hatası: {str(e)}")
        import traceback
        traceback.print_exc()
        
        error_result = {
            'success': False,
            'team1': team1,
            'team2': team2,
            'error': f'Analiz sırasında hata oluştu: {str(e)}'
        }
        
        return templates.TemplateResponse("analysis.html", {
            "request": request,
            "analysis_result": error_result
        })

@app.get("/api/fixtures")
async def get_fixtures(
    date_str: str,
    leagues: str,
    session_id: str = Cookie(None, alias="session_id")
):
    """Maç listesi API"""
    username = get_current_user(session_id)
    if not username:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    try:
        selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        league_ids = [int(x) for x in leagues.split(',')]
        
        api_key = load_secrets()
        if not api_key:
            # API anahtarı yoksa mock data döndür
            mock_fixtures = [
                {
                    "fixture": {
                        "id": 12345,
                        "date": f"{date_str}T15:00:00+00:00",
                        "status": {"short": "NS", "long": "Not Started"}
                    },
                    "league": {"id": 203, "name": "Süper Lig", "country": "Turkey"},
                    "teams": {
                        "home": {"name": "Demo Takım A", "logo": ""},
                        "away": {"name": "Demo Takım B", "logo": ""}
                    },
                    "goals": {"home": None, "away": None}
                }
            ]
            return JSONResponse({"fixtures": mock_fixtures})
        
        # Gerçek API çağrısı
        fixtures, error = api_utils.get_fixtures_by_date(
            api_key,
            "https://v3.football.api-sports.io",
            league_ids,
            selected_date,
            bypass_limit_check=True
        )
        
        if error:
            # API hatası varsa mock data döndür
            mock_fixtures = [
                {
                    "fixture": {
                        "id": 12345,
                        "date": f"{date_str}T15:00:00+00:00",
                        "status": {"short": "NS", "long": "Not Started"}
                    },
                    "league": {"id": league_ids[0] if league_ids else 203, "name": "Demo Liga", "country": "Demo"},
                    "teams": {
                        "home": {"name": "Takım A", "logo": ""},
                        "away": {"name": "Takım B", "logo": ""}
                    },
                    "goals": {"home": None, "away": None}
                }
            ]
            return JSONResponse({"fixtures": mock_fixtures, "note": f"API Hatası: {error}"})
            
        return JSONResponse({"fixtures": fixtures or []})
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analysis", response_class=HTMLResponse)
async def analysis(request: Request, session_id: str = Cookie(None, alias="session_id")):
    """Gelişmiş analiz sayfası"""
    username = get_current_user(session_id)
    if not username:
        return RedirectResponse(url="/login")
        
    return templates.TemplateResponse("analysis.html", {
        "request": request,
        "username": username
    })

@app.get("/statistics", response_class=HTMLResponse)
async def statistics(request: Request, session_id: str = Cookie(None, alias="session_id")):
    """İstatistikler sayfası"""
    username = get_current_user(session_id)
    if not username:
        return RedirectResponse(url="/login")
        
    return templates.TemplateResponse("statistics.html", {
        "request": request,
        "username": username
    })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))