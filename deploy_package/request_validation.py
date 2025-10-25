"""
Request Validation & Input Sanitization - Phase 8.B (Simplified)
=================================================================
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
import re
import html


# ============================================================================
# INPUT SANITIZATION
# ============================================================================

def sanitize_string(text: str, max_length: int = 1000) -> str:
    """String sanitization - XSS koruması"""
    if not text:
        return text
    
    text = text[:max_length]
    text = html.escape(text)
    
    dangerous = ['<', '>', '"', "'", '&', ';']
    for char in dangerous:
        text = text.replace(char, '')
    
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def sanitize_sql(text: str) -> str:
    """SQL injection koruması"""
    if not text:
        return text
    
    sql_keywords = ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'DROP', 'UNION', 'EXEC']
    text_upper = text.upper()
    
    for keyword in sql_keywords:
        if keyword in text_upper:
            raise ValueError(f"SQL keyword tespit edildi: {keyword}")
    
    return text


def sanitize_path(path: str) -> str:
    """Path traversal koruması"""
    if not path:
        return path
    
    if '..' in path or '~' in path:
        raise ValueError("Path traversal denemesi")
    
    if not re.match(r'^[a-zA-Z0-9._-]+$', path):
        raise ValueError("Geçersiz path karakteri")
    
    return path


# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class PredictionRequest(BaseModel):
    """ML Tahmin request"""
    home_team: str = Field(..., min_length=2, max_length=100)
    away_team: str = Field(..., min_length=2, max_length=100)
    league: str = Field(..., min_length=2, max_length=100)
    model_name: Optional[str] = None
    team1_factors: Optional[Dict[str, float]] = None
    team2_factors: Optional[Dict[str, float]] = None


class EnsemblePredictionRequest(BaseModel):
    """Ensemble tahmin request"""
    home_team: str = Field(..., min_length=2, max_length=100)
    away_team: str = Field(..., min_length=2, max_length=100)
    league: str = Field(..., min_length=2, max_length=100)
    ensemble_method: str = "weighted"
    team1_factors: Optional[Dict[str, float]] = None
    team2_factors: Optional[Dict[str, float]] = None


class APIKeyCreateRequest(BaseModel):
    """API key oluşturma"""
    name: str = Field(..., min_length=3, max_length=100)
    owner: Optional[str] = None
    expires_days: Optional[int] = None
    rate_limit: int = 100
    permissions: str = "basic"


class ResultCheckRequest(BaseModel):
    """Sonuç kontrol"""
    mode: str = "auto"
    start_date: Optional[str] = None
    end_date: Optional[str] = None


class AutoRetrainRequest(BaseModel):
    """Auto-retrain"""
    model: str = "all"
    force: bool = False
    check_only: bool = False


class OptimizeWeightsRequest(BaseModel):
    """Weight optimization"""
    mode: str = "general"
    n_trials: int = 100
    league: Optional[str] = None


# ============================================================================
# RESPONSE MODELS
# ============================================================================

class ErrorResponse(BaseModel):
    """Hata response"""
    success: bool = False
    error: str
    detail: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


class SuccessResponse(BaseModel):
    """Başarı response"""
    success: bool = True
    message: str
    data: Optional[Dict[str, Any]] = None


# ============================================================================
# ERROR HANDLERS
# ============================================================================

from fastapi.responses import JSONResponse

async def validation_exception_handler(request, exc):
    """Validation error handler"""
    errors = []
    for error in exc.errors():
        errors.append({
            "field": " -> ".join(str(x) for x in error["loc"]),
            "message": error["msg"]
        })
    
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "error": "Validation Error",
            "errors": errors,
            "timestamp": datetime.now().isoformat()
        }
    )


async def http_exception_handler(request, exc):
    """HTTP error handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": str(exc.detail),
            "timestamp": datetime.now().isoformat()
        }
    )


async def general_exception_handler(request, exc):
    """Genel error handler"""
    print(f"❌ Error: {type(exc).__name__}: {str(exc)}")
    
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal Server Error",
            "detail": str(exc),
            "timestamp": datetime.now().isoformat()
        }
    )


# ============================================================================
# VALIDATION HELPERS
# ============================================================================

def validate_team_name(team: str) -> str:
    """Takım adı validation"""
    if not team or len(team) < 2:
        raise ValueError("Geçersiz takım adı")
    return sanitize_string(team, 100)


def validate_league_name(league: str) -> str:
    """Lig adı validation"""
    if not league or len(league) < 2:
        raise ValueError("Geçersiz lig adı")
    return sanitize_string(league, 100)


def validate_model_name(model: str) -> str:
    """Model adı validation"""
    valid_prefixes = ['xgb', 'lgb', 'ensemble']
    if not any(model.startswith(p) for p in valid_prefixes):
        raise ValueError("Geçersiz model adı")
    return sanitize_path(model)


if __name__ == "__main__":
    print("\n✅ Request Validation System - Ready!")
    print("✅ Pydantic V2 Compatible")
    print("✅ Input Sanitization: XSS, SQL, Path")
    print("✅ Error Handlers: 3 types")
    print("✅ Validation Helpers: Ready\n")
