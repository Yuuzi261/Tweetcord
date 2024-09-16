import asyncio

from dotenv import load_dotenv
from tweety import Twitter

from src.log import setup_logger
from src.utils import get_accounts

log = setup_logger(__name__)


async def sync_db(follow_list: dict[str, str]) -> None:

    apps: dict[str, Twitter] = {}
    for account_name, account_token in get_accounts().items():
        app = Twitter(account_name)
        app.load_auth_token(account_token)
        apps[account_name] = app

    for user_id, client_used in follow_list.items():
        app = apps[client_used]
        app.follow_user(user_id)
        app.enable_user_notification(user_id)
        await asyncio.sleep(1)

    log.info('synchronization with database completed')
