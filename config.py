"""
Phase 10.C: Production Configuration
Centralized configuration management for production
"""

import os
from typing import Optional, List
from pydantic import BaseSettings, Field, validator
from functools import lru_cache


class Settings(BaseSettings):
    """Production settings with environment variable support"""
    
    # ============================================
    # Application Settings
    # ============================================
    app_name: str = Field("Güvenilir Analiz", env="APP_NAME")
    app_version: str = Field("10.0.0", env="APP_VERSION")
    environment: str = Field("production", env="ENVIRONMENT")
    debug: bool = Field(False, env="DEBUG")
    log_level: str = Field("INFO", env="LOG_LEVEL")
    
    # ============================================
    # Server Settings
    # ============================================
    host: str = Field("0.0.0.0", env="HOST")
    port: int = Field(8000, env="PORT")
    workers: int = Field(4, env="WORKERS")
    worker_timeout: int = Field(120, env="WORKER_TIMEOUT")
    max_requests: int = Field(1000, env="MAX_REQUESTS")
    max_requests_jitter: int = Field(50, env="MAX_REQUESTS_JITTER")
    
    # ============================================
    # Security
    # ============================================
    secret_key: str = Field(..., env="SECRET_KEY")
    api_key: str = Field(..., env="API_KEY")
    allowed_hosts: List[str] = Field(["localhost"], env="ALLOWED_HOSTS")
    cors_origins: List[str] = Field(["http://localhost:3000"], env="CORS_ORIGINS")
    
    # ============================================
    # Database
    # ============================================
    database_url: str = Field(..., env="DATABASE_URL")
    db_pool_size: int = Field(10, env="DB_POOL_SIZE")
    db_max_overflow: int = Field(20, env="DB_MAX_OVERFLOW")
    db_echo: bool = Field(False, env="DB_ECHO")
    
    # ============================================
    # Redis Cache
    # ============================================
    redis_url: str = Field("redis://localhost:6379/0", env="REDIS_URL")
    redis_max_connections: int = Field(50, env="REDIS_MAX_CONNECTIONS")
    cache_ttl: int = Field(3600, env="CACHE_TTL")  # 1 hour
    
    # ============================================
    # API Configuration
    # ============================================
    api_base_url: str = Field("https://v3.football.api-sports.io", env="API_BASE_URL")
    api_rate_limit: int = Field(30, env="API_RATE_LIMIT")
    api_timeout: int = Field(10, env="API_TIMEOUT")
    
    # ============================================
    # ML Model Settings
    # ============================================
    ml_model_cache: str = Field("/app/models", env="ML_MODEL_CACHE")
    ml_performance_log: str = Field("/app/logs/ml_performance.json", env="ML_PERFORMANCE_LOG")
    enable_auto_retraining: bool = Field(False, env="ENABLE_AUTO_RETRAINING")
    
    # ============================================
    # Monitoring & Logging
    # ============================================
    sentry_dsn: Optional[str] = Field(None, env="SENTRY_DSN")
    sentry_environment: str = Field("production", env="SENTRY_ENVIRONMENT")
    enable_monitoring: bool = Field(True, env="ENABLE_MONITORING")
    
    # ============================================
    # Feature Flags
    # ============================================
    enable_automl: bool = Field(True, env="ENABLE_AUTOML")
    enable_drift_detection: bool = Field(True, env="ENABLE_DRIFT_DETECTION")
    enable_explainability: bool = Field(True, env="ENABLE_EXPLAINABILITY")
    enable_real_time_predictions: bool = Field(True, env="ENABLE_REAL_TIME_PREDICTIONS")
    
    # ============================================
    # Backup & Maintenance
    # ============================================
    backup_enabled: bool = Field(True, env="BACKUP_ENABLED")
    backup_interval: str = Field("24h", env="BACKUP_INTERVAL")
    backup_retention: str = Field("7d", env="BACKUP_RETENTION")
    
    @validator("cors_origins", pre=True)
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    @validator("allowed_hosts", pre=True)
    def parse_allowed_hosts(cls, v):
        if isinstance(v, str):
            return [host.strip() for host in v.split(",")]
        return v
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Database connection
def get_database_url(settings: Settings = None) -> str:
    """Get formatted database URL"""
    if settings is None:
        settings = get_settings()
    return settings.database_url


# Redis connection
def get_redis_url(settings: Settings = None) -> str:
    """Get formatted Redis URL"""
    if settings is None:
        settings = get_settings()
    return settings.redis_url


# Check if production
def is_production() -> bool:
    """Check if running in production environment"""
    settings = get_settings()
    return settings.environment.lower() == "production"


# Check if debug mode
def is_debug() -> bool:
    """Check if debug mode is enabled"""
    settings = get_settings()
    return settings.debug


# Export settings instance
settings = get_settings()


if __name__ == "__main__":
    # Test configuration
    print("=" * 70)
    print("Production Configuration")
    print("=" * 70)
    
    config = get_settings()
    
    print(f"\nApplication:")
    print(f"  Name: {config.app_name}")
    print(f"  Version: {config.app_version}")
    print(f"  Environment: {config.environment}")
    print(f"  Debug: {config.debug}")
    
    print(f"\nServer:")
    print(f"  Host: {config.host}:{config.port}")
    print(f"  Workers: {config.workers}")
    
    print(f"\nDatabase:")
    print(f"  URL: {config.database_url[:50]}...")
    
    print(f"\nRedis:")
    print(f"  URL: {config.redis_url}")
    
    print(f"\nFeature Flags:")
    print(f"  AutoML: {config.enable_automl}")
    print(f"  Drift Detection: {config.enable_drift_detection}")
    print(f"  Explainability: {config.enable_explainability}")
    
    print(f"\nMonitoring:")
    print(f"  Enabled: {config.enable_monitoring}")
    print(f"  Sentry: {'Configured' if config.sentry_dsn else 'Not configured'}")
    
    print("\n" + "=" * 70)
