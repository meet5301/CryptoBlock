#!/usr/bin/env python
"""
Test trading and SIP functionality with live prices
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

def test_buy_trade(session):
    """Test buying a coin"""
    print("\nTesting BUY trade...")
    trade_data = {
        "coin": "BTC",
        "action": "BUY",
        "qty": 0.0001,
        "stoploss": 0
    }
    r = session.post(f"{BASE_URL}/api/trade", json=trade_data)
    result = r.json()
    print(f"  Response: {result}")
    if result.get("success"):
        print("  ✓ BUY successful")
        return True
    else:
        print(f"  ✗ BUY failed: {result.get('error')}")
        return False

def test_sell_trade(session):
    """Test selling a coin"""
    print("\nTesting SELL trade...")
    trade_data = {
        "coin": "BTC",
        "action": "SELL"
    }
    r = session.post(f"{BASE_URL}/api/trade", json=trade_data)
    result = r.json()
    print(f"  Response: {result}")
    if result.get("success"):
        print(f"  ✓ SELL successful, PnL: ₹{result.get('pnl')}")
        return True
    else:
        print(f"  ✗ SELL failed: {result.get('error')}")
        return False

def test_wallet_balance(session):
    """Test wallet balance"""
    print("\nTesting wallet balance...")
    r = session.get(f"{BASE_URL}/api/wallet")
    result = r.json()
    print(f"  Cash balance: ₹{result.get('cash')}")
    return result.get("cash") is not None

def test_start_sip(session):
    """Test starting a SIP"""
    print("\nTesting SIP start...")
    sip_data = {
        "coin": "ETH",
        "amount": 100,
        "months": 3
    }
    r = session.post(f"{BASE_URL}/sip/start", json=sip_data)
    result = r.json()
    print(f"  Response: {result}")
    if result.get("id"):
        print(f"  ✓ SIP started successfully, ID: {result.get('id')}")
        return result.get("id")
    else:
        print(f"  ✗ SIP start failed: {result.get('error')}")
        return None

def test_close_sip(session, sip_id):
    """Test closing a SIP"""
    print("\nTesting SIP close...")
    if not sip_id:
        print("  No SIP ID to close")
        return False
    r = session.post(f"{BASE_URL}/sip/close/{sip_id}")
    result = r.json()
    print(f"  Response: {result}")
    if result.get("wallet_cash"):
        print(f"  ✓ SIP closed successfully, wallet cash: ₹{result.get('wallet_cash')}")
        return True
    else:
        print(f"  ✗ SIP close failed: {result.get('error')}")
        return False

def test_blockchain_mining(session):
    """Test blockchain mining"""
    print("\nTesting blockchain mining...")
    r = session.get(f"{BASE_URL}/blockchain/mine")
    print(f"  Mining status: {r.status_code}")
    if r.status_code == 200:
        print("  ✓ Mining page accessible")
        return True
    return False

def main():
    print("="*50)
    print("CRYPTOBLOCK TRADING & SIP TEST")
    print("="*50)
    
    session = get_session()
    if not session:
        print("✗ Failed to login")
        return
    
    results = []
    
    # Test wallet balance
    try:
        results.append(("Wallet Balance", test_wallet_balance(session)))
    except Exception as e:
        print(f"✗ Wallet balance failed: {e}")
        results.append(("Wallet Balance", False))
    
    # Test buy trade
    try:
        results.append(("BUY Trade", test_buy_trade(session)))
    except Exception as e:
        print(f"✗ BUY trade failed: {e}")
        results.append(("BUY Trade", False))
    
    # Test sell trade
    try:
        results.append(("SELL Trade", test_sell_trade(session)))
    except Exception as e:
        print(f"✗ SELL trade failed: {e}")
        results.append(("SELL Trade", False))
    
    # Test SIP start
    try:
        sip_id = test_start_sip(session)
        results.append(("SIP Start", sip_id is not None))
    except Exception as e:
        print(f"✗ SIP start failed: {e}")
        results.append(("SIP Start", False))
        sip_id = None
    
    # Test SIP close
    try:
        results.append(("SIP Close", test_close_sip(session, sip_id)))
    except Exception as e:
        print(f"✗ SIP close failed: {e}")
        results.append(("SIP Close", False))
    
    # Test blockchain mining
    try:
        results.append(("Blockchain Mining", test_blockchain_mining(session)))
    except Exception as e:
        print(f"✗ Blockchain mining failed: {e}")
        results.append(("Blockchain Mining", False))
    
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
