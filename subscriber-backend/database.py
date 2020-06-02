from urllib.parse import urlparse

import motor.motor_asyncio
from motor.core import AgnosticClient, AgnosticCollection, AgnosticDatabase


async def get_db(url):
    parsed_url = urlparse(url)
    host = parsed_url.netloc
    db, collection = parsed_url.path[1:].split("/")

    client: AgnosticClient = motor.motor_asyncio.AsyncIOMotorClient(f"mongodb://{host}/{db}")
    db: AgnosticDatabase = client[db]
    collections: AgnosticCollection = db[collection]

    return collections
