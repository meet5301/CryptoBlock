#!/usr/bin/env python
"""
Test advanced features: wallet transfers, blockchain mining, AI monitoring
"""
import requests
import json
import time

BASE_URL = "http://127.0.0.1:5000"

def get_session():
    """Login and return session"""
    session = requests.Session()
    data = {
        "email": "testuser@example.com",
        "password": "testpass123"
    }
    r = session.post(f"{BASE_URL}/login", data=data)
    if r.status_code == 200:
        return session
    return None

def test_register_second_user():
    """Register a second user for transfer testing"""
    print("\nRegistering second user...")
    data = {
        "name": "Second User",
        "email": "second@example.com",
        "password": "testpass123"
    }
    r = requests.post(f"{BASE_URL}/register", data=data)
    print(f"  Registration status: {r.status_code}")
    return r.status_code == 200

def test_send_crypto(session):
    """Test sending crypto to another user"""
    print("\nTesting send crypto...")
    transfer_data = {
        "receiver": "second@example.com",
        "rupees": 1000
    }
    r = session.post(f"{BASE_URL}/send_crypto", data=transfer_data)
    print(f"  Transfer status: {r.status_code}")
    if r.status_code == 200:
        print("  ✓ Transfer successful")
        return True
    else:
        print(f"  ✗ Transfer failed")
        return False

def test_wallet_detail(session):
    """Test wallet detail page"""
    print("\nTesting wallet detail...")
    r = session.get(f"{BASE_URL}/wallet/detail")
    print(f"  Wallet detail status: {r.status_code}")
    return r.status_code == 200

def test_wallet_history(session):
    """Test wallet history API"""
    print("\nTesting wallet history...")
    r = session.get(f"{BASE_URL}/wallet/history")
    result = r.json()
    print(f"  History status: {r.status_code}")
    print(f"  Transactions count: {len(result.get('transactions', []))}")
    return r.status_code == 200

def test_blockchain_stats(session):
    """Test blockchain stats API"""
    print("\nTesting blockchain stats...")
    r = session.get(f"{BASE_URL}/blockchain/stats")
    result = r.json()
    print(f"  Stats status: {r.status_code}")
    print(f"  Total blocks: {result.get('total_blocks')}")
    print(f"  Chain valid: {result.get('chain_valid')}")
    print(f"  Pending transactions: {result.get('pending_count')}")
    return r.status_code == 200

def test_ai_monitor_data(session):
    """Test AI monitor data"""
    print("\nTesting AI monitor...")
    r = session.get(f"{BASE_URL}/ai/monitor")
    print(f"  AI monitor status: {r.status_code}")
    return r.status_code == 200

def test_leaderboard(session):
    """Test leaderboard"""
    print("\nTesting leaderboard...")
    r = session.get(f"{BASE_URL}/leaderboard")
    print(f"  Leaderboard status: {r.status_code}")
    return r.status_code == 200

def test_notifications(session):
    """Test notifications"""
    print("\nTesting notifications...")
    r = session.get(f"{BASE_URL}/api/notifications")
    print(f"  Notifications status: {r.status_code}")
    return r.status_code == 200

def main():
    print("="*50)
    print("CRYPTOBLOCK ADVANCED FEATURES TEST")
    print("="*50)
    
    # Register second user
    test_register_second_user()
    
    session = get_session()
    if not session:
        print("✗ Failed to login")
        return
    
    results = []
    
    # Test send crypto
    try:
        results.append(("Send Crypto", test_send_crypto(session)))
    except Exception as e:
        print(f"✗ Send crypto failed: {e}")
        results.append(("Send Crypto", False))
    
    # Test wallet detail
    try:
        results.append(("Wallet Detail", test_wallet_detail(session)))
    except Exception as e:
        print(f"✗ Wallet detail failed: {e}")
        results.append(("Wallet Detail", False))
    
    # Test wallet history
    try:
        results.append(("Wallet History", test_wallet_history(session)))
    except Exception as e:
        print(f"✗ Wallet history failed: {e}")
        results.append(("Wallet History", False))
    
    # Test blockchain stats
    try:
        results.append(("Blockchain Stats", test_blockchain_stats(session)))
    except Exception as e:
        print(f"✗ Blockchain stats failed: {e}")
        results.append(("Blockchain Stats", False))
    
    # Test AI monitor
    try:
        results.append(("AI Monitor", test_ai_monitor_data(session)))
    except Exception as e:
        print(f"✗ AI monitor failed: {e}")
        results.append(("AI Monitor", False))
    
    # Test leaderboard
    try:
        results.append(("Leaderboard", test_leaderboard(session)))
    except Exception as e:
        print(f"✗ Leaderboard failed: {e}")
        results.append(("Leaderboard", False))
    
    # Test notifications
    try:
        results.append(("Notifications", test_notifications(session)))
    except Exception as e:
        print(f"✗ Notifications failed: {e}")
        results.append(("Notifications", False))
    
    # Summary
    print("\n" + "="*50)
    print("TEST SUMMARY")
    print("="*50)
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    print("="*50)

if __name__ == "__main__":
    main()
