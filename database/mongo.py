from pymongo import MongoClient
from config import MONGO_URI, DB_NAME

client = MongoClient(MONGO_URI)
db = client[DB_NAME]


def get_db():
    return db


def _ensure_indexes():
    db.users.create_index("email", unique=True)
    db.transactions.create_index("sender")
    db.transactions.create_index("receiver")
    db.transactions.create_index("timestamp")
    db.trades.create_index("email")
    db.sip.create_index("email")


_ensure_indexes()
