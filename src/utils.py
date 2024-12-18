import asyncio
import os

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
