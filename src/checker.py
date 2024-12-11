import os

import aiosqlite

from src.db_function.readonly_db import connect_readonly
from src.log import setup_logger

log = setup_logger(__name__)


def check_configs(configs):
    def check_missing_keys(required_keys, config_section, section_name=''):
        missing_keys = [key for key in required_keys if key not in config_section]
        if missing_keys:
            log.error(f'missing required {section_name}config keys: {missing_keys}')
            return False
        return True

    required_keys = [
        'prefix', 'activity_name', 'activity_type', 'tweets_check_period', 'tweets_updater_retry_delay',
        'tasks_monitor_check_period', 'tasks_monitor_log_period', 'auto_turn_off_notification',
        'auto_unfollow', 'auto_change_client', 'embed', 'default_message'
    ]

    if not check_missing_keys(required_keys, configs):
        return False

    if 'embed' in configs:
        embed_required_keys = {
            'type': [],
            'built_in': ['fx_image', 'video_link_button', 'footer_logo'],
            'fx_twitter': ['domain_name', 'original_url_button']
        }

        for section, keys in embed_required_keys.items():
            if section in configs['embed'] and not check_missing_keys(keys, configs['embed'][section], f'{section} '):
                return False

    if True not in [_ in configs['embed']['type'] for _ in ['built_in', 'fx_twitter']]:
        log.warning(f"invalid type: {configs['embed']['type']}, will be treated as 'built_in' and continue execution")
        
    if True not in [_ in configs['embed']['fx_twitter']['domain_name'] for _ in ['fxtwitter', 'fixupx']]:
        log.warning(f"invalid domain name: {configs['embed']['fx_twitter']['domain_name']}, will be treated as 'fxtwitter' and continue execution")

    log.info('configs check passed')
    return True


def check_env():
    required_keys = [
        'BOT_TOKEN', 'DATA_PATH', 'TWITTER_TOKEN'
    ]

    missing_keys = [key for key in required_keys if key not in os.environ]
    if missing_keys:
        log.error(f'missing required environment variables: {missing_keys}')
        return False

    twitter_token = os.getenv('TWITTER_TOKEN')
    if not all([(lambda e : len(e) == 2 and all(e))(entry.split(':')) for entry in twitter_token.split(',')]):
        log.error('invalid TWITTER_TOKEN format, must be in the form of "account_name:twitter_token"')
        return False

    log.info('environment variables check passed')
    return True

# currently only client_used is checked
async def check_db() -> set[str]:
    twitter_token = os.getenv('TWITTER_TOKEN')
    
    async with connect_readonly(os.path.join(os.getenv('DATA_PATH'), 'tracked_accounts.db')) as db:
        async with db.execute('SELECT client_used FROM user') as cursor:
            row = await cursor.fetchall()
            
    db_clients = set(client[0] for client in row)
    env_clients = set(entry.split(':')[0] for entry in twitter_token.split(','))
    invalid_clients = db_clients - env_clients
    
    return invalid_clients

def check_upgrade():
    if os.path.isfile('upgrade.py'):
        log.info('found upgrade.py, executing...')
        os.system('python upgrade.py')
