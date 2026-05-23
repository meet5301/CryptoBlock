#!/usr/bin/env python
"""
Test all features of CryptoBlock platform
"""
import requests
import json
import time

BASE_URL = "http://127.0.0.1:5000"

def test_prices():
    """Test live price API"""
    print("Testing live prices...")
    r = requests.get(f"{BASE_URL}/api/prices")
    prices = r.json()
    print(f"✓ Got {len(prices)} coin prices")
    for coin, data in list(prices.items())[:3]:
        print(f"  {coin}: ₹{data['inr']} ({data['change_24h']}%)")
    return True

def test_register():
    """Test user registration"""
    print("\nTesting registration...")
    data = {
        "name": "Test User",
        "email": "testuser@example.com",
        "password": "testpass123"
    }
    r = requests.post(f"{BASE_URL}/register", data=data)
    print(f"✓ Registration status: {r.status_code}")
    return r.status_code == 200

def test_login():
    """Test user login"""
    print("\nTesting login...")
    session = requests.Session()
    data = {
        "email": "testuser@example.com",
        "password": "testpass123"
    }
    r = session.post(f"{BASE_URL}/login", data=data)
    print(f"✓ Login status: {r.status_code}")
    return session, r.status_code == 200

def test_dashboard(session):
    """Test dashboard access"""
    print("\nTesting dashboard...")
    r = session.get(f"{BASE_URL}/dashboard")
    print(f"✓ Dashboard status: {r.status_code}")
    return r.status_code == 200

def test_portfolio(session):
    """Test portfolio access"""
    print("\nTesting portfolio...")
    r = session.get(f"{BASE_URL}/portfolio")
    print(f"✓ Portfolio status: {r.status_code}")
    return r.status_code == 200

def test_sip_page(session):
    """Test SIP page access"""
    print("\nTesting SIP page...")
    r = session.get(f"{BASE_URL}/sip_page")
    print(f"✓ SIP page status: {r.status_code}")
    return r.status_code == 200

def test_wallet_page(session):
    """Test wallet page access"""
    print("\nTesting wallet page...")
    r = session.get(f"{BASE_URL}/wallet_page")
    print(f"✓ Wallet page status: {r.status_code}")
    return r.status_code == 200

def test_blockchain_page(session):
    """Test blockchain page access"""
    print("\nTesting blockchain page...")
    r = session.get(f"{BASE_URL}/blockchain/view")
    print(f"✓ Blockchain page status: {r.status_code}")
    return r.status_code == 200

def test_ai_monitor(session):
    """Test AI monitor page access"""
    print("\nTesting AI monitor...")
    r = session.get(f"{BASE_URL}/ai/monitor")
    print(f"✓ AI monitor status: {r.status_code}")
    return r.status_code == 200

def main():
    print("="*50)
    print("CRYPTOBLOCK FEATURE TEST")
    print("="*50)
    
    results = []
    
    # Test 1: Prices
    try:
        results.append(("Live Prices", test_prices()))
    except Exception as e:
        print(f"✗ Live prices failed: {e}")
        results.append(("Live Prices", False))
    
    # Test 2: Register
    try:
        results.append(("Registration", test_register()))
    except Exception as e:
        print(f"✗ Registration failed: {e}")
        results.append(("Registration", False))
    
    # Test 3: Login
    try:
        session, success = test_login()
        results.append(("Login", success))
    except Exception as e:
        print(f"✗ Login failed: {e}")
        results.append(("Login", False))
        session = None
    
    # Test authenticated pages if login succeeded
    if session:
        for test_func, name in [
            (test_dashboard, "Dashboard"),
            (test_portfolio, "Portfolio"),
            (test_sip_page, "SIP Page"),
            (test_wallet_page, "Wallet Page"),
            (test_blockchain_page, "Blockchain"),
            (test_ai_monitor, "AI Monitor"),
        ]:
            try:
                results.append((name, test_func(session)))
            except Exception as e:
                print(f"✗ {name} failed: {e}")
                results.append((name, False))
    
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
