import asyncio

from tweety import Twitter

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
        app = apps[client_used]
        await app.follow_user(user_id)
        await app.enable_user_notification(user_id)
        await asyncio.sleep(1)

    log.info('synchronization with database completed')
