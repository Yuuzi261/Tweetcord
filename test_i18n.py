"""Quick verification script for the i18n implementation."""
import sys
sys.path.insert(0, '.')

import yaml

from src.i18n import init_i18n, t


def _collect_keys(data: dict, prefix: str = '') -> set:
    keys = set()
    for k, v in data.items():
        full_key = f'{prefix}.{k}' if prefix else k
        if isinstance(v, dict):
            keys |= _collect_keys(v, full_key)
        else:
            keys.add(full_key)
    return keys


def check_locale_parity():
    with open('locales/en.yml', 'r', encoding='utf-8') as f:
        en = yaml.safe_load(f) or {}
    with open('locales/zh-TW.yml', 'r', encoding='utf-8') as f:
        zh = yaml.safe_load(f) or {}

    en_keys = _collect_keys(en)
    zh_keys = _collect_keys(zh)

    missing_in_zh = en_keys - zh_keys
    missing_in_en = zh_keys - en_keys

    if missing_in_zh:
        print(f'[FAIL] Keys in en.yml but missing in zh-TW.yml:')
        for k in sorted(missing_in_zh):
            print(f'  - {k}')
    if missing_in_en:
        print(f'[FAIL] Keys in zh-TW.yml but missing in en.yml:')
        for k in sorted(missing_in_en):
            print(f'  - {k}')
    if not missing_in_zh and not missing_in_en:
        print('[OK] en.yml and zh-TW.yml have identical keys')

def section(title):
    print(f'\n=== {title} ===')

# --- Locale parity ---
section('Locale key parity check')
check_locale_parity()

# --- English ---
section('English (en)')
init_i18n('en')
print(t('sync.background'))
print(t('notification.add.user_not_found', username='testuser'))
print(t('notification.add.client_conflict', username='testuser', account_used='client1'))
print(t('notification.add.failed'))
print(t('notification.add.success_new', username='testuser', account_used='client1'))
print(t('notification.add.success_update', username='testuser', client_used='client1'))
print(t('notification.remove.success', username='testuser'))
print(t('notification.remove.not_found', username='testuser', channel_id='123'))
print(t('notification.remove.channel_not_found', channel_id='123', guild_name='My Server'))
print(t('notification.remove.failed'))
print(t('notification.customize.message.channel_not_found', channel_id='123'))
print(t('notification.customize.message.notifier_not_found', username='testuser', channel_mention='#general'))
print(t('notification.customize.message.success_default'))
print(t('notification.customize.translation.not_enabled'))
print(t('notification.customize.translation.invalid_lang'))
print(t('notification.customize.translation.success_default', username='testuser', default_lang='en'))
print(t('notification.customize.translation.success_set', username='testuser', lang_code='ja'))
print(t('notification.customize.translation.user_not_found', username='testuser'))
print(t('list.title', guild_name='My Server', page_counter=''))
print(t('list.title', guild_name='My Server', page_counter=t('list.title_page_counter', page=1, total=3)))
print(t('list.no_users'))
print(t('list.footer', page=1, total=3))
print(t('modal.customize_message.title'))
print(t('modal.customize_message.label_full', username='testuser', channel_name='general'))
print(t('modal.customize_message.label_short', username='testuser'))
print(t('modal.customize_message.label_fallback'))
print(t('modal.customize_message.placeholder'))
print(t('modal.customize_message.success'))
print(t('display.action.tweeted'))
print(t('display.action.retweeted'))
print(t('display.action.quoted'))
print(t('display.tweet_type.photos', count=3))
print(t('display.tweet_type.media', media_type='photo'))
print(t('display.tweet_type.status'))
print(t('display.media_type_map.photo'))
print(t('display.media_type_map.video'))
print(t('display.media_type_map.gif'))

# --- zh-TW ---
section('繁體中文 (zh-TW)')
init_i18n('zh-TW')
print(t('sync.background'))
print(t('notification.add.user_not_found', username='testuser'))
print(t('notification.add.success_new', username='testuser', account_used='client1'))
print(t('list.title', guild_name='我的伺服器', page_counter=t('list.title_page_counter', page=2, total=5)))
print(t('list.no_users'))
print(t('list.footer', page=2, total=5))
print(t('modal.customize_message.title'))
print(t('display.action.tweeted'))
print(t('display.tweet_type.photos', count=4))
print(t('display.media_type_map.photo'))
print(t('display.media_type_map.video'))
print(t('display.media_type_map.gif'))

# --- Fallback ---
section('Nonexistent locale → fallback to en')
init_i18n('nonexistent')
print(t('sync.background'))
print(t('notification.add.user_not_found', username='testuser'))

# --- Missing key ---
section('Missing key → returns key name + warning')
init_i18n('en')
print(t('this.key.does.not.exist'))
