import os
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure, PyMongoError
import asyncio
from dotenv import load_dotenv
import pymongo

load_dotenv()

# Configurazione MongoDB
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "social_manager_db")

# Client globale MongoDB
_mongo_client: AsyncIOMotorClient | None = None
_database = None


async def connect_to_mongodb(max_retries: int = 3, delay: float = 1.0):
    """
    Stabilisce connessione con MongoDB con retry logic
    
    Parametri:
        max_retries: numero massimo di tentativi
        delay: delay iniziale tra retry in secondi (incrementa ad ogni retry)
    """
    user = os.getenv("MONGO_DB_USER")
    password = os.getenv("MONGO_DB_PW")

    if user and password:
<<<<<<< HEAD
        MONGO_URI = f"mongodb://{user}:{password}@localhost:27017/{MONGO_DB_NAME}?authSource={MONGO_DB_NAME}"
    else:
        MONGO_URI = f"mongodb://localhost:27017/{MONGO_DB_NAME}"
=======
        mongo_uri = (
            f"mongodb://{user}:{password}@localhost:27017/{MONGO_DB_NAME}?authSource={MONGO_DB_NAME}"
        )
    else:
        mongo_uri = f"mongodb://localhost:27017/{MONGO_DB_NAME}"
>>>>>>> f8664637ecf714755898d6e100f74053591e7c84

    global _mongo_client, _database

    attempt = 0
    while attempt < max_retries:
        try:
            _mongo_client = AsyncIOMotorClient(
<<<<<<< HEAD
                MONGO_URI,
=======
                mongo_uri,
>>>>>>> f8664637ecf714755898d6e100f74053591e7c84
                serverSelectionTimeoutMS=5000,
                maxPoolSize=10,
                minPoolSize=1
            )

            # Test connessione con ping
            await _mongo_client.admin.command('ping')

            _database = _mongo_client[MONGO_DB_NAME]
            print(f"✅ Connesso a MongoDB: {MONGO_DB_NAME} (tentativo {attempt + 1})")
            return _database

        except ConnectionFailure as e:
            attempt += 1
            print(f"❌ Errore connessione MongoDB (tentativo {attempt}/{max_retries}): {e}")
            if attempt < max_retries:
                sleep_time = delay * (2 ** (attempt - 1))  # exponential backoff
                print(f"⏳ Ritento tra {sleep_time:.1f} secondi...")
                await asyncio.sleep(sleep_time)
            else:
                print("💥 Numero massimo di retry raggiunto. Connessione fallita.")
                raise

        except PyMongoError as e:
            print(f"❌ Errore generico MongoDB: {e}")
            raise


async def verify_connection() -> bool:
    """
    Issue #19: Verifica connessione con ping, query semplice, latenza, permessi, spazio
    
    Returns:
        bool: True se connessione OK, False altrimenti
    """
    try:
        db = get_database()

        # Ping test + misurazione latenza
        import time
        start_time = time.perf_counter()
        await db.client.admin.command('ping')
        latency = (time.perf_counter() - start_time) * 1000  # in ms
        print(f"⏱ Latenza ping: {latency:.2f} ms")

        # Query semplice test
        collections = await db.list_collection_names()
        print(f"✅ Collections: {collections}")

        # Verifica permessi utente
        user_info = await db.command("connectionStatus")
        roles = user_info.get('authInfo', {}).get('authenticatedUserRoles', [])
        print(f"👤 Ruoli utente: {roles}")

        # Controllo spazio disponibile (approssimativo)
        stats = await db.command("dbStats")
        data_size_mb = stats.get("dataSize", 0) / (1024 * 1024)
        storage_size_mb = stats.get("storageSize", 0) / (1024 * 1024)
        print(f"💾 Data size: {data_size_mb:.2f} MB, Storage size: {storage_size_mb:.2f} MB")

        return True

    except Exception as e:
        print(f"❌ Verifica connessione fallita: {e}")
        return False


async def close_mongodb_connection():
    """
    Chiude connessione MongoDB
    """
    global _mongo_client
    if _mongo_client:
        _mongo_client.close()
        print("✅ Connessione MongoDB chiusa")


def get_database():
    """
    Restituisce database MongoDB corrente
    
    Returns:
        Database MongoDB instance
    
    Raises:
        RuntimeError: Se database non è connesso
    """
    if _database is None:
        raise RuntimeError("Database non connesso. Chiamare connect_to_mongodb() prima.")
    return _database


def get_database_sync():
    """
    Versione sincrona per compatibilità Streamlit
    
    Nota:
        Usa pymongo sincrono per evitare problemi con loop asyncio in Streamlit
    """
    global _database, _mongo_client

    if _database is None:
        # Connessione sincrona fallback
        user = os.getenv("MONGO_DB_USER")
        password = os.getenv("MONGO_DB_PW")

        if user and password:
            uri = f"mongodb://{user}:{password}@localhost:27017/{MONGO_DB_NAME}?authSource={MONGO_DB_NAME}"
        else:
            uri = f"mongodb://localhost:27017/{MONGO_DB_NAME}"

        _mongo_client = pymongo.MongoClient(uri, serverSelectionTimeoutMS=5000)
        _database = _mongo_client[MONGO_DB_NAME]
        try:
            _mongo_client.admin.command("ping")
            print(f"✅ Connessione sincrona MongoDB OK: {_database.name}")
        except Exception as e:
            raise RuntimeError(f"Connessione sincrona fallita: {e}")
    return _database



async def main():
 await connect_to_mongodb()

 await verify_connection()

 print("Tutto a posto")


if __name__ == "__main__":
    asyncio.run(main())
