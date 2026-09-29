import os

def get_data_path() -> str:
    return os.getenv('DATA_PATH', './data')

def get_db_path() -> str:
    return os.path.join(get_data_path(), 'tracked_accounts.db')