"""
Post DAO - Data Access Object per gestione Post
Issue #16, #20-25: Implementazione CRUD per Post

Estende BaseDAO con metodi specifici per Post
"""

<<<<<<< HEAD
from typing import List, Dict, Any, Optional,TypedDict
=======
from typing import List, Dict, Any, Optional, TypedDict
>>>>>>> f8664637ecf714755898d6e100f74053591e7c84
from datetime import datetime
from enum import Enum

from .base_dao import BaseDAO
from ..database import get_database
<<<<<<< HEAD
from enum import Enum
=======


>>>>>>> f8664637ecf714755898d6e100f74053591e7c84
class PostStatus(str, Enum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    PUBLISHED = "published"
    FAILED = "failed"
<<<<<<< HEAD
=======


>>>>>>> f8664637ecf714755898d6e100f74053591e7c84
class PostMetadata(TypedDict):
    views: int
    likes: int
    comments: int
    shares: int
<<<<<<< HEAD
class mediaPost:
        _id: str
        title: str
        content: str
        social_targets: str  
        status: PostStatus    
        created_at: datetime
        scheduled_at: datetime
        published_at: datetime
        metadata: PostMetadata
class PostDAO(BaseDAO):
    """
    DAO per gestione Post social
    

=======


class MediaPost(TypedDict, total=False):
    _id: str
    testo: str
    social_target: str
    status: PostStatus
    created_at: datetime
    updated_at: datetime
    data_programmazione: datetime
    published_at: datetime
    metadata: PostMetadata


class PostDAO(BaseDAO):
    """
    DAO per gestione Post social
>>>>>>> f8664637ecf714755898d6e100f74053591e7c84
    """

    def __init__(self):
        db = get_database()
        super().__init__(db["posts"])

    async def create_post(
<<<<<<< HEAD
        self, 
        testo: str, 
        data_programmazione: Optional[datetime] = None,
        status: PostStatus = PostStatus.DRAFT
    ) -> str:
        """Issue #21: Crea nuovo post con validazione Instagram"""
        
        # 1. Validazioni
        if not testo or not testo.strip():
            raise ValueError("Il contenuto del post non può essere vuoto")
        
        if len(testo) >= 2200:
            raise ValueError("Testo troppo lungo per Instagram (Max 2200 caratteri)")

        # 2. Generazione Preview (Logica corretta)
        def genera_preview(t: str, length: int = 50) -> str:
            return t[:length] + "..." if len(t) > length else t

        # 3. Preparazione Dati
        # Usiamo utcnow() per consistenza del database
        post_data = {
            "title": genera_preview(testo, 30), # Usiamo la preview come titolo se manca
            "content": testo,
            "status": status,
            "metadata": { # Inizializziamo i metadati a zero
                "views": 0, "likes": 0, "comments": 0, "shares": 0
            },
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        
        # 4. Logica Programmazione
        if data_programmazione:
            post_data["scheduled_at"] = data_programmazione
            # Se c'è una data, lo stato diventa automaticamente SCHEDULED
            if status == PostStatus.DRAFT:
                post_data["status"] = PostStatus.SCHEDULED
        
        return await self.insert_one(post_data)
    
    """async def get_posts_by_social(self, social_target: str) -> List[Dict[str, Any]]:
  
        Issue #22: Trova post per social network
        
        Args:
            social_target: Social network
            
        Returns:
            List[Dict]: Lista post
        """"""
        return await self.find_many(
            filter_query={"social_target": social_target},
            sort=[("created_at", -1)]  # Più recenti prima
        )"""
    
    
    async def get_posts_by_status(self, status: PostStatus) -> List[Dict[str, Any]]:
        """
        Issue #22: Trova post per status
        
        Args:
            status: draft, scheduled, published
            
        Returns:
            List[Dict]: Lista post
        """
=======
        self,
        testo: str,
        social_target: str,
        data_programmazione: Optional[datetime] = None,
        status: PostStatus = PostStatus.DRAFT,
    ) -> str:
        """
        Issue #21: Crea nuovo post
        """
        testo = testo.strip()
        social_target = social_target.strip()

        if not testo:
            raise ValueError("Testo vuoto")

        if not social_target:
            raise ValueError("Social target vuoto")

        if len(testo) >= 2200:
            raise ValueError("Testo troppo lungo per Instagram, valore massimo: 2200 caratteri")

        now = datetime.utcnow()
        post_data: MediaPost = {
            "testo": testo,
            "social_target": social_target,
            "status": status,
            "created_at": now,
            "updated_at": now,
        }

        if data_programmazione:
            post_data["data_programmazione"] = data_programmazione
            if status == PostStatus.DRAFT:
                post_data["status"] = PostStatus.SCHEDULED

        return await self.insert_one(post_data)

    async def get_posts_by_social(self, social_target: str) -> List[Dict[str, Any]]:
        return await self.find_many(
            filter_query={"social_target": social_target},
            sort=[("created_at", -1)],
        )

    async def get_posts_by_status(self, status: PostStatus) -> List[Dict[str, Any]]:
>>>>>>> f8664637ecf714755898d6e100f74053591e7c84
        return await self.find_many(
            filter_query={"status": status},
            sort=[("created_at", -1)],
        )

    async def get_scheduled_posts(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[Dict[str, Any]]:
<<<<<<< HEAD
        """
        Issue #22: Trova post programmati in range date
        
        Args:
            start_date: Data inizio
            end_date: Data fine
            
        Returns:
            List[Dict]: Post programmati
            

        """
        filter_query = {"status": "scheduled"}
        
=======
        filter_query: Dict[str, Any] = {"status": PostStatus.SCHEDULED}

>>>>>>> f8664637ecf714755898d6e100f74053591e7c84
        if start_date or end_date:
            date_filter: Dict[str, Any] = {}
            if start_date:
                date_filter["$gte"] = start_date
            if end_date:
                date_filter["$lte"] = end_date
            filter_query["data_programmazione"] = date_filter

        return await self.find_many(
            filter_query=filter_query,
            sort=[("data_programmazione", 1)],
        )

    async def update_post_status(self, post_id: str, new_status: PostStatus) -> bool:
        return await self.update_by_id(
            post_id,
            {"status": new_status, "updated_at": datetime.utcnow()},
        )

    async def publish_post(self, post_id: str) -> bool:
<<<<<<< HEAD
        """Issue #23: Pubblica post e aggiorna timestamp"""
=======
>>>>>>> f8664637ecf714755898d6e100f74053591e7c84
        return await self.update_by_id(
            post_id,
            {
                "status": PostStatus.PUBLISHED,
<<<<<<< HEAD
                "published_at": datetime.now()
            }
=======
                "published_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            },
>>>>>>> f8664637ecf714755898d6e100f74053591e7c84
        )

    async def search_posts(self, search_text: str) -> List[Dict[str, Any]]:
<<<<<<< HEAD
        """
        Issue #22: Ricerca full-text nei post
        
        Args:
            search_text: Testo da cercare
            
        Returns:
            List[Dict]: Post trovati
            

        """

        filter_query = {
            "testo": {"$regex": search_text, "$options": "i"}
        }
        
=======
        filter_query = {"testo": {"$regex": search_text, "$options": "i"}}
>>>>>>> f8664637ecf714755898d6e100f74053591e7c84
        return await self.find_many(filter_query)

    async def get_analytics_data(self, social_target: Optional[str] = None) -> Dict[str, Any]:
<<<<<<< HEAD
        """
        Aggregazione dati per analytics
        
        Args:
            social_target: Filtra per social (opzionale)
            
        Returns:
            Dict: Dati aggregati
            

        """
        match_stage = {}
=======
        match_stage: Dict[str, Any] = {}
>>>>>>> f8664637ecf714755898d6e100f74053591e7c84
        if social_target:
            match_stage = {"social_target": social_target}

        pipeline = [
            {"$match": match_stage},
            {"$group": {"_id": "$status", "count": {"$sum": 1}}},
        ]

        cursor = self.collection.aggregate(pipeline)
        results = await cursor.to_list(length=None)

        return {
            "by_status": results,
            "total": sum(r["count"] for r in results),
        }
