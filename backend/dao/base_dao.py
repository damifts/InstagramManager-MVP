import logging
from typing import TypeVar, Generic, List, Dict, Any, Optional, Type
from motor.motor_asyncio import AsyncIOMotorCollection
from bson import ObjectId
from datetime import datetime
from pydantic import BaseModel, ValidationError

# Configurazione logging di base
logger = logging.getLogger("DAO")
logging.basicConfig(level=logging.INFO)

T = TypeVar('T', bound=BaseModel)

class BaseDAO(Generic[T]):
    """
    DAO base potenziato con Soft Delete, Pydantic e Logging.
    """
    
    def __init__(self, collection: AsyncIOMotorCollection, model: Type[T] = None):
        self.collection = collection
        self.model = model # Per validazione Pydantic

    def _convert_id(self, doc: Dict[str, Any]) -> Dict[str, Any]:
        """Utility per convertire ObjectId in stringa ricorsivamente."""
        if doc and "_id" in doc:
            doc["_id"] = str(doc["_id"])
        return doc

    # --- CREATE ---
    async def insert_one(self, document: Dict[str, Any]) -> str:
        """Issue #21: Inserimento con validazione e timestamp."""
        # Aggiunta timestamp automatici
        document["created_at"] = datetime.now()
        document["updated_at"] = document["created_at"]
        document["is_deleted"] = False # Per Soft Delete

        # Validazione Pydantic (se il modello è fornito)
        if self.model:
            try:
                self.model(**document)
            except ValidationError as e:
                logger.error(f"Validazione fallita in insert_one: {e}")
                raise

        result = await self.collection.insert_one(document)
        logger.info(f"Inserito documento {result.inserted_id} in {self.collection.name}")
        return str(result.inserted_id)

    # --- READ ---
    async def find_one(self, filter_query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Trova un documento escludendo quelli cancellati logicamente."""
        # Forza il filtro per escludere i soft-deleted
        filter_query["is_deleted"] = {"$ne": True}
        
        document = await self.collection.find_one(filter_query)
        return self._convert_id(document)

    async def find_many(
        self, 
        filter_query: Dict[str, Any] = None,
        limit: int = 100,
        skip: int = 0,
        sort: List[tuple] = None
    ) -> List[Dict[str, Any]]:
        """Lettura con paginazione e filtro Soft Delete."""
        if filter_query is None: filter_query = {}
        filter_query["is_deleted"] = {"$ne": True}
        
        cursor = self.collection.find(filter_query).limit(limit).skip(skip)
        if sort:
            cursor = cursor.sort(sort)
        
        documents = await cursor.to_list(length=limit)
        return [self._convert_id(doc) for doc in documents]

    # --- UPDATE ---
    async def update_one(self, filter_query: Dict[str, Any], update_data: Dict[str, Any]) -> bool:
        """Aggiornamento con timestamp automatico."""
        update_data["updated_at"] = datetime.now()
        
        # Impediamo che l'aggiornamento tocchi documenti cancellati
        filter_query["is_deleted"] = {"$ne": True}
        
        result = await self.collection.update_one(
            filter_query,
            {"$set": update_data}
        )
        return result.modified_count > 0

    # --- DELETE (SOFT DELETE) ---
    async def delete_one(self, filter_query: Dict[str, Any], hard_delete: bool = False) -> bool:
        """
        Issue #24: Implementazione Soft Delete.
        Se hard_delete=True, rimuove fisicamente dal DB.
        """
        if hard_delete:
            result = await self.collection.delete_one(filter_query)
            logger.warning(f"HARD DELETE eseguito su {filter_query}")
        else:
            # Soft delete: aggiorniamo il flag is_deleted
            result = await self.collection.update_one(
                filter_query,
                {"$set": {
                    "is_deleted": True,
                    "deleted_at": datetime.now()
                }}
            )
            logger.info(f"SOFT DELETE eseguito su {filter_query}")
            
        return (result.modified_count if not hard_delete else result.deleted_count) > 0

    async def restore(self, document_id: str) -> bool:
        """Ripristina un documento cancellato logicamente."""
        try:
            result = await self.collection.update_one(
                {"_id": ObjectId(document_id)},
                {"$set": {"is_deleted": False}, "$unset": {"deleted_at": ""}}
            )
            return result.modified_count > 0
        except: return False