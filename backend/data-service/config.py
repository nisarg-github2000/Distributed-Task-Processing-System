from motor.motor_asyncio import AsyncIOMotorClient
import os
client = AsyncIOMotorClient(os.environ['MONGODB_URL'])
db = client[os.environ['DATABASE_NAME']]
collection = db[os.environ['COLLECTION_NAME']]
