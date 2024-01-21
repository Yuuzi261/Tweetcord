from tweety import Twitter
from dotenv import load_dotenv
import os
import asyncio

from src.log import setup_logger

log = setup_logger(__name__)

load_dotenv()

async def sync_db(follow_list):
    app = Twitter("session")
    app.load_auth_token(os.getenv('TWITTER_TOKEN'))
    
    for user in follow_list:
        user_id = user[0]
        app.follow_user(user_id)
        app.enable_user_notification(user_id)
        await asyncio.sleep(1)
        
    log.info('synchronization with database completed')