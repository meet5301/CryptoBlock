#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

print("=" * 60)
print("CryptoBlock - Startup Test")
print("=" * 60)

print("\n[1] Testing imports...")
try:
    from flask import Flask
    print("[OK] Flask imported")
except Exception as e:
    print(f"[ERROR] Flask: {e}")
    sys.exit(1)

try:
    from flask_socketio import SocketIO
    print("[OK] Flask-SocketIO imported")
except Exception as e:
    print(f"[ERROR] Flask-SocketIO: {e}")
    sys.exit(1)

try:
    from pymongo import MongoClient
    print("[OK] PyMongo imported")
except Exception as e:
    print(f"[ERROR] PyMongo: {e}")
    sys.exit(1)

print("\n[2] Testing config...")
try:
    from config import MONGO_URI, DB_NAME, SECRET_KEY
    print("[OK] Config loaded")
    print(f"     MONGO_URI: {MONGO_URI}")
    print(f"     DB_NAME: {DB_NAME}")
except Exception as e:
    print(f"[ERROR] Config: {e}")
    sys.exit(1)

print("\n[3] Testing MongoDB connection...")
try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    client.server_info()
    print("[OK] MongoDB connected")
    db = client[DB_NAME]
    print(f"[OK] Database '{DB_NAME}' accessible")
except Exception as e:
    print(f"[ERROR] MongoDB: {e}")
    sys.exit(1)

print("\n[4] Testing database models...")
try:
    from database.mongo import get_db
    db = get_db()
    print("[OK] Database models loaded")
except Exception as e:
    print(f"[ERROR] Database models: {e}")
    sys.exit(1)

print("\n[5] Testing core modules...")
try:
    from core.blockchain_instance import blockchain
    print(f"[OK] Blockchain loaded (chain length: {len(blockchain.chain)})")
except Exception as e:
    print(f"[ERROR] Blockchain: {e}")
    sys.exit(1)

try:
    from core.mempool import mempool
    print("[OK] Mempool loaded")
except Exception as e:
    print(f"[ERROR] Mempool: {e}")
    sys.exit(1)

print("\n[6] Testing price engine...")
try:
    from price_engine import get_all_prices, get_price
    prices = get_all_prices()
    print(f"[OK] Price engine loaded ({len(prices)} coins cached)")
except Exception as e:
    print(f"[ERROR] Price engine: {e}")
    sys.exit(1)

print("\n[7] Testing API routes...")
try:
    from api.routes.auth import auth_bp
    from api.routes.blockchain import blockchain_bp
    from api.routes.wallet import wallet_bp
    print("[OK] API routes loaded")
except Exception as e:
    print(f"[ERROR] API routes: {e}")
    sys.exit(1)

print("\n[8] Creating Flask app...")
try:
    from app import app, socketio
    print("[OK] Flask app created")
    print("[OK] SocketIO initialized")
except Exception as e:
    print(f"[ERROR] Flask app: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)
print("[SUCCESS] All tests passed! App is ready to run.")
print("=" * 60)
print("\nTo start the app, run:")
print("  python app.py")
print("\nThen open: http://localhost:5000")
print("=" * 60)
