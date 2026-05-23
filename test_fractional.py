#!/usr/bin/env python
"""
Test fractional trading - buy/sell/SIP with decimal amounts
"""
import requests
import json

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

def test_fractional_buy(session):
    """Test buying fractional BTC (0.001)"""
    print("\nTesting fractional BUY (0.001 BTC)...")
    trade_data = {
        "coin": "BTC",
        "action": "BUY",
        "qty": 0.001,  # Fractional amount
        "stoploss": 0
    }
    r = session.post(f"{BASE_URL}/api/trade", json=trade_data)
    result = r.json()
    print(f"  Response: {result}")
    if result.get("success"):
        print("  ✓ Fractional BUY successful")
        return True
    else:
        print(f"  ✗ Fractional BUY failed: {result.get('error')}")
        return False

def test_fractional_sell(session):
    """Test selling fractional amount"""
    print("\nTesting fractional SELL...")
    trade_data = {
        "coin": "BTC",
        "action": "SELL"
    }
    r = session.post(f"{BASE_URL}/api/trade", json=trade_data)
    result = r.json()
    print(f"  Response: {result}")
    if result.get("success"):
        print(f"  ✓ Fractional SELL successful, PnL: ₹{result.get('pnl')}")
        return True
    else:
        print(f"  ✗ Fractional SELL failed: {result.get('error')}")
        return False

def test_fractional_sip(session):
    """Test SIP with small amount (will result in fractional units)"""
    print("\nTesting fractional SIP (₹100 for ETH)...")
    sip_data = {
        "coin": "ETH",
        "amount": 100,  # Small amount that will buy fractional ETH
        "months": 1
    }
    r = session.post(f"{BASE_URL}/sip/start", json=sip_data)
    result = r.json()
    print(f"  Response: {result}")
    if result.get("id"):
        print(f"  ✓ Fractional SIP started successfully")
        # Calculate expected units
        eth_price = requests.get(f"{BASE_URL}/api/prices").json().get("ETH", {}).get("inr", 0)
        expected_units = 100 / eth_price if eth_price else 0
        print(f"  Expected units: {expected_units:.6f} ETH")
        return result.get("id")
    else:
        print(f"  ✗ Fractional SIP failed: {result.get('error')}")
        return None

def test_very_small_buy(session):
    """Test buying very small amount (0.0001 BTC)"""
    print("\nTesting very small BUY (0.0001 BTC)...")
    trade_data = {
        "coin": "BTC",
        "action": "BUY",
        "qty": 0.0001,  # Very small fractional amount
        "stoploss": 0
    }
    r = session.post(f"{BASE_URL}/api/trade", json=trade_data)
    result = r.json()
    print(f"  Response: {result}")
    if result.get("success"):
        print("  ✓ Very small BUY successful")
        return True
    else:
        print(f"  ✗ Very small BUY failed: {result.get('error')}")
        return False

def main():
    print("="*50)
    print("FRACTIONAL TRADING TEST")
    print("="*50)
    
    session = get_session()
    if not session:
        print("✗ Failed to login")
        return
    
    results = []
    
    # Test fractional buy
    try:
        results.append(("Fractional BUY (0.001 BTC)", test_fractional_buy(session)))
    except Exception as e:
        print(f"✗ Fractional BUY failed: {e}")
        results.append(("Fractional BUY (0.001 BTC)", False))
    
    # Test fractional sell
    try:
        results.append(("Fractional SELL", test_fractional_sell(session)))
    except Exception as e:
        print(f"✗ Fractional SELL failed: {e}")
        results.append(("Fractional SELL", False))
    
    # Test very small buy
    try:
        results.append(("Very Small BUY (0.0001 BTC)", test_very_small_buy(session)))
    except Exception as e:
        print(f"✗ Very small BUY failed: {e}")
        results.append(("Very Small BUY (0.0001 BTC)", False))
    
    # Test fractional SIP
    try:
        sip_id = test_fractional_sip(session)
        results.append(("Fractional SIP", sip_id is not None))
    except Exception as e:
        print(f"✗ Fractional SIP failed: {e}")
        results.append(("Fractional SIP", False))
    
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
    if passed == total:
        print("\n✓ Fractional trading is FULLY SUPPORTED!")
    print("="*50)

if __name__ == "__main__":
    main()
