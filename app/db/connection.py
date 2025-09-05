import logging

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.core.config import settings

logger = logging.getLogger(__name__)

class Database:
    client: AsyncIOMotorClient = None
    db: AsyncIOMotorDatabase = None

database = Database()


async def connect_to_mongo():
    """Create database connection"""
    logger.info("Connecting to MongoDB...")
    database.client = AsyncIOMotorClient(settings.mongo_uri)
    database.db = database.client[settings.mongo_db]

    # Create indexes
    await create_indexes()
    logger.info("Connected to MongoDB")


async def close_mongo_connection():
    """Close database connection"""
    logger.info("Closing connection to MongoDB...")
    database.client.close()
    logger.info("Disconnected from MongoDB")


async def create_indexes():
    """Create compound indexes for analytics"""
    try:
        # Prompts indexes
        await database.db.prompts.create_index([("scenario", 1), ("length_bin", 1)])
        await database.db.prompts.create_index([("text", "text")])

        # Runs indexes
        await database.db.runs.create_index([("prompt_id", 1), ("model", 1)])
        await database.db.runs.create_index([("status", 1)])
        await database.db.runs.create_index([("model", 1), ("scenario", 1), ("length_bin", 1)])
        await database.db.runs.create_index([("created_at", -1)])

        # Audits indexes
        await database.db.audits.create_index([("run_id", 1)])
        await database.db.audits.create_index([("created_at", -1)])

        # Baselines indexes
        await database.db.baselines.create_index([("source", 1), ("model", 1)])

        logger.info("Database indexes created successfully")
    except Exception as e:
        logger.error(f"Error creating indexes: {e}")


def get_database() -> AsyncIOMotorDatabase:
    """Get database instance"""
    return database.db
