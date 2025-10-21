# -*- coding: utf-8 -*-
from __future__ import annotations
import argparse
from api_utils import reset_daily_usage

def run_daily_reset(user: str = None):
    """Günlük API sayaçlarını sıfırlayan ana fonksiyon."""
    if user:
        reset_daily_usage(user)
        print(f"Günlük sayaçlar {user} için sıfırlandı.")
    else:
        reset_daily_usage()
        print("Tüm kullanıcıların günlük sayaçları sıfırlandı.")

def main():
    parser = argparse.ArgumentParser(description='Günlük API sayaçlarını sıfırlama scripti')
    parser.add_argument('--user', '-u', help='Sadece bu kullanıcı için sıfırla (opsiyonel)', default=None)
    args = parser.parse_args()
    run_daily_reset(args.user)

if __name__ == '__main__':
    main()