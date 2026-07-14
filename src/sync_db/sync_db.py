import asyncio

from tweety import Twitter
from tweety.exceptions import TwitterError

from src.log import setup_logger
from src.utils import get_accounts

log = setup_logger(__name__)


async def sync_db(follow_list: dict[str, str]) -> None:

    apps: dict[str, Twitter] = {}
    for account_name, _ in get_accounts().items():
        app = Twitter(account_name)
        await app.connect()
        apps[account_name] = app

    for user_id, client_used in follow_list.items():
        app = apps.get(client_used)
        if app is None:
            log.warning(f'client "{client_used}" for user {user_id} is not configured, skip synchronization')
            continue

        try:
            await app.follow_user(user_id)
            await app.enable_user_notification(user_id)
        except TwitterError as e:
            if '[108]' in str(e):
                log.warning(f'cannot find specified user: {user_id}, skip synchronization')
            else:
                log.error(f'failed to sync {user_id} to {client_used}: {e}')
        except Exception as e:
            log.error(f'failed to sync {user_id} to {client_used}: {e}')
            
        await asyncio.sleep(1)

    log.info('synchronization with database completed')
