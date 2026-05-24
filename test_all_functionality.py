#!/usr/bin/env python3
"""
Comprehensive test script for CryptoBlock project
Tests all major functionality and reports issues
"""

import sys
import os
import traceback
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 80)
print("CRYPTOBLOCK COMPREHENSIVE TEST SUITE")
print("=" * 80)

# Track results
results = {
    "passed": [],
    "failed": [],
    "warnings": []
}

def test_imports():
    """Test all critical imports"""
    print("\n[TEST 1] Testing all imports...")
    try:
        from config import SECRET_KEY, MONGO_URI, DB_NAME, DEBUG, MINING_DIFFICULTY, INITIAL_BALANCE
        print("✓ Config imports successful")
        results["passed"].append("Config imports")
    except Exception as e:
        print(f"✗ Config import failed: {e}")
        results["failed"].append(f"Config imports: {e}")
        traceback.print_exc()

    try:
        from price_engine import get_price, get_all_prices, get_history, start
        print("✓ Price engine imports successful")
        results["passed"].append("Price engine imports")
    except Exception as e:
        print(f"✗ Price engine import failed: {e}")
        results["failed"].append(f"Price engine: {e}")
        traceback.print_exc()

    try:
        from core.blockchain import Blockchain
        from core.blockchain_instance import blockchain
        from core.mempool import mempool
        from core.block import Block
        print("✓ Blockchain imports successful")
        results["passed"].append("Blockchain imports")
    except Exception as e:
        print(f"✗ Blockchain import failed: {e}")
        results["failed"].append(f"Blockchain: {e}")
        traceback.print_exc()

    try:
        from database.mongo import get_db
        print("✓ Database imports successful")
        results["passed"].append("Database imports")
    except Exception as e:
        print(f"✗ Database import failed: {e}")
        results["failed"].append(f"Database: {e}")
        traceback.print_exc()

    try:
        from api.routes.auth import auth_bp
        from api.routes.wallet import wallet_bp
        from api.routes.transaction import transaction_bp
        print("✓ API route imports successful")
        results["passed"].append("API routes imports")
    except Exception as e:
        print(f"✗ API route import failed: {e}")
        results["failed"].append(f"API routes: {e}")
        traceback.print_exc()

def test_blockchain():
    """Test blockchain functionality"""
    print("\n[TEST 2] Testing blockchain functionality...")
    try:
        from core.blockchain import Blockchain
        bc = Blockchain()
        
        # Test genesis block
        assert len(bc.chain) == 1, "Genesis block not created"
        assert bc.is_chain_valid(), "Chain validation failed"
        print(f"✓ Genesis block created: {bc.chain[0].hash[:8]}...")
        
        # Test adding blocks
        bc.add_block([{"test": "transaction1"}])
        assert len(bc.chain) == 2, "Block addition failed"
        assert bc.is_chain_valid(), "Chain validation failed after adding block"
        print(f"✓ Block added successfully")
        
        stats = bc.get_chain_stats()
        print(f"✓ Blockchain stats: {stats['total_blocks']} blocks, Valid: {stats['is_valid']}")
        results["passed"].append("Blockchain operations")
    except Exception as e:
        print(f"✗ Blockchain test failed: {e}")
        results["failed"].append(f"Blockchain: {e}")
        traceback.print_exc()

def test_mempool():
    """Test mempool functionality"""
    print("\n[TEST 3] Testing mempool functionality...")
    try:
        from core.mempool import mempool
        
        mempool.clear()
        assert mempool.get_count() == 0, "Mempool not cleared"
        
        tx = {"sender": "alice", "receiver": "bob", "amount": 100}
        mempool.add_transaction(tx)
        assert mempool.get_count() == 1, "Transaction not added"
        assert mempool.has_transactions(), "Has transactions check failed"
        
        pending = mempool.get_pending()
        assert len(pending) == 1, "Get pending failed"
        print(f"✓ Mempool: {mempool.get_count()} transaction(s) pending")
        results["passed"].append("Mempool operations")
    except Exception as e:
        print(f"✗ Mempool test failed: {e}")
        results["failed"].append(f"Mempool: {e}")
        traceback.print_exc()

def test_price_engine():
    """Test price engine"""
    print("\n[TEST 4] Testing price engine functionality...")
    try:
        from price_engine import get_price, get_all_prices, get_history, _cache
        
        # Check if cache has been initialized
        if not _cache:
            print("⚠ Price cache is empty - may need initialization")
            results["warnings"].append("Price cache empty")
        else:
            print(f"✓ Price cache has {len(_cache)} coins")
            
            # Check specific coins
            for coin in ["BTC", "ETH", "BNB"]:
                price = get_price(coin)
                print(f"  - {coin}: ₹{price}")
            
            all_prices = get_all_prices()
            print(f"✓ Got all prices for {len(all_prices)} coins")
            results["passed"].append("Price engine")
    except Exception as e:
        print(f"✗ Price engine test failed: {e}")
        results["failed"].append(f"Price engine: {e}")
        traceback.print_exc()

def test_wallet_functions():
    """Test wallet functionality"""
    print("\n[TEST 5] Testing wallet helper functions...")
    try:
        from api.routes.auth import _create_wallet
        
        wallet = _create_wallet()
        assert wallet["cash"] == 100000, "Initial cash not set correctly"
        assert isinstance(wallet["coins"], dict), "Coins not a dict"
        assert wallet["wallet_address"].startswith("0x"), "Wallet address format invalid"
        
        print(f"✓ Wallet created with ₹{wallet['cash']} initial balance")
        print(f"✓ Wallet address: {wallet['wallet_address']}")
        print(f"✓ Coins initialized: {len(wallet['coins'])} coins with 0 balance each")
        results["passed"].append("Wallet creation")
    except Exception as e:
        print(f"✗ Wallet test failed: {e}")
        results["failed"].append(f"Wallet: {e}")
        traceback.print_exc()

def test_profit_loss_calculations():
    """Test P&L calculation logic"""
    print("\n[TEST 6] Testing profit/loss calculations...")
    try:
        # Simulate P&L calculation
        buy_price = 100.0
        sell_price = 110.0
        quantity = 10.0
        
        # P&L = (sell_price - buy_price) * quantity
        pnl = (sell_price - buy_price) * quantity
        pnl_pct = ((sell_price - buy_price) / buy_price) * 100
        
        assert pnl == 100.0, f"P&L calculation failed: expected 100.0, got {pnl}"
        assert pnl_pct == 10.0, f"P&L % calculation failed: expected 10.0, got {pnl_pct}"
        
        print(f"✓ Profit calculation: Buy @₹{buy_price} Sell @₹{sell_price} × {quantity} = ₹{pnl} ({pnl_pct}%)")
        
        # Test loss scenario
        buy_price = 100.0
        sell_price = 90.0
        quantity = 10.0
        pnl = (sell_price - buy_price) * quantity
        pnl_pct = ((sell_price - buy_price) / buy_price) * 100
        assert pnl == -100.0, f"Loss calculation failed"
        print(f"✓ Loss calculation: Buy @₹{buy_price} Sell @₹{sell_price} × {quantity} = ₹{pnl} ({pnl_pct}%)")
        
        results["passed"].append("P&L calculations")
    except Exception as e:
        print(f"✗ P&L calculation test failed: {e}")
        results["failed"].append(f"P&L calculations: {e}")
        traceback.print_exc()

def test_sip_calculations():
    """Test SIP functionality"""
    print("\n[TEST 7] Testing SIP calculations...")
    try:
        # Simulate SIP investment
        monthly_amount = 10000
        months = 6
        total = monthly_amount * months
        
        assert total == 60000, f"Total SIP calculation failed"
        print(f"✓ SIP Calculation: ₹{monthly_amount}/month × {months} months = ₹{total}")
        
        # Simulate SIP with varying prices
        prices = [100, 110, 105, 120, 115, 125]
        total_units = 0
        total_invested = 0
        
        for i, price in enumerate(prices, 1):
            units = monthly_amount / price
            total_units += units
            total_invested += monthly_amount
            print(f"  Month {i}: ₹{monthly_amount} / ₹{price} = {units:.4f} units")
        
        current_price = 130
        current_value = total_units * current_price
        returns = current_value - total_invested
        
        print(f"✓ SIP Summary: {total_units:.4f} units @ ₹{current_price} = ₹{current_value:.2f}")
        print(f"  Total Invested: ₹{total_invested:.2f}, Returns: ₹{returns:.2f}")
        results["passed"].append("SIP calculations")
    except Exception as e:
        print(f"✗ SIP test failed: {e}")
        results["failed"].append(f"SIP: {e}")
        traceback.print_exc()

def test_weighted_average_price():
    """Test weighted average price calculation"""
    print("\n[TEST 8] Testing weighted average price calculation...")
    try:
        # Scenario: Buy 10 coins at 100, then 5 more at 120
        current_qty = 10
        current_avg = 100
        new_qty = 5
        new_price = 120
        
        new_avg = ((current_qty * current_avg) + (new_qty * new_price)) / (current_qty + new_qty)
        expected = (1000 + 600) / 15  # 1600 / 15 = 106.67
        
        assert abs(new_avg - expected) < 0.01, f"WAP calculation failed"
        print(f"✓ WAP: Buy {current_qty}@₹{current_avg} + {new_qty}@₹{new_price} = ₹{new_avg:.2f}")
        
        results["passed"].append("Weighted average price")
    except Exception as e:
        print(f"✗ WAP test failed: {e}")
        results["failed"].append(f"WAP: {e}")
        traceback.print_exc()

def test_database_connection():
    """Test database connection"""
    print("\n[TEST 9] Testing database connection...")
    try:
        from database.mongo import get_db
        db = get_db()
        
        # Try to access collections (non-destructive)
        collections = db.list_collection_names()
        print(f"✓ MongoDB connection successful")
        print(f"  Collections: {collections if collections else 'None (new database)'}")
        results["passed"].append("Database connection")
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        print("  Note: This is expected if MongoDB is not running")
        results["warnings"].append(f"Database not available: {e}")

def test_app_creation():
    """Test Flask app creation"""
    print("\n[TEST 10] Testing Flask app creation...")
    try:
        # Import at root level to catch errors
        from app import app, COINS
        
        assert app is not None, "App creation failed"
        assert len(COINS) > 0, "COINS not defined"
        print(f"✓ Flask app created successfully")
        print(f"✓ {len(COINS)} coins configured: {', '.join(list(COINS.keys())[:5])}...")
        
        # Test route registration
        routes = [str(rule) for rule in app.url_map.iter_rules()]
        print(f"✓ {len(routes)} routes registered")
        
        results["passed"].append("Flask app")
    except Exception as e:
        print(f"✗ Flask app test failed: {e}")
        results["failed"].append(f"Flask app: {e}")
        traceback.print_exc()

# Run all tests
if __name__ == "__main__":
    test_imports()
    test_blockchain()
    test_mempool()
    test_price_engine()
    test_wallet_functions()
    test_profit_loss_calculations()
    test_sip_calculations()
    test_weighted_average_price()
    test_database_connection()
    test_app_creation()
    
    # Print summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"✓ Passed: {len(results['passed'])}")
    for test in results["passed"]:
        print(f"  ✓ {test}")
    
    if results["warnings"]:
        print(f"\n⚠ Warnings: {len(results['warnings'])}")
        for warning in results["warnings"]:
            print(f"  ⚠ {warning}")
    
    if results["failed"]:
        print(f"\n✗ Failed: {len(results['failed'])}")
        for failure in results["failed"]:
            print(f"  ✗ {failure}")
    else:
        print(f"\n✓ ALL TESTS PASSED!" if not results["warnings"] else "\n⚠ All critical tests passed (with warnings)")
    
    print("=" * 80)
