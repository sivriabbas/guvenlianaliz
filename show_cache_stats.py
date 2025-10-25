"""
CACHE İSTATİSTİKLERİNİ GÖSTER
"""
from cache_manager import get_cache

cache = get_cache()

print("="*70)
print("📊 CACHE İSTATİSTİKLERİ")
print("="*70)

cache.print_stats()

print("="*70)
