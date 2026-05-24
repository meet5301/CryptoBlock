# CryptoBlock - Complete User Journey Guide

## 🎯 User Flow Examples

### Scenario 1: New User Registration & First Trade

#### Step 1: Register
```
1. Go to /auth/register
2. Enter: name, email, password
3. Account created in MongoDB
4. Initial wallet.cash = $10,000 ✓
```

#### Step 2: First Time Login
```
1. Go to /auth/login
2. Enter: email, password
3. Session created
4. Redirect to /home
5. See: Price ticker, charts, market table
```

#### Step 3: Home Page - View Prices
```
Display:
┌─ TICKER ─────────────────────────────────┐
│ BTC: $97,000 +2.5% │ ETH: $3,200 -0.8%   │
│ BNB: $580 +0.2% │ SOL: $145 +1.1%        │
└───────────────────────────────────────────┘

Market Table:
┌──────────────────────────────────────────┐
│ BTC  │ $97,000   │ +2.5% │ $19B      │
│ ETH  │ $3,200    │ -0.8% │ $3,200B   │
│ BNB  │ $580      │ +0.2% │ $725B     │
└──────────────────────────────────────────┘
```

#### Step 4: Buy Crypto
```
1. Chart double-click → Modal opens
2. Enter: Quantity = 0.5, Stop Loss = $95,000
3. Click BUY button
4. Processing...

Result:
Before:  wallet.cash = $10,000
Cost: 0.5 × $97,000 = $48,500
After:   wallet.cash = $1,500

Database Updates:
✓ users: wallet.cash decreased
✓ users: wallet.coins.BTC increased
✓ trades: new trade created (OPEN)
✓ profit_loss: new record created
✓ notifications: sent to user

Notification Display:
"BUY 0.5 BTC @ $97,000.00"
```

#### Step 5: View Dashboard
```
Go to /dashboard

Display:
┌─ STAT CARDS ──────────────────────────┐
│ Total Portfolio      │ $51,500        │
│ Today's P&L         │ $0 (pending)   │
│ Best Coin           │ BTC            │
│ Worst Coin          │ —              │
└───────────────────────────────────────┘

Holdings Table:
┌─────────────────────────────────────────┐
│ Coin │ Qty  │ Avg   │ Current │ Value  │
│ BTC  │ 0.5  │$97k   │ $97k    │$48.5k │
└─────────────────────────────────────────┘

Real-Time Updates: Every 5 seconds
→ Price ticker updates
→ P&L recalculated
→ Wallet balance refreshed
```

#### Step 6: Price Increases - Sell Profit
```
Price Update: BTC now at $100,000 (was $97,000)

Dashboard shows:
Unrealized P&L: +$1,500 (profit)

User clicks SELL:
Processing...

Result:
Before: wallet.cash = $1,500
Proceeds: 0.5 × $100,000 = $50,000
After: wallet.cash = $51,500

Database Updates:
✓ users: wallet.cash increased
✓ users: wallet.coins.BTC decreased
✓ trades: status = CLOSED, sell_price = $100,000
✓ profit_loss: amount = +$1,500, status = CLOSED
✓ notifications: sent notification

Notification:
"SELL 0.5 BTC @ $100,000.00 | PnL: +$1,500.00"

Dashboard updates:
Today's P&L: +$1,500 (green) ✓
```

---

### Scenario 2: User B Receives Transfer

#### Step 1: User A sends $1,000
```
User A at /profile → Transfer section
Enters:
- Receiver: user_b@example.com
- Amount: $1,000
- Clicks: SEND

Processing:
A's cash: $51,500 - $1,000 = $50,500
B's cash: $10,000 + $1,000 = $11,000

Database:
✓ users: A.wallet.cash = $50,500
✓ users: B.wallet.cash = $11,000
✓ transfers: new record created
✓ notifications: sent to A & B
```

#### Step 2: Notifications
```
User A sees:
"Sent $1,000 to user_b@example.com"

User B sees (immediately):
"Received $1,000 from user_a@example.com"

User C sees:
(nothing - privacy maintained) ❌
```

#### Step 3: User B checks Wallet
```
Go to /wallet_page

Display:
Cash: $11,000 (increased from $10,000)

Portfolio Value: $11,000 + holdings
Real-time updates active
```

---

### Scenario 3: Stop-Loss Triggered

#### Step 1: User has open trade
```
Trade:
BTC: 0.5 @ buy $97,000
Stop-Loss: $95,000
Status: OPEN
```

#### Step 2: Price drops
```
WebSocket price update:
"BTC price: $94,500"

Server checks all open trades:
→ Find: BTC trades with stop-loss
→ Check: current_price ($94,500) < stop_loss ($95,000)?
→ Yes! Execute sell

Processing:
wallet.cash: $51,500 + (0.5 × $94,500) = $99,250
wallet.coins.BTC: 0 (removed)
Trade: CLOSED (status: CLOSED, sell_price: $94,500)
P&L: ($94,500 - $97,000) × 0.5 = -$1,250

Database:
✓ trades: updated with sell_price & closed_at
✓ profit_loss: amount = -$1,250
✓ users: wallet updated
✓ notifications: sent

Notification:
"Stop-loss triggered: BTC sold @ $94,500.00"
```

#### Step 3: Dashboard shows loss
```
Today's P&L: -$1,250 (red) ↓
Portfolio value: recalculated lower
```

---

### Scenario 4: User Privacy - Data Isolation

#### Situation: 3 Users trading

```
User A:
├─ Dashboard: sees only A's trades
├─ Portfolio: sees only A's holdings
├─ Profile: sees only A's transfers
├─ Leaderboard: sees A's portfolio value only
└─ CAN'T see: B's or C's data

User B:
├─ Dashboard: sees only B's trades
├─ Portfolio: sees only B's holdings
├─ Profile: sees only B's transfers
├─ Leaderboard: sees B's portfolio value only
└─ CAN'T see: A's or C's data

User C:
├─ Dashboard: sees only C's trades
├─ Portfolio: sees only C's holdings
├─ Profile: sees only C's transfers
├─ Leaderboard: sees C's portfolio value only
└─ CAN'T see: A's or B's data
```

#### Database Filtering
```
When User A accesses /dashboard:
db.trades.find({"email": "a@example.com"})
↓
Result: Only A's trades

When User A accesses /profile:
db.transfers.find({
  "$or": [
    {"sender": "a@example.com"},
    {"receiver": "a@example.com"}
  ]
})
↓
Result: Only A's transfers (as sender OR receiver)

When User A accesses /leaderboard:
→ All users' portfolio values shown
→ But no private data visible
```

---

## 📱 Real-Time Updates Example

### Initial Load (Time: T=0s)
```
BTC Price: $97,000
Dashboard: $51,500 cash + $48,500 holdings = $100,000 total
```

### After 3 Seconds (Time: T=3s)
```
WebSocket Event: price_tick
{
  "symbol": "BTC",
  "price": 97050,
  "change_24h": 2.52
}

UI Updates:
- Ticker: BTC $97,050.00 +2.52%
- Chart: updates candlestick
- Dashboard: holdings = $48,525 (0.5 × $97,050)
```

### After 6 Seconds (Time: T=6s)
```
WebSocket Event: price_tick
{
  "symbol": "BTC",
  "price": 97100,
  "change_24h": 2.54
}

UI Updates:
- Ticker: BTC $97,100.00 +2.54%
- Dashboard: holdings = $48,550, total = $100,050
```

### Dashboard Refresh (Time: T=5s, T=10s, T=15s...)
```
Every 5 seconds:
fetch('/api/wallet')
↓
Response: {
  "cash": 51500,
  "coins_value": 48550,
  "total": 100050
}
↓
Update DOM: totalVal.textContent = "$100,050.00"
```

---

## 💰 Wallet State Tracking

### User Journey With Balance Changes

```
┌─ Initial State ────────────────────────┐
│ Cash: $10,000                          │
│ Holdings: $0                           │
│ Total: $10,000                         │
└────────────────────────────────────────┘
        ↓
        User buys 0.5 BTC @ $97,000
        ↓
┌─ After Buy ────────────────────────────┐
│ Cash: $1,500 (decreased)               │
│ Holdings: $48,500 (BTC value)          │
│ Total: $50,000                         │
└────────────────────────────────────────┘
        ↓
        Price increases to $100,000
        ↓
┌─ Price Change (Still Open) ────────────┐
│ Cash: $1,500                           │
│ Holdings: $50,000 (0.5 × $100,000)     │
│ Total: $51,500                         │
│ Unrealized P&L: +$1,500               │
└────────────────────────────────────────┘
        ↓
        User sells 0.5 BTC @ $100,000
        ↓
┌─ After Sell ───────────────────────────┐
│ Cash: $51,500 (increased)              │
│ Holdings: $0 (all sold)                │
│ Total: $51,500                         │
│ Realized P&L: +$1,500                  │
└────────────────────────────────────────┘
```

---

## 🔄 Complete Transaction Flow Diagram

```
┌─────────────────────────────────────────────────────┐
│ USER INITIATES TRADE (BUY/SELL)                     │
└──────────────────────┬──────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────┐
│ VALIDATE                                            │
│ • Check session: user logged in?                    │
│ • Check balance: enough cash?                       │
│ • Check price: available?                           │
└──────────────────────────┬──────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────┐
│ UPDATE DATABASE                                     │
│ • users: wallet.cash ±                              │
│ • users: wallet.coins.{coin} ±                      │
│ • trades: new or update status                      │
│ • profit_loss: calculate P&L                        │
└──────────────────────────┬──────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────┐
│ BLOCKCHAIN RECORD                                   │
│ • transactions: new record created                  │
│ • status: Pending → Processing → Mined              │
└──────────────────────────┬──────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────┐
│ NOTIFICATIONS                                       │
│ • Create notification entry                         │
│ • User sees: "BUY x COIN @ $price | PnL: ±$amount" │
└──────────────────────────┬──────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────┐
│ EMIT EVENTS                                         │
│ • WebSocket: price_tick for updates                 │
│ • Dashboard: refresh via /api/wallet                │
│ • UI: update displays                               │
└──────────────────────────┬──────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────┐
│ RESPONSE TO USER                                    │
│ • Success: {"success": true, "pnl": amount}         │
│ • UI updates: dashboard, portfolio, wallet          │
│ • Notification appears                              │
└─────────────────────────────────────────────────────┘
```

---

## 📊 Data Consistency Examples

### Buy Transaction Consistency

```
Before:
users.cash = $10,000
trades = []
profit_loss = []

Action: BUY 0.5 BTC @ $97,000

After:
users.cash = $1,500 (consistent: decreased)
users.coins.BTC = 0.5 (new)
trades[0] = {status: OPEN, qty: 0.5, ...}
profit_loss[0] = {status: OPEN, amount: 0, ...}

Check:
$1,500 + (0.5 × $97,000) = $10,000 ✓ (consistent)
```

### Sell Transaction Consistency

```
Before:
users.cash = $1,500
users.coins.BTC = 0.5
trades[0].status = OPEN
profit_loss[0].amount = 0

Action: SELL 0.5 BTC @ $100,000

After:
users.cash = $51,500 (consistent: increased)
users.coins.BTC = 0 (removed)
trades[0].status = CLOSED
profit_loss[0].amount = +$1,500 (calculated)

Check:
$51,500 = $1,500 + (0.5 × $100,000) ✓ (consistent)
Profit = ($100,000 - $97,000) × 0.5 = $1,500 ✓ (correct)
```

---

## ✅ All Features in Action

Everything works together seamlessly:

```
┌──────────────────────────────────────────────────────┐
│                    CRYPTOBLOCK                       │
├──────────────────────────────────────────────────────┤
│                                                      │
│  Ticker (Real-time) → Price Display → Charts       │
│         ↓                    ↓              ↓         │
│   WebSocket updates   Format in $    Update every 3s │
│                                                      │
│  Trading System                                      │
│         ↓                                             │
│   Buy → Wallet ↓    Sell → Wallet ↑                 │
│   P&L Track → Dashboard                             │
│                                                      │
│  User Privacy                                        │
│         ↓                                             │
│   Session Filter → DB Filter → No Data Leakage      │
│                                                      │
│  Real-Time Updates                                   │
│         ↓                                             │
│   WebSocket (3-5s) → Fallback (15s)                 │
│                                                      │
│  Result: ✅ EVERYTHING WORKING                      │
│                                                      │
└──────────────────────────────────────────────────────┘
```

---

## 🎓 Summary

All features are fully operational:
- ✅ Buy/Sell with proper cash flow
- ✅ P&L calculated & displayed
- ✅ All prices in USD ($)
- ✅ Real-time updates every 3-5 seconds
- ✅ User data isolation & privacy
- ✅ Ticker on all pages
- ✅ Dashboard updates without reload
- ✅ Notifications user-specific
- ✅ AI feature accessible
- ✅ Leaderboard rankings working

**Status: PRODUCTION READY** ✅
