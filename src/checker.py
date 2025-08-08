import os

from src.db_function.readonly_db import connect_readonly
from src.log import setup_logger
from src.constants import VALID_PROXY_SERVICES

log = setup_logger(__name__)


def check_configs(configs):
    REQUIRED_KEYS = {
        'root': [
            'prefix', 'activity_name', 'activity_type', 'users_list_pagination_size',
            'users_list_page_counter_position', 'tweets_check_period', 'tweets_updater_retry_delay',
            'tasks_monitor_check_period', 'tasks_monitor_log_period', 'auth_max_attempts',
            'auto_change_client', 'auto_turn_off_notification', 'auto_unfollow',
            'auto_repair_mismatched_clients', 'embed', 'default_message', 'emoji_auto_format'
        ],
        'embed': {
            'type': [],
            'built_in': ['fx_image', 'video_link_button', 'legacy_logo'],
            'proxy': ['service', 'domain_name', 'original_url_button', 'auto_translation']
        }
    }
    
    def check_missing_keys(required_keys, config_section, section_name=''):
        missing_keys = [key for key in required_keys if key not in config_section]
        if missing_keys:
            log.error(f'missing required {section_name}config keys: {missing_keys}')
            return False
        return True
    
    if not check_missing_keys(REQUIRED_KEYS['root'], configs):
        return False

    embed = configs['embed']
    for section, keys in REQUIRED_KEYS['embed'].items():
        if section not in embed:
            log.error(f'missing required embed config keys: {section}')
            return False
        
        if not check_missing_keys(keys, embed[section], f'{section} '):
            return False
        
    if not check_missing_keys(['enabled', 'default_language'], embed['proxy']['auto_translation'], 'proxy.auto_translation '):
        return False
        
    pcpos = configs['users_list_page_counter_position']
    if pcpos not in ['title', 'footer']:
        log.warning(f"invalid page counter position: {pcpos}, will be treated as 'title' and continue execution")

    embed_type = embed['type']
    if embed_type not in ['built_in', 'proxy']:
        log.warning(f"invalid type: {embed_type}, will be treated as 'built_in' and continue execution")
        
    if embed_type == 'proxy':
        proxy_config = embed['proxy']
        service = proxy_config['service']
        domain_name = proxy_config['domain_name']

        if service not in VALID_PROXY_SERVICES:
            log.warning(f"invalid service: {service}. Allowed values: {list(VALID_PROXY_SERVICES.keys())}. Will be treated as '{list(VALID_PROXY_SERVICES.keys())[0]}' and continue execution")
            service = list(VALID_PROXY_SERVICES.keys())[0]

        if domain_name not in VALID_PROXY_SERVICES[service]:
            log.warning(f"invalid domain name: {domain_name} for service: {service}. Allowed values: {VALID_PROXY_SERVICES[service]}. Will be treated as '{VALID_PROXY_SERVICES[service][0]}' and continue execution")

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
