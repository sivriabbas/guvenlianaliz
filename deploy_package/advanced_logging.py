"""
Advanced Logging System - Phase 8.C
Gelişmiş structured logging, log rotation ve analiz sistemi

Özellikler:
- Structured logging (JSON format)
- Log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Automatic log rotation
- Error tracking ve alerting
- Performance logging
- Request/Response logging
"""

import logging
import logging.handlers
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import traceback
from functools import wraps


class StructuredFormatter(logging.Formatter):
    """JSON formatında structured log oluştur"""
    
    def format(self, record: logging.LogRecord) -> str:
        """Log record'u JSON'a çevir"""
        
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Extra alanları ekle
        if hasattr(record, 'extra_data'):
            log_data.update(record.extra_data)
        
        # Exception bilgisi varsa ekle
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": traceback.format_exception(*record.exc_info)
            }
        
        return json.dumps(log_data, ensure_ascii=False)


class ColoredFormatter(logging.Formatter):
    """Renkli console output için formatter"""
    
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'        # Reset
    }
    
    def format(self, record: logging.LogRecord) -> str:
        """Renkli log formatla"""
        
        color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        reset = self.COLORS['RESET']
        
        # Emoji ekle
        emoji_map = {
            'DEBUG': '🔍',
            'INFO': '✅',
            'WARNING': '⚠️',
            'ERROR': '❌',
            'CRITICAL': '🔥'
        }
        emoji = emoji_map.get(record.levelname, '📝')
        
        formatted = f"{color}{emoji} [{record.levelname}]{reset} {record.getMessage()}"
        
        if record.exc_info:
            formatted += f"\n{self.formatException(record.exc_info)}"
        
        return formatted


class LoggerSetup:
    """Logger yapılandırma ve yönetimi"""
    
    def __init__(self, name: str = "api", log_dir: str = "logs"):
        self.name = name
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        # Mevcut handler'ları temizle
        self.logger.handlers.clear()
        
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Log handler'larını yapılandır"""
        
        # 1. Console Handler (Renkli)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(ColoredFormatter())
        self.logger.addHandler(console_handler)
        
        # 2. File Handler - Genel loglar (JSON)
        general_file = self.log_dir / f"{self.name}.log"
        file_handler = logging.handlers.RotatingFileHandler(
            general_file,
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(StructuredFormatter())
        self.logger.addHandler(file_handler)
        
        # 3. Error Handler - Sadece hatalar
        error_file = self.log_dir / f"{self.name}_errors.log"
        error_handler = logging.handlers.RotatingFileHandler(
            error_file,
            maxBytes=5 * 1024 * 1024,  # 5 MB
            backupCount=5,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(StructuredFormatter())
        self.logger.addHandler(error_handler)
        
        # 4. Time-based Rotating Handler - Günlük loglar
        daily_file = self.log_dir / f"{self.name}_daily.log"
        daily_handler = logging.handlers.TimedRotatingFileHandler(
            daily_file,
            when='midnight',
            interval=1,
            backupCount=30,  # 30 gün
            encoding='utf-8'
        )
        daily_handler.setLevel(logging.INFO)
        daily_handler.setFormatter(StructuredFormatter())
        self.logger.addHandler(daily_handler)
    
    def get_logger(self) -> logging.Logger:
        """Logger instance'ı döndür"""
        return self.logger


# Global logger instance
api_logger_setup = LoggerSetup(name="api", log_dir="logs")
api_logger = api_logger_setup.get_logger()


def log_execution(func):
    """Fonksiyon çalışmasını logla (decorator)"""
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        func_name = func.__name__
        
        # Başlangıç logu
        api_logger.debug(f"🚀 {func_name} başladı", extra={
            'extra_data': {
                'function': func_name,
                'args_count': len(args),
                'kwargs_count': len(kwargs)
            }
        })
        
        start_time = datetime.now()
        
        try:
            result = func(*args, **kwargs)
            
            # Başarılı tamamlanma
            duration = (datetime.now() - start_time).total_seconds()
            api_logger.debug(f"✅ {func_name} tamamlandı ({duration:.3f}s)", extra={
                'extra_data': {
                    'function': func_name,
                    'duration_seconds': duration,
                    'status': 'success'
                }
            })
            
            return result
            
        except Exception as e:
            # Hata durumu
            duration = (datetime.now() - start_time).total_seconds()
            api_logger.error(f"❌ {func_name} hata verdi: {str(e)}", extra={
                'extra_data': {
                    'function': func_name,
                    'duration_seconds': duration,
                    'status': 'error',
                    'error_type': type(e).__name__
                }
            }, exc_info=True)
            
            raise
    
    return wrapper


def log_api_request(endpoint: str, method: str, status_code: int, 
                    response_time: float, ip_address: str = None,
                    user_agent: str = None, error: str = None):
    """API isteğini logla"""
    
    log_data = {
        'event_type': 'api_request',
        'endpoint': endpoint,
        'method': method,
        'status_code': status_code,
        'response_time': response_time,
        'ip_address': ip_address,
        'user_agent': user_agent
    }
    
    if error:
        log_data['error'] = error
    
    level = logging.INFO if status_code < 400 else logging.ERROR
    
    api_logger.log(level, f"API Request: {method} {endpoint} -> {status_code}", extra={
        'extra_data': log_data
    })


def log_ml_prediction(model_type: str, prediction_result: Any, 
                      processing_time: float, confidence: float = None):
    """ML tahmin işlemini logla"""
    
    log_data = {
        'event_type': 'ml_prediction',
        'model_type': model_type,
        'processing_time': processing_time,
        'confidence': confidence
    }
    
    api_logger.info(f"ML Prediction: {model_type} ({processing_time:.3f}s)", extra={
        'extra_data': log_data
    })


def log_cache_operation(operation: str, key: str, hit: bool = None, 
                       value_size: int = None):
    """Cache işlemini logla"""
    
    log_data = {
        'event_type': 'cache_operation',
        'operation': operation,
        'key': key,
        'hit': hit,
        'value_size': value_size
    }
    
    api_logger.debug(f"Cache {operation}: {key}", extra={
        'extra_data': log_data
    })


def log_database_operation(operation: str, table: str, 
                          affected_rows: int = None, 
                          execution_time: float = None):
    """Veritabanı işlemini logla"""
    
    log_data = {
        'event_type': 'database_operation',
        'operation': operation,
        'table': table,
        'affected_rows': affected_rows,
        'execution_time': execution_time
    }
    
    api_logger.debug(f"Database {operation}: {table}", extra={
        'extra_data': log_data
    })


def log_performance_warning(component: str, metric: str, 
                           value: float, threshold: float):
    """Performans uyarısı logla"""
    
    log_data = {
        'event_type': 'performance_warning',
        'component': component,
        'metric': metric,
        'value': value,
        'threshold': threshold
    }
    
    api_logger.warning(
        f"⚠️ Performance Warning: {component} - {metric} = {value} (threshold: {threshold})", 
        extra={'extra_data': log_data}
    )


def log_security_event(event_type: str, severity: str, 
                       ip_address: str = None, details: Dict = None):
    """Güvenlik olayını logla"""
    
    log_data = {
        'event_type': 'security_event',
        'security_event_type': event_type,
        'severity': severity,
        'ip_address': ip_address
    }
    
    if details:
        log_data.update(details)
    
    level_map = {
        'low': logging.INFO,
        'medium': logging.WARNING,
        'high': logging.ERROR,
        'critical': logging.CRITICAL
    }
    
    level = level_map.get(severity.lower(), logging.WARNING)
    
    api_logger.log(level, f"🔒 Security Event: {event_type}", extra={
        'extra_data': log_data
    })


class LogAnalyzer:
    """Log dosyalarını analiz eden sınıf"""
    
    def __init__(self, log_file: str):
        self.log_file = Path(log_file)
    
    def get_error_summary(self, last_n_lines: int = 1000) -> Dict[str, Any]:
        """Son N satırda hata özeti"""
        
        if not self.log_file.exists():
            return {"error": "Log dosyası bulunamadı"}
        
        errors = []
        
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                # Son N satırı oku
                lines = f.readlines()[-last_n_lines:]
                
                for line in lines:
                    try:
                        log_entry = json.loads(line.strip())
                        if log_entry.get('level') in ['ERROR', 'CRITICAL']:
                            errors.append(log_entry)
                    except json.JSONDecodeError:
                        continue
            
            # Hata tiplerini say
            error_types = {}
            for error in errors:
                error_type = error.get('exception', {}).get('type', 'Unknown')
                error_types[error_type] = error_types.get(error_type, 0) + 1
            
            return {
                "total_errors": len(errors),
                "error_types": error_types,
                "recent_errors": errors[-10:] if errors else []
            }
            
        except Exception as e:
            return {"error": f"Analiz hatası: {str(e)}"}
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Performans metriklerini çıkar"""
        
        if not self.log_file.exists():
            return {"error": "Log dosyası bulunamadı"}
        
        response_times = []
        slow_requests = []
        
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        log_entry = json.loads(line.strip())
                        extra = log_entry.get('extra_data', {})
                        
                        if extra.get('event_type') == 'api_request':
                            rt = extra.get('response_time', 0)
                            response_times.append(rt)
                            
                            if rt > 1.0:  # 1 saniyeden yavaş
                                slow_requests.append({
                                    'endpoint': extra.get('endpoint'),
                                    'response_time': rt,
                                    'timestamp': log_entry.get('timestamp')
                                })
                    except json.JSONDecodeError:
                        continue
            
            if response_times:
                return {
                    "avg_response_time": sum(response_times) / len(response_times),
                    "min_response_time": min(response_times),
                    "max_response_time": max(response_times),
                    "slow_requests_count": len(slow_requests),
                    "slow_requests": slow_requests[-10:]
                }
            else:
                return {"message": "Performans verisi bulunamadı"}
                
        except Exception as e:
            return {"error": f"Analiz hatası: {str(e)}"}


# Test fonksiyonu
if __name__ == "__main__":
    print("🔧 Advanced Logging System Test\n")
    
    # Test logları
    api_logger.debug("Debug mesajı - sistem detayları")
    api_logger.info("Info mesajı - normal işlem")
    api_logger.warning("Warning mesajı - dikkat edilmesi gereken durum")
    api_logger.error("Error mesajı - hata oluştu")
    
    print("\n📊 Structured Logging Test:")
    
    # API request log
    log_api_request(
        endpoint="/api/predict",
        method="POST",
        status_code=200,
        response_time=0.523,
        ip_address="192.168.1.100",
        user_agent="TestClient/1.0"
    )
    
    # ML prediction log
    log_ml_prediction(
        model_type="XGBoost",
        prediction_result="1",
        processing_time=0.156,
        confidence=0.89
    )
    
    # Cache operation log
    log_cache_operation(
        operation="GET",
        key="predict_12345",
        hit=True,
        value_size=256
    )
    
    # Performance warning
    log_performance_warning(
        component="API",
        metric="response_time",
        value=2.5,
        threshold=1.0
    )
    
    # Security event
    log_security_event(
        event_type="rate_limit_exceeded",
        severity="medium",
        ip_address="192.168.1.200",
        details={"attempts": 150, "limit": 100}
    )
    
    print("\n🔍 Decorator Test:")
    
    @log_execution
    def test_function(x, y):
        """Test fonksiyonu"""
        import time
        time.sleep(0.1)
        return x + y
    
    result = test_function(5, 10)
    print(f"Sonuç: {result}")
    
    print("\n📈 Log Analysis Test:")
    
    analyzer = LogAnalyzer("logs/api.log")
    error_summary = analyzer.get_error_summary()
    print(f"Hata sayısı: {error_summary.get('total_errors', 0)}")
    
    print("\n✅ Advanced Logging System - Ready!")
    print("   - Structured logging (JSON): ✅")
    print("   - Log rotation: ✅")
    print("   - Colored console: ✅")
    print("   - Error tracking: ✅")
    print("   - Performance logging: ✅")
    print("   - Log analysis: ✅")
    print(f"\n📁 Log dosyaları: logs/ dizininde")
