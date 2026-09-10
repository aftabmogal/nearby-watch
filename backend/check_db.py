"""
Diagnostic script — not part of the app, just for figuring out where your
data actually lives. Run with: python check_db.py
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings


async def main():
    masked_uri = settings.MONGO_URI.replace(settings.MONGO_URI.split(":")[2].split("@")[0], "****")
    print(f"MONGO_URI the app is actually loading: {masked_uri}")
    print(f"MONGO_DB_NAME the app is actually loading: {settings.MONGO_DB_NAME}")
    print()

    client = AsyncIOMotorClient(settings.MONGO_URI)

    print("Databases visible on this cluster (direct from MongoDB, not the Atlas website):")
    db_names = await client.list_database_names()
    for name in db_names:
        print(f"  - {name}")
    print()

    db = client[settings.MONGO_DB_NAME]
    collections = await db.list_collection_names()
    print(f"Collections inside '{settings.MONGO_DB_NAME}':")
    if not collections:
        print("  (none — this database is empty or doesn't exist yet)")
    for c in collections:
        count = await db[c].count_documents({})
        print(f"  - {c}: {count} documents")


if __name__ == "__main__":
    asyncio.run(main())