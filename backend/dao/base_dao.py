from datetime import datetime
from typing import Any


class BaseDAO:
    def __init__(self, collezione: list[dict[str, Any]] | None = None):
        self.collezione = collezione or []

    async def insert_one(self, documento: dict[str, Any]) -> str:
        doc = dict(documento)
        doc.setdefault("_id", str(len(self.collezione) + 1))
        doc.setdefault("created_at", datetime.utcnow())
        self.collezione.append(doc)
        return doc["_id"]

    async def find_one(self, filtro: dict[str, Any]) -> dict[str, Any] | None:
        for doc in self.collezione:
            if all(doc.get(k) == v for k, v in filtro.items()):
                return dict(doc)
        return None

    async def find_many(self, filter_query: dict[str, Any] | None = None, **_: Any) -> list[dict[str, Any]]:
        filtro = filter_query or {}
        risultati: list[dict[str, Any]] = []
        for doc in self.collezione:
            if all(doc.get(k) == v for k, v in filtro.items()):
                risultati.append(dict(doc))
        return risultati

    async def update_one(self, filtro: dict[str, Any], dati: dict[str, Any]) -> bool:
        for doc in self.collezione:
            if all(doc.get(k) == v for k, v in filtro.items()):
                doc.update(dati)
                doc["updated_at"] = datetime.utcnow()
                return True
        return False

    async def delete_one(self, filtro: dict[str, Any]) -> bool:
        for i, doc in enumerate(self.collezione):
            if all(doc.get(k) == v for k, v in filtro.items()):
                del self.collezione[i]
                return True
        return False

    async def update_by_id(self, document_id: str, update_data: dict[str, Any]) -> bool:
        return await self.update_one({"_id": document_id}, update_data)

    async def delete_by_id(self, document_id: str) -> bool:
        return await self.delete_one({"_id": document_id})

    async def count(self, filter_query: dict[str, Any] | None = None) -> int:
        return len(await self.find_many(filter_query))
