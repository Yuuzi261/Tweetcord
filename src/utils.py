import asyncio
import os
import re

from datetime import datetime, timezone


class LockManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.lock = asyncio.Lock()
        return cls._instance


def get_lock():
    return LockManager().lock


def bool_to_str(boo: bool):
    return '1' if boo else '0'


def str_to_bool(string: str):
    return False if string == '0' else True


def get_accounts():
    accounts_str = os.getenv('TWITTER_TOKEN').strip(",")
    accounts = {account.split(':')[0]: account.split(':')[1] for account in accounts_str.split(',')}  # accounts_str = 'username:token,username:token'
    return accounts


def get_utcnow():
    return datetime.now(timezone.utc).isoformat(timespec='seconds').replace('T', ' ')


# Checking only the format may still allow passage through languages ​​that do not exist
def validate_and_normalize_language(lang_code: str) -> str | None:
    if not lang_code or not isinstance(lang_code, str):
        return None

    normalized = lang_code.strip().lower().replace('_', '-')

    normalization_map = {
        'zh': 'zh-cn',
        'cn': 'zh-cn',
        'tw': 'zh-tw',
        'jp': 'ja',
        'kr': 'ko',
        'ua': 'uk'
    }
    normalized = normalization_map.get(normalized, normalized)

    pattern = r"^[a-z]{2,3}(-[a-z0-9]{2,4})?$"
    
    if re.match(pattern, normalized):
        return normalized

    return None
