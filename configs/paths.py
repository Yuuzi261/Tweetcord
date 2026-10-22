import os

def get_data_path() -> str:
    return os.getenv('DATA_PATH', './data')

def get_db_path() -> str:
    return os.path.join(get_data_path(), 'tracked_accounts.db')

# session 檔放在 DATA_PATH，Docker 重建 container 後才不會遺失
# 只傳帳號名稱的話，tweety 會去工作目錄找 session，找不到就變成未登入
def get_session_path(account_name: str) -> str:
    return os.path.join(get_data_path(), account_name)