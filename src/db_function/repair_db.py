import os

import aiosqlite

async def auto_repair_mismatched_clients(invalid_clients: set[str]):
    default_client = os.getenv('TWITTER_TOKEN').split(',')[0].split(':')[0]
    
    async with aiosqlite.connect(os.path.join(os.getenv('DATA_PATH'), 'tracked_accounts.db')) as db:
        async with db.execute('SELECT id, client_used FROM user') as cursor:
            rows = await cursor.fetchall()
            updates = [(default_client, user_id) for user_id, client_used in rows if client_used in invalid_clients]
            
            if updates:
                await db.executemany('UPDATE user SET client_used = ? WHERE id = ?', updates)
                await db.commit()