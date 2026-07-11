from app.client import client
from app.db.index import db
from app.services.mapping import MappingService
from app.utills import import_submodules
from app.logger import logger

import_submodules("app.handlers")

async def main():
    logger.info('Preparing Resources')
    await db.connect()
    await MappingService.load_cache()

    await client.start() # type:ignore
    me = await client.get_me()
    logger.info(f"Bot started as {me.first_name} (@{me.username})")

    try:
        await client.run_until_disconnected()
    finally:
        await db.close()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())