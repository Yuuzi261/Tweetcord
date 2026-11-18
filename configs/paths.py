import os

def get_data_path() -> str:
    return os.getenv('DATA_PATH', './data')

def get_db_path() -> str:
    return os.path.join(get_data_path(), 'tracked_accounts.db')

# Store tweety session files under DATA_PATH so they persist across container restarts.
def get_session_path(account_name: str) -> str:
    return os.path.join(get_data_path(), account_name)