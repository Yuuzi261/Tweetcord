import os

import dotenv

from src.log import setup_logger

dotenv.load_dotenv()
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
            'fx_twitter': ['original_url_button']
        }

        for section, keys in embed_required_keys.items():
            if section in configs['embed'] and not check_missing_keys(keys, configs['embed'][section], f'{section} '):
                return False

    if True not in [_ in configs['embed']['type'] for _ in ['built_in', 'fx_twitter']]:
        log.warning(f"invalid type: {configs['embed']['type']}, will be treated as 'built_in' and continue execution")

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
    first_entry = twitter_token.split(',')[0].split(':')
    if len(first_entry) != 2 or not all(first_entry):
        log.error('invalid TWITTER_TOKEN format, must be in the form of "account_name:twitter_token"')
        return False

    log.info('environment variables check passed')
    return True
