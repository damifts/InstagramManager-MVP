from datetime import datetime
from enum import Enum
from typing import Any

try:
    from dao.base_dao import BaseDAO
    from database.connection import get_database
except ModuleNotFoundError:
    from backend.dao.base_dao import BaseDAO
    from backend.database.connection import get_database


class PostStatus(str, Enum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    PUBLISHED = "published"


class PostDAO(BaseDAO):
    def __init__(self):
        db = get_database()
        super().__init__(db["posts"])

    async def create_post(
        self,
        testo: str,
        social_target: str,
        data_programmazione: datetime | None = None,
        status: PostStatus = PostStatus.DRAFT,
    ) -> str:
        if not testo.strip() or not social_target.strip():
            raise ValueError("testo e social_target sono obbligatori")

        stato = status
        if data_programmazione and stato == PostStatus.DRAFT:
            stato = PostStatus.SCHEDULED

        return await self.insert_one(
            {
                "testo": testo.strip(),
                "social_target": social_target.strip(),
                "status": stato,
                "data_programmazione": data_programmazione,
            }
        )

    async def get_posts_by_status(self, status: PostStatus) -> list[dict[str, Any]]:
        return await self.find_many({"status": status})

    async def update_post_status(self, post_id: str, new_status: PostStatus) -> bool:
        return await self.update_by_id(post_id, {"status": new_status})

    async def publish_post(self, post_id: str) -> bool:
        return await self.update_by_id(post_id, {"status": PostStatus.PUBLISHED, "published_at": datetime.utcnow()})
