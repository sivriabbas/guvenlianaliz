# -*- coding: utf-8 -*-
"""
password_manager.py

Küçük bir CLI ve Streamlit arayüzü ile `config.yaml` içindeki kullanıcıları yönetmenizi sağlar.
Desteklenen işlemler: add (ekle), passwd (parola değiştir), remove (sil), list (listele).

Kullanım örnekleri (cmd.exe):
    python password_manager.py add --username ali --email ali@mail.com --name Ali --password S3cure! --tier ücretsiz
    python password_manager.py passwd --username ali --password YeniParola123!
    python password_manager.py remove --username ali
    python password_manager.py list

Bu script parolaları `streamlit_authenticator.Hasher` ile hash'ler ve `config.yaml` dosyasına yazar.
"""

import argparse
import getpass
import sys
from yaml.loader import SafeLoader
import yaml
import os
import streamlit_authenticator as stauth

CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'config.yaml')


def load_config(path=CONFIG_PATH):
    if not os.path.exists(path):
        return {'credentials': {'usernames': {}}, 'cookie': {'expiry_days': 30, 'key': '', 'name': ''}}
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.load(f, Loader=SafeLoader) or {}


def save_config(cfg, path=CONFIG_PATH):
    with open(path, 'w', encoding='utf-8') as f:
        yaml.dump(cfg, f, default_flow_style=False, allow_unicode=True)


def gen_hash(password: str) -> str:
    hasher = stauth.Hasher()
    return hasher.hash(password)


def add_user(username: str, email: str, name: str, password: str, tier: str):
    cfg = load_config()
    users = cfg.setdefault('credentials', {}).setdefault('usernames', {})
    if username in users:
        print(f"Kullanıcı '{username}' zaten mevcut.")
        return 1
    hashed = gen_hash(password)
    users[username] = {'email': email, 'name': name, 'password': hashed, 'tier': tier}
    save_config(cfg)
    # Yeni kullanıcı eklendikten sonra default limitleri atamaya çalış
    try:
        import api_utils
        api_utils.ensure_user_limits(username, tier)
    except Exception:
        # Hata olsa da kullanıcı ekleme başarılı sayılır
        pass
    print(f"Kullanıcı '{username}' eklendi.")
    return 0


def change_password(username: str, password: str):
    cfg = load_config()
    users = cfg.get('credentials', {}).get('usernames', {})
    if username not in users:
        print(f"Kullanıcı '{username}' bulunamadı.")
        return 1
    users[username]['password'] = gen_hash(password)
    save_config(cfg)
    print(f"{username} kullanıcısının parolası güncellendi.")
    return 0


def change_email(username: str, new_email: str):
    """Bir kullanıcının e-posta adresini config.yaml dosyasında günceller."""
    cfg = load_config()
    users = cfg.get('credentials', {}).get('usernames', {})
    if username not in users:
        return 1  # Kullanıcı bulunamadı
    users[username]['email'] = new_email
    save_config(cfg)
    return 0  # Başarılı


def remove_user(username: str):
    cfg = load_config()
    users = cfg.get('credentials', {}).get('usernames', {})
    if username not in users:
        print(f"Kullanıcı '{username}' bulunamadı.")
        return 1
    del users[username]
    save_config(cfg)
    print(f"Kullanıcı '{username}' silindi.")
    return 0


def list_users():
    cfg = load_config()
    users = cfg.get('credentials', {}).get('usernames', {})
    if not users:
        print('Kayıtlı kullanıcı bulunamadı.')
        return 0
    for u, info in users.items():
        print(f"- {u}: {info.get('name','')}<{info.get('email','')}> (seviye: {info.get('tier','')})")
    return 0


def parse_args():
    p = argparse.ArgumentParser(description='config.yaml içindeki kullanıcıları yönet')
    sp = p.add_subparsers(dest='cmd')

    p_add = sp.add_parser('add', help='Yeni kullanıcı ekle')
    p_add.add_argument('--username', required=True)
    p_add.add_argument('--email', required=True)
    p_add.add_argument('--name', required=True)
    p_add.add_argument('--password', required=False)
    p_add.add_argument('--tier', default='ücretsiz')

    p_pass = sp.add_parser('passwd', help='Var olan kullanıcının parolasını değiştir')
    p_pass.add_argument('--username', required=True)
    p_pass.add_argument('--password', required=False)

    p_rem = sp.add_parser('remove', help='Kullanıcıyı sil')
    p_rem.add_argument('--username', required=True)

    sp.add_parser('list')
    sp.add_parser('admins', help='Yönetici listesini göster')
    p_prom = sp.add_parser('promote', help='Bir kullanıcıyı admin yap')
    p_prom.add_argument('--username', required=True)
    p_dem = sp.add_parser('demote', help='Bir admini geri al (adminlik kaldır)')
    p_dem.add_argument('--username', required=True)

    return p.parse_args()


def main():
    args = parse_args()
    if args.cmd == 'add':
        pwd = args.password or getpass.getpass(prompt='Parola: ')
        return add_user(args.username, args.email, args.name, pwd, args.tier)
    if args.cmd == 'passwd':
        pwd = args.password or getpass.getpass(prompt='Yeni parola: ')
        return change_password(args.username, pwd)
    if args.cmd == 'remove':
        return remove_user(args.username)
    if args.cmd == 'list':
        return list_users()
    if args.cmd == 'admins':
        cfg = load_config()
        admins = cfg.get('admin_users', [])
        if not admins:
            print('Admin kullanıcı bulunmuyor.')
        else:
            print('Admin kullanıcılar:')
            for a in admins:
                print('-', a)
        return 0
    if args.cmd == 'promote':
        cfg = load_config()
        admins = cfg.setdefault('admin_users', [])
        if args.username in admins:
            print(f"{args.username} zaten admin.")
            return 0
        admins.append(args.username)
        save_config(cfg)
        print(f"{args.username} artık admin.")
        return 0
    if args.cmd == 'demote':
        cfg = load_config()
        admins = cfg.get('admin_users', [])
        if args.username not in admins:
            print(f"{args.username} admin değil.")
            return 0
        admins.remove(args.username)
        cfg['admin_users'] = admins
        save_config(cfg)
        print(f"{args.username} adminlikten alındı.")
        return 0
    print('Komut belirtilmedi. Yardım için --help kullanın.')
    return 2


if __name__ == '__main__':
    # If invoked as a module, allow choosing CLI or Streamlit UI
    if len(sys.argv) > 1:
        sys.exit(main())
    else:
        # Launch Streamlit UI
        import streamlit as st

        def run_streamlit_ui():
            st.set_page_config(page_title='Parola Yöneticisi', layout='centered')
            st.title('🔑 Parola Yöneticisi')

            # --- Basit UI auth: hangi kullanıcı aracı kullanıyor belirle ---
            cfg = load_config()
            any_hashed = False
            try:
                creds = cfg.get('credentials', {}).get('usernames', {})
                for u, info in creds.items():
                    pw = info.get('password', '')
                    if isinstance(pw, str) and pw.startswith('$2'):
                        any_hashed = True
                        break
            except Exception:
                any_hashed = False

            authenticator = stauth.Authenticate(
                cfg.get('credentials', {}),
                cfg.get('cookie', {}).get('name', ''),
                cfg.get('cookie', {}).get('key', ''),
                cfg.get('cookie', {}).get('expiry_days', 30),
                auto_hash=(not any_hashed)
            )

            authenticator.login('Giriş Yap')
            is_admin = False
            if st.session_state.get('authentication_status'):
                cur_user = st.session_state.get('username')
                admin_users = cfg.get('admin_users', [])
                cur_tier = cfg.get('credentials', {}).get('usernames', {}).get(cur_user, {}).get('tier')
                if cur_user in admin_users or cur_tier == 'admin':
                    is_admin = True

            # Eğer kullanıcı admin değilse Admin Yönetimi seçeneğini gösterme
            options = ['Listele', 'Ekle', 'Parola değiştir', 'Sil', 'Limit Yönetimi']
            if is_admin:
                options = options + ['Admin Yönetimi']
            action = st.sidebar.selectbox('İşlem', options)

            # Add Admin Yönetimi option
            if 'Admin Yönetimi' not in ['Listele', 'Ekle', 'Parola değiştir', 'Sil', 'Limit Yönetimi']:
                pass

            cfg = load_config()
            users = cfg.get('credentials', {}).get('usernames', {})

            if action == 'Listele':
                st.subheader('Kayıtlı kullanıcılar')
                if not users:
                    st.info('Kayıtlı kullanıcı bulunamadı')
                else:
                    for u, info in users.items():
                        st.write(f"- **{u}**: {info.get('name','')}<{info.get('email','')}> (seviye: {info.get('tier','')})")

            elif action == 'Admin Yönetimi':
                st.subheader('Admin Yönetimi')
                admins = cfg.get('admin_users', [])
                st.markdown('**Mevcut Adminler**')
                if not admins:
                    st.info('Admin kullanıcı bulunmuyor')
                else:
                    for a in admins:
                        st.write(f'- {a}')

                st.markdown('---')
                st.markdown('**Kullanıcıyı Admin Yap / Geri Al**')
                sel = st.selectbox('Kullanıcı seç', list(users.keys()) if users else [])
                col1, col2 = st.columns(2)
                with col1:
                    if st.button('Admin Yap'):
                        if not sel:
                            st.error('Lütfen bir kullanıcı seçin')
                        else:
                            admins = cfg.setdefault('admin_users', [])
                            if sel in admins:
                                st.info('Kullanıcı zaten admin')
                            else:
                                admins.append(sel)
                                save_config(cfg)
                                st.success(f'{sel} admin yapıldı')
                with col2:
                    if st.button('Adminlik Kaldır'):
                        if not sel:
                            st.error('Lütfen bir kullanıcı seçin')
                        else:
                            admins = cfg.get('admin_users', [])
                            if sel not in admins:
                                st.info('Kullanıcı admin değil')
                            else:
                                admins.remove(sel)
                                cfg['admin_users'] = admins
                                save_config(cfg)
                                st.success(f'{sel} adminlikten alındı')

            elif action == 'Ekle':
                st.subheader('Yeni kullanıcı ekle')
                username = st.text_input('Kullanıcı adı')
                email = st.text_input('E-posta')
                name = st.text_input('Ad Soyad')
                tier = st.selectbox('Seviye', ['ücretsiz', 'ücretli'])
                pw = st.text_input('Parola', type='password')
                if st.button('Ekle'):
                    if not username or not email or not name or not pw:
                        st.error('Lütfen tüm alanları doldurun')
                    else:
                        res = add_user(username.strip(), email.strip(), name.strip(), pw, tier)
                        if res == 0:
                            # Try to ensure user limits (best-effort)
                            try:
                                import api_utils
                                api_utils.ensure_user_limits(username.strip(), tier)
                            except Exception:
                                pass
                            st.success(f"Kullanıcı {username} eklendi")
                        else:
                            st.error('Kullanıcı eklenemedi')

            elif action == 'Parola değiştir':
                st.subheader('Kullanıcı parolasını değiştir')
                sel = st.selectbox('Kullanıcı seçin', list(users.keys()) if users else [])
                newpw = st.text_input('Yeni parola', type='password')
                if st.button('Değiştir'):
                    if not sel or not newpw:
                        st.error('Lütfen bir kullanıcı seçin ve yeni parolayı girin')
                    else:
                        res = change_password(sel, newpw)
                        if res == 0:
                            st.success('Parola güncellendi')
                        else:
                            st.error('Parola güncellenemedi')

            elif action == 'Sil':
                st.subheader('Kullanıcıyı sil')
                sel = st.selectbox('Silinecek kullanıcıyı seçin', list(users.keys()) if users else [])
                if st.button('Sil'):
                    if not sel:
                        st.error('Lütfen bir kullanıcı seçin')
                    else:
                        res = remove_user(sel)
                        if res == 0:
                            st.success('Kullanıcı silindi')
                        else:
                            st.error('Kullanıcı silinemedi')

            elif action == 'Limit Yönetimi':
                st.subheader('Limit Yönetimi (admin)')
                # import api helpers lazily
                from api_utils import set_user_daily_limit, set_user_monthly_limit, reset_daily_usage, get_usage_summary

                summary = get_usage_summary()
                st.markdown('### Kullanım Özeti')
                if not summary:
                    st.info('Kullanıcı kullanım verisi bulunmuyor.')
                else:
                    for u, info in summary.items():
                        st.write(f"**{u}** — Günlük: {info['count']} / {info['daily_limit'] or 'varsayılan'}, Aylık: {info['monthly_count']} / {info['monthly_limit'] or 'varsayılan'}")

                st.markdown('---')
                st.markdown('### Limitsiz/Sınırlı Kullanıcı Ayarları')
                users_list = list(load_config().get('credentials', {}).get('usernames', {}).keys())
                sel_user = st.selectbox('Kullanıcı seç', [''] + users_list)
                daily_lim = st.number_input('Günlük limit (boş bırak = varsayılan)', min_value=0, value=0, step=1)
                monthly_lim = st.number_input('Aylık limit (boş bırak = yok)', min_value=0, value=0, step=1)
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button('Günlük limiti uygula'):
                        if not sel_user:
                            st.error('Lütfen bir kullanıcı seçin')
                        else:
                            try:
                                usage_before = __import__('api_utils')._read_usage_file()
                                before_count = usage_before.get(sel_user, {}).get('count', 0)
                            except Exception:
                                before_count = None

                            set_user_daily_limit(sel_user, int(daily_lim))

                            try:
                                usage_after = __import__('api_utils')._read_usage_file()
                                after_count = usage_after.get(sel_user, {}).get('count', 0)
                            except Exception:
                                after_count = None

                            if before_count is not None and after_count is not None and after_count != before_count:
                                st.success(f"{sel_user}: günlük sayaç {before_count} → {after_count} olarak güncellendi (limit {int(daily_lim)})")
                            else:
                                st.success('Günlük limit kaydedildi')
                with col2:
                    if st.button('Aylık limiti uygula'):
                        if not sel_user:
                            st.error('Lütfen bir kullanıcı seçin')
                        else:
                            try:
                                usage_before = __import__('api_utils')._read_usage_file()
                                before_monthly = usage_before.get(sel_user, {}).get('monthly_count', 0)
                            except Exception:
                                before_monthly = None

                            set_user_monthly_limit(sel_user, int(monthly_lim))

                            try:
                                usage_after = __import__('api_utils')._read_usage_file()
                                after_monthly = usage_after.get(sel_user, {}).get('monthly_count', 0)
                            except Exception:
                                after_monthly = None

                            if before_monthly is not None and after_monthly is not None and after_monthly != before_monthly:
                                st.success(f"{sel_user}: aylık sayaç {before_monthly} → {after_monthly} olarak güncellendi (limit {int(monthly_lim)})")
                            else:
                                st.success('Aylık limit kaydedildi')
                with col3:
                    if st.button('Günlük sayaç sıfırla (tüm kullanıcılar)'):
                        reset_daily_usage()
                        st.success('Günlük sayaçlar sıfırlandı')

        run_streamlit_ui()