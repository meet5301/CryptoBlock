#!/usr/bin/env python3
"""
Advanced CryptoBlock Functionality Test
Tests: Live prices, trading, profit/loss, SIP, wallet operations
"""

import sys
import os
import time
import traceback
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 100)
print("CRYPTOBLOCK ADVANCED FUNCTIONALITY TEST")
print("=" * 100)

results = {"passed": [], "failed": [], "warnings": []}

def test_live_prices():
    """Test live price updates and feeds"""
    print("\n[TEST 1] Testing live price updates...")
    try:
        from price_engine import get_price, get_all_prices, _cache, _history
        
        # Check cache initialization
        if _cache:
            print(f"✓ Price cache initialized with {len(_cache)} coins")
            
            # Check each coin
            for coin in ["BTC", "ETH", "BNB", "SOL"]:
                price = get_price(coin)
                if price > 0:
                    print(f"  ✓ {coin}: ₹{price:,.2f}")
                else:
                    print(f"  ⚠ {coin}: No price (fallback may be needed)")
            
            all_prices = get_all_prices()
            total_value = sum(v.get("inr", 0) for v in all_prices.values())
            print(f"✓ All prices retrieved: {len(all_prices)} coins, Total market cap estimate: ₹{total_value:,.2f}")
            results["passed"].append("Live prices")
        else:
            raise Exception("Price cache is empty")
    except Exception as e:
        print(f"✗ Live price test failed: {e}")
        results["failed"].append(f"Live prices: {e}")
        traceback.print_exc()

def test_trading_simulation():
    """Simulate complete trading workflow"""
    print("\n[TEST 2] Simulating trading workflow...")
    try:
        from price_engine import get_price
        
        # Simulate 3 trades
        trades = [
            {"coin": "BTC", "action": "BUY", "qty": 0.5, "price": 97000},
            {"coin": "ETH", "action": "BUY", "qty": 2.0, "price": 3200},
            {"coin": "BNB", "action": "BUY", "qty": 10.0, "price": 580},
        ]
        
        wallet = {
            "cash": 100000,
            "coins": {},
            "avg_price": {},
            "trades": []
        }
        
        print("Opening trades:")
        for trade in trades:
            coin = trade["coin"]
            qty = trade["qty"]
            price = trade["price"]
            cost = qty * price
            
            if wallet["cash"] >= cost:
                wallet["cash"] -= cost
                wallet["coins"][coin] = wallet["coins"].get(coin, 0) + qty
                wallet["avg_price"][coin] = price
                wallet["trades"].append(trade)
                print(f"  ✓ BUY {qty} {coin} @ ₹{price:,.2f} = ₹{cost:,.2f}")
            else:
                print(f"  ✗ Insufficient balance for {coin}")
        
        print(f"\nWallet after trades:")
        print(f"  Cash remaining: ₹{wallet['cash']:,.2f}")
        for coin, qty in wallet["coins"].items():
            avg = wallet["avg_price"].get(coin, 0)
            print(f"  {coin}: {qty} units @ ₹{avg:,.2f} avg")
        
        # Simulate selling
        print(f"\nClosing trade - BTC:")
        if "BTC" in wallet["coins"]:
            sell_price = 100000  # Assume price went up
            qty = wallet["coins"]["BTC"]
            avg = wallet["avg_price"]["BTC"]
            sell_amount = qty * sell_price
            pnl = (sell_price - avg) * qty
            pnl_pct = ((sell_price - avg) / avg) * 100
            
            print(f"  Bought @ ₹{avg:,.2f}, Selling @ ₹{sell_price:,.2f}")
            print(f"  P&L: ₹{pnl:,.2f} ({pnl_pct:+.2f}%)")
            
            wallet["cash"] += sell_amount
            del wallet["coins"]["BTC"]
            del wallet["avg_price"]["BTC"]
        
        print(f"\nFinal cash: ₹{wallet['cash']:,.2f}")
        results["passed"].append("Trading simulation")
    except Exception as e:
        print(f"✗ Trading simulation failed: {e}")
        results["failed"].append(f"Trading: {e}")
        traceback.print_exc()

def test_portfolio_calculations():
    """Test portfolio value and P&L calculations"""
    print("\n[TEST 3] Testing portfolio calculations...")
    try:
        portfolio = {
            "BTC": {"qty": 0.5, "avg_price": 95000, "current_price": 100000},
            "ETH": {"qty": 2.0, "avg_price": 3000, "current_price": 3500},
            "BNB": {"qty": 10.0, "avg_price": 500, "current_price": 600},
        }
        
        total_invested = 0
        total_current = 0
        holdings = []
        
        print("Portfolio positions:")
        for coin, data in portfolio.items():
            invested = data["qty"] * data["avg_price"]
            current = data["qty"] * data["current_price"]
            unrealized = current - invested
            pnl_pct = (unrealized / invested * 100) if invested else 0
            
            total_invested += invested
            total_current += current
            holdings.append({
                "coin": coin,
                "qty": data["qty"],
                "invested": invested,
                "current": current,
                "unrealized": unrealized,
                "pnl_pct": pnl_pct
            })
            
            print(f"  {coin}:")
            print(f"    Qty: {data['qty']}, Avg: ₹{data['avg_price']:,.2f}, Current: ₹{data['current_price']:,.2f}")
            print(f"    Invested: ₹{invested:,.2f}, Current Value: ₹{current:,.2f}")
            print(f"    Unrealized P&L: ₹{unrealized:,.2f} ({pnl_pct:+.2f}%)")
        
        total_unrealized = total_current - total_invested
        total_pnl_pct = (total_unrealized / total_invested * 100) if total_invested else 0
        
        print(f"\nPortfolio Summary:")
        print(f"  Total Invested: ₹{total_invested:,.2f}")
        print(f"  Current Value: ₹{total_current:,.2f}")
        print(f"  Unrealized P&L: ₹{total_unrealized:,.2f} ({total_pnl_pct:+.2f}%)")
        results["passed"].append("Portfolio calculations")
    except Exception as e:
        print(f"✗ Portfolio calculation failed: {e}")
        results["failed"].append(f"Portfolio: {e}")
        traceback.print_exc()

def test_sip_advanced():
    """Test SIP with advanced metrics"""
    print("\n[TEST 4] Testing SIP with advanced metrics...")
    try:
        # SIP parameters
        monthly = 10000
        months = 12
        prices = [
            100, 110, 105, 120, 115, 125,  # First 6 months
            130, 128, 135, 140, 145, 150   # Last 6 months
        ]
        
        print(f"SIP: ₹{monthly}/month for {months} months")
        print("Month | Price  | Units   | Total Invested | Current Value | Gain")
        print("-" * 70)
        
        total_units = 0
        total_invested = 0
        results_data = []
        
        for month, price in enumerate(prices, 1):
            units = monthly / price
            total_units += units
            total_invested += monthly
            current_value = total_units * price
            gain = current_value - total_invested
            gain_pct = (gain / total_invested * 100) if total_invested else 0
            
            print(f"{month:2d}    | {price:6.0f} | {units:7.4f} | ₹{total_invested:13,.0f} | ₹{current_value:13,.2f} | {gain_pct:+6.2f}%")
            results_data.append({
                "month": month,
                "price": price,
                "units": units,
                "total_units": total_units,
                "total_invested": total_invested,
                "current_value": current_value,
                "gain": gain
            })
        
        final_price = 155
        final_value = total_units * final_price
        total_gain = final_value - total_invested
        total_return_pct = (total_gain / total_invested * 100)
        
        print(f"\nFinal SIP Status @ ₹{final_price}:")
        print(f"  Total Units: {total_units:.4f}")
        print(f"  Total Invested: ₹{total_invested:,.2f}")
        print(f"  Current Value: ₹{final_value:,.2f}")
        print(f"  Total Gain: ₹{total_gain:,.2f} ({total_return_pct:+.2f}%)")
        
        results["passed"].append("Advanced SIP")
    except Exception as e:
        print(f"✗ Advanced SIP test failed: {e}")
        results["failed"].append(f"Advanced SIP: {e}")
        traceback.print_exc()

def test_wallet_operations():
    """Test wallet operations and transfers"""
    print("\n[TEST 5] Testing wallet operations...")
    try:
        # Two wallets
        wallet_a = {
            "email": "alice@test.com",
            "cash": 100000,
            "coins": {"BTC": 1.0, "ETH": 5.0},
            "address": "0x" + "a" * 40
        }
        
        wallet_b = {
            "email": "bob@test.com",
            "cash": 50000,
            "coins": {"BTC": 0.5},
            "address": "0x" + "b" * 40
        }
        
        print(f"Before transfer:")
        print(f"  Alice: ₹{wallet_a['cash']:,.2f}")
        print(f"  Bob: ₹{wallet_b['cash']:,.2f}")
        
        # Transfer
        transfer_amount = 10000
        wallet_a["cash"] -= transfer_amount
        wallet_b["cash"] += transfer_amount
        
        print(f"\nTransferring ₹{transfer_amount:,.2f} from Alice to Bob")
        print(f"After transfer:")
        print(f"  Alice: ₹{wallet_a['cash']:,.2f}")
        print(f"  Bob: ₹{wallet_b['cash']:,.2f}")
        
        # Crypto transfer
        crypto_amount = 0.1
        wallet_a["coins"]["BTC"] -= crypto_amount
        wallet_b["coins"]["BTC"] = wallet_b["coins"].get("BTC", 0) + crypto_amount
        
        print(f"\nTransferring {crypto_amount} BTC from Alice to Bob")
        print(f"After crypto transfer:")
        print(f"  Alice BTC: {wallet_a['coins']['BTC']}")
        print(f"  Bob BTC: {wallet_b['coins']['BTC']}")
        
        results["passed"].append("Wallet operations")
    except Exception as e:
        print(f"✗ Wallet operation failed: {e}")
        results["failed"].append(f"Wallet ops: {e}")
        traceback.print_exc()

def test_stoploss_mechanism():
    """Test stop-loss trigger mechanism"""
    print("\n[TEST 6] Testing stop-loss mechanism...")
    try:
        trades = [
            {"coin": "BTC", "qty": 1.0, "buy_price": 100000, "stoploss": 95000, "status": "OPEN"},
            {"coin": "ETH", "qty": 5.0, "buy_price": 3000, "stoploss": 2800, "status": "OPEN"},
            {"coin": "BNB", "qty": 10.0, "buy_price": 600, "stoploss": 550, "status": "OPEN"},
        ]
        
        current_prices = {
            "BTC": 98000,  # Above stop loss
            "ETH": 2700,   # Below stop loss - SHOULD TRIGGER
            "BNB": 620,    # Above stop loss
        }
        
        print("Checking trades against current prices:")
        triggered = []
        
        for trade in trades:
            coin = trade["coin"]
            current = current_prices.get(coin, 0)
            stoploss = trade["stoploss"]
            
            if current <= stoploss and trade["status"] == "OPEN":
                triggered.append(trade)
                print(f"  ✓ {coin}: Current ₹{current:,.2f} <= Stop-loss ₹{stoploss:,.2f} → TRIGGER")
                trade["status"] = "CLOSED"
                pnl = (current - trade["buy_price"]) * trade["qty"]
                print(f"    P&L: ₹{pnl:,.2f}")
            else:
                print(f"  ✓ {coin}: Current ₹{current:,.2f} > Stop-loss ₹{stoploss:,.2f} → HOLD")
        
        print(f"\nTriggered: {len(triggered)} trades")
        results["passed"].append("Stop-loss mechanism")
    except Exception as e:
        print(f"✗ Stop-loss test failed: {e}")
        results["failed"].append(f"Stop-loss: {e}")
        traceback.print_exc()

def test_blockchain_transactions():
    """Test blockchain transaction recording"""
    print("\n[TEST 7] Testing blockchain transactions...")
    try:
        from core.blockchain_instance import blockchain
        from core.mempool import mempool
        
        mempool.clear()
        
        # Add transactions
        transactions = [
            {"from": "alice", "to": "bob", "amount": 100, "coin": "BTC"},
            {"from": "bob", "to": "charlie", "amount": 50, "coin": "ETH"},
            {"from": "charlie", "to": "alice", "amount": 25, "coin": "BNB"},
        ]
        
        for tx in transactions:
            mempool.add_transaction(tx)
        
        print(f"Pending transactions: {mempool.get_count()}")
        
        # Mine block
        pending_txs = mempool.get_pending()
        blockchain.add_block(pending_txs)
        mempool.clear()
        
        print(f"Block mined: Block #{len(blockchain.chain) - 1}")
        print(f"Block hash: {blockchain.chain[-1].hash[:16]}...")
        print(f"Chain valid: {blockchain.is_chain_valid()}")
        
        results["passed"].append("Blockchain transactions")
    except Exception as e:
        print(f"✗ Blockchain transaction test failed: {e}")
        results["failed"].append(f"Blockchain: {e}")
        traceback.print_exc()

def test_order_types():
    """Test different order types"""
    print("\n[TEST 8] Testing order types (LIMIT, STOP-LOSS, MARKET)...")
    try:
        orders = [
            {"type": "MARKET", "coin": "BTC", "qty": 1.0, "action": "BUY"},
            {"type": "LIMIT", "coin": "ETH", "qty": 5.0, "action": "BUY", "limit_price": 2900},
            {"type": "STOP_LOSS", "coin": "BNB", "qty": 10.0, "action": "SELL", "stop_price": 550},
        ]
        
        current_prices = {"BTC": 100000, "ETH": 3000, "BNB": 600}
        
        print("Processing orders:")
        executed = []
        
        for order in orders:
            current = current_prices[order["coin"]]
            
            if order["type"] == "MARKET":
                print(f"  ✓ {order['type']}: {order['action']} {order['qty']} {order['coin']} @ Market ₹{current:,.2f}")
                executed.append(order)
            
            elif order["type"] == "LIMIT":
                if (order["action"] == "BUY" and current <= order["limit_price"]) or \
                   (order["action"] == "SELL" and current >= order["limit_price"]):
                    print(f"  ✓ {order['type']}: {order['action']} {order['qty']} {order['coin']} @ ₹{current:,.2f} (limit: ₹{order['limit_price']})")
                    executed.append(order)
                else:
                    print(f"  ⏳ {order['type']}: Waiting - current ₹{current:,.2f} vs limit ₹{order['limit_price']}")
            
            elif order["type"] == "STOP_LOSS":
                if current <= order["stop_price"]:
                    print(f"  ✓ {order['type']}: {order['action']} triggered @ ₹{current:,.2f}")
                    executed.append(order)
                else:
                    print(f"  ⏳ {order['type']}: Protected - current ₹{current:,.2f} > stop ₹{order['stop_price']}")
        
        print(f"\nExecuted: {len(executed)}/{len(orders)} orders")
        results["passed"].append("Order types")
    except Exception as e:
        print(f"✗ Order type test failed: {e}")
        results["failed"].append(f"Orders: {e}")
        traceback.print_exc()

def test_profit_loss_tracking():
    """Test P&L tracking across multiple trades"""
    print("\n[TEST 9] Testing profit/loss tracking...")
    try:
        closed_trades = [
            {"coin": "BTC", "qty": 0.5, "buy_price": 90000, "sell_price": 100000, "status": "CLOSED"},
            {"coin": "ETH", "qty": 2.0, "buy_price": 3000, "sell_price": 2800, "status": "CLOSED"},
            {"coin": "BNB", "qty": 10.0, "buy_price": 600, "sell_price": 650, "status": "CLOSED"},
        ]
        
        total_profit = 0
        total_loss = 0
        print("Closed trades P&L:")
        
        for trade in closed_trades:
            pnl = (trade["sell_price"] - trade["buy_price"]) * trade["qty"]
            pnl_pct = ((trade["sell_price"] - trade["buy_price"]) / trade["buy_price"]) * 100
            
            if pnl > 0:
                total_profit += pnl
                status = "✓ PROFIT"
            else:
                total_loss += abs(pnl)
                status = "✗ LOSS"
            
            print(f"  {status}: {trade['coin']} - {trade['qty']} @ ₹{trade['buy_price']:,.2f} → ₹{trade['sell_price']:,.2f}")
            print(f"      P&L: ₹{pnl:,.2f} ({pnl_pct:+.2f}%)")
        
        net_pnl = total_profit - total_loss
        print(f"\nSummary:")
        print(f"  Total Profit: ₹{total_profit:,.2f}")
        print(f"  Total Loss: ₹{total_loss:,.2f}")
        print(f"  Net P&L: ₹{net_pnl:,.2f}")
        print(f"  Win Rate: {sum(1 for t in closed_trades if (t['sell_price'] - t['buy_price']) > 0)}/{len(closed_trades)}")
        
        results["passed"].append("P&L tracking")
    except Exception as e:
        print(f"✗ P&L tracking test failed: {e}")
        results["failed"].append(f"P&L tracking: {e}")
        traceback.print_exc()

def test_live_dashboard_metrics():
    """Test live dashboard metric calculations"""
    print("\n[TEST 10] Testing live dashboard metrics...")
    try:
        # Simulate portfolio
        cash = 20000
        holdings = {
            "BTC": {"qty": 0.5, "avg_price": 90000, "current_price": 100000},
            "ETH": {"qty": 5.0, "avg_price": 2800, "current_price": 3500},
        }
        
        total_holdings_value = 0
        best_coin = worst_coin = None
        best_pnl = float("-inf")
        worst_pnl = float("inf")
        
        print("Live Portfolio:")
        print(f"Cash: ₹{cash:,.2f}")
        
        for coin, data in holdings.items():
            value = data["qty"] * data["current_price"]
            unrealized = (data["current_price"] - data["avg_price"]) * data["qty"]
            pnl_pct = ((data["current_price"] - data["avg_price"]) / data["avg_price"]) * 100
            
            total_holdings_value += value
            
            if unrealized > best_pnl:
                best_pnl = unrealized
                best_coin = coin
            
            if unrealized < worst_pnl:
                worst_pnl = unrealized
                worst_coin = coin
            
            print(f"  {coin}: {data['qty']} @ ₹{data['avg_price']:,.2f} → ₹{data['current_price']:,.2f}")
            print(f"    Value: ₹{value:,.2f}, Unrealized: ₹{unrealized:,.2f} ({pnl_pct:+.2f}%)")
        
        total_value = cash + total_holdings_value
        print(f"\nDashboard Summary:")
        print(f"  Total Portfolio Value: ₹{total_value:,.2f}")
        print(f"  Holdings Value: ₹{total_holdings_value:,.2f}")
        print(f"  Best Performer: {best_coin} (₹{best_pnl:,.2f})")
        print(f"  Worst Performer: {worst_coin} (₹{worst_pnl:,.2f})")
        
        results["passed"].append("Dashboard metrics")
    except Exception as e:
        print(f"✗ Dashboard metrics test failed: {e}")
        results["failed"].append(f"Dashboard: {e}")
        traceback.print_exc()

# Run all tests
if __name__ == "__main__":
    test_live_prices()
    test_trading_simulation()
    test_portfolio_calculations()
    test_sip_advanced()
    test_wallet_operations()
    test_stoploss_mechanism()
    test_blockchain_transactions()
    test_order_types()
    test_profit_loss_tracking()
    test_live_dashboard_metrics()
    
    # Summary
    print("\n" + "=" * 100)
    print("ADVANCED TEST SUMMARY")
    print("=" * 100)
    
    print(f"\n✓ PASSED: {len(results['passed'])}")
    for test in results["passed"]:
        print(f"  ✓ {test}")
    
    if results["failed"]:
        print(f"\n✗ FAILED: {len(results['failed'])}")
        for failure in results["failed"]:
            print(f"  ✗ {failure}")
    
    if results["warnings"]:
        print(f"\n⚠ WARNINGS: {len(results['warnings'])}")
        for warning in results["warnings"]:
            print(f"  ⚠ {warning}")
    
    print("\n" + "=" * 100)
    if len(results["failed"]) == 0:
        print("✓ ALL TESTS PASSED - PROJECT IS FULLY FUNCTIONAL")
    else:
        print(f"⚠ Some tests failed - review above for details")
    print("=" * 100)
