_db: dict[str, list[dict]] = {"posts": []}


async def connect_to_mongodb(*_, **__):
    return _db


async def verify_connection() -> bool:
    return True


async def close_mongodb_connection():
    return None


def get_database() -> dict[str, list[dict]]:
    return _db


def get_database_sync() -> dict[str, list[dict]]:
    return _db
