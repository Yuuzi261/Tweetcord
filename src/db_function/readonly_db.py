import aiosqlite

async def connect_readonly(db_path: str):
    uri = f'file:{db_path}?mode=ro'
    return aiosqlite.connect(uri, uri=True)
