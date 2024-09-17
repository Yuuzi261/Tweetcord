import os

def bool_to_str(boo: bool):
    return '1' if boo else '0'


def str_to_bool(string: str):
    return False if string == '0' else True


def get_accounts():
    accounts_str = os.getenv('TWITTER_TOKEN').strip(",")
    accounts = {account.split(':')[0]: account.split(':')[1] for account in accounts_str.split(',')}  # accounts_str = 'username:token,username:token'
    return accounts
