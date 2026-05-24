# CryptoBlock - User Activity & Privacy Features

## ✅ Implemented Features

### 1. **User Wallet Management**

#### Wallet Cash Display
- Wallet balance shows in **$ (US Dollars)**
- Real-time updates when buying/selling crypto
- Displays across all pages: Dashboard, Portfolio, Wallet, Profile

#### Wallet Operations
- **BUY**: Deducts cost from `wallet.cash`
- **SELL**: Adds proceeds to `wallet.cash`
- **TRANSFER**: Deducts from sender's cash, adds to receiver's cash
- All operations tracked in MongoDB with user email

#### Wallet API
```
GET /api/wallet
Response: {
  "cash": 10000.50,
  "coins_value": 5000.00,
  "total": 15000.50,
  "email": "user@email.com"
}
```

---

### 2. **User Activity Isolation**

#### Privacy Controls
✅ Each user sees ONLY their own:
- Trading activity (BUY/SELL trades)
- Transfer history (sent/received)
- Notifications
- Portfolio positions
- SIP plans
- Orders
- Closed trades & P&L history

#### Activity Endpoints (User-Specific)
```
GET /api/user/activity  → Returns only logged-in user's activity
GET /dashboard          → Shows only this user's holdings & trades
GET /portfolio          → Shows only this user's positions
GET /profile            → Shows only this user's transfers & notifications
GET /wallet_page        → Shows only this user's wallet
GET /sip_page           → Shows only this user's SIP plans
```

#### Database Filtering
All queries filter by `email: session["user"]`:
```python
db.trades.find({"email": session["user"]})
db.transfers.find({"sender": email})
db.notifications.find({"user_email": email})
```

**Other users' data is NOT visible** ❌ No access to other profiles, transfers, or trades

---

### 3. **Real-Time Price Updates**

#### Top Ticker Display
✅ Moving price header shows:
- BTC, ETH, BNB, SOL, XRP, DOGE, ADA, TRX, MATIC, LTC, AVAX, LINK
- Current price in **$ (USD)**
- 24h change % (green ↑ / red ↓)
- Updates every 3 seconds via WebSocket
- Works on all pages (Home, Dashboard, Portfolio, etc.)

#### Price Sources
- **CoinGecko API** for live prices
- **Binance API** for OHLC charts
- Both return prices in USD

#### Price Display Format
```
BTC:    $97,000.00    +2.5%  ↑ (green)
ETH:    $3,200.00     -0.8%  ↓ (red)
BNB:    $580.00       +0.2%  ↑
```

---

### 4. **Profit & Loss Tracking**

#### P&L Calculation
When SELL trade closes:
```
P&L = (Sell Price - Buy Price) × Quantity
```

#### P&L Storage
- Stored in `profit_loss` collection
- Records: `amount`, `status`, `trade_id`, `email`
- Displays in Portfolio with green (profit) / red (loss)

#### P&L Display
```
Profit: +$1,500.00  (green)
Loss:   -$500.00    (red)
```

---

### 5. **Crypto Trading**

#### Trade Flow
1. User enters: Quantity, Buy Price (optional), Stop Loss
2. Click BUY → Deducts from wallet.cash
3. Click SELL → Adds proceeds to wallet.cash
4. P&L calculated and stored
5. Notification sent to user

#### Trade Data
Stored fields:
- `email` - User email
- `coin` - Cryptocurrency symbol
- `qty` - Quantity
- `buy_price` - Entry price
- `sell_price` - Exit price (on SELL)
- `status` - OPEN / CLOSED
- `pnl` - Profit/Loss amount
- `created_at` - Trade timestamp

#### Notifications
```
✓ BUY 0.5 BTC @ $97,000.00
✓ SELL 0.5 BTC @ $100,000.00 | PnL: $1,500.00
✓ SELL 1.0 ETH @ $3,200.00 | PnL: -$200.00
```

---

### 6. **Real-Time Dashboard**

#### Dashboard Features
✅ Total Portfolio Value (Cash + Holdings)
✅ Today's P&L
✅ Best/Worst Coin Performance
✅ Holdings Table with Current Prices
✅ Running Trades
✅ Real-time updates every 5 seconds

#### Update Mechanism
- WebSocket price ticks trigger updates
- No full page reload (smooth experience)
- Fallback: Auto-refresh every 15 seconds

```javascript
// Updates wallet display in real-time
fetch('/api/wallet').then(r => r.json()).then(d => {
  // Update total value to: $5,000.00
});
```

---

### 7. **AI Monitoring Feature**

#### AI Access
✅ Available at `/ai/monitor`
✅ Requires login (checks session)
✅ Shows only mined transactions
✅ Detects anomalies using AI/ML

#### AI Features
- Risk scoring for transactions
- Anomaly detection
- Suspicious activity flagging
- Average risk calculation

---

### 8. **Leaderboard (Multi-User)**

#### Leaderboard Display
✅ Shows all users ranked by portfolio value
✅ Each user's data is calculated publicly (for leaderboard)
✅ Does NOT show individual user's transfers or private data
✅ Private activity remains hidden from other users

#### Public Data (in Leaderboard)
- User name / email
- Portfolio value (total)
- Best coin position
- Trade count
- Risk score

#### Private Data (hidden from others)
- Transfer history
- Transaction details
- Notification messages
- Open trades
- Cost basis / average prices

---

### 9. **User Transfers**

#### Transfer Features
✅ Send cash to other users
✅ Receive cash from other users
✅ Each user sees only their own transfers

#### Transfer History
```
Sent:     $1,000 to user@example.com  → Only sender sees this
Received: $500 from trader@mail.com   → Only receiver sees this

(Other users cannot see these transfers)
```

---

### 10. **SIP (Systematic Investment Plan)**

#### SIP Status
✅ User can create SIP plans
✅ Monthly automatic investments
✅ Only user sees their own SIPs
✅ Tracks: invested amount, current value, progress

#### SIP Display
```
BTC — $100/month | 3/12 months executed
ETH — $50/month  | Active
```

---

## Summary Table

| Feature | Status | User-Specific? | Real-Time? |
|---------|--------|---|---|
| Wallet Cash Balance | ✅ | Yes | Yes (5s) |
| Trading (BUY/SELL) | ✅ | Yes | Immediate |
| P&L Tracking | ✅ | Yes | Yes |
| Price Ticker | ✅ | No (Public) | Yes (3s) |
| Dashboard | ✅ | Yes | Yes (5s) |
| Portfolio | ✅ | Yes | Yes |
| Transfers | ✅ | Yes (own only) | Immediate |
| Notifications | ✅ | Yes | Yes |
| AI Monitor | ✅ | Yes (login req) | Yes |
| Leaderboard | ✅ | Mixed | Yes |
| Profile | ✅ | Yes | Immediate |

---

## Security Features

✅ **Session Verification**
- All private routes check `if "user" not in session`
- Redirect to login if not authenticated

✅ **Database Filtering**
- All queries filter by `session["user"]` email
- Other users' data is NOT retrieved

✅ **API Protection**
- `/api/wallet` - requires login
- `/api/user/activity` - requires login
- `/dashboard` - requires login
- `/portfolio` - requires login
- `/profile` - requires login

✅ **No Data Leakage**
- User A cannot see User B's:
  - Wallet balance
  - Trades
  - Transfers
  - Notifications
  - Private holdings

---

## Display Examples

### Wallet Display (User Specific)
```
Cash: $10,000.00
Holdings: $5,000.00
Total: $15,000.00
```

### Trade Notification (User Specific)
```
✓ BUY 0.5 BTC @ $97,000.00
Your cash: $10,000 → $5,150
```

### Price Ticker (Public)
```
BTC: $97,000.00 +2.5%  ETH: $3,200.00 -0.8%  BNB: $580.00 +0.2%
```

### P&L Display
```
Running Trades:
BTC 0.5 @ $95,000 → Current $97,000 | PnL: +$1,000 (green)
ETH 1.0 @ $3,500 → Current $3,200   | PnL: -$300 (red)
```

---

## Testing User Privacy

To verify user isolation works:

1. **Create User A**: Register and make a trade
2. **Create User B**: Register (different email)
3. **Test User A's Dashboard**: See only A's trades ✓
4. **Test User B's Dashboard**: See only B's trades (NOT A's) ✓
5. **Test Leaderboard**: Both users ranked by portfolio value ✓
6. **Test Profile**: Each sees only their own transfers ✓
7. **Test Transfers**: A sends $100 to B
   - A sees in sent history ✓
   - B sees in received history ✓
   - No one else sees it ✓

---

## Real-Time Updates Mechanism

### WebSocket Flow
```
1. Client connects via Socket.IO
2. Client subscribes to price updates
3. Server emits price_tick every 3 seconds
4. Client updates: Ticker, Dashboard, Charts
5. No full page reload needed
```

### Automatic Refresh Fallback
```
If WebSocket fails:
→ Dashboard refreshes every 15 seconds
→ User sees latest data
```

---

## Currency Display

### All Prices in USD ($)
- ✅ Ticker prices
- ✅ Trade prices
- ✅ Portfolio values
- ✅ P&L amounts
- ✅ Wallet balance
- ✅ Chart data
- ✅ Notifications

### Number Formatting
- Locale: `en-US` (1,234.56)
- Symbol: `$`
- Decimal places: 2

---

## Status Summary

✅ **Wallet Management**: Working
✅ **Buy/Sell Trading**: Working
✅ **P&L Tracking**: Working
✅ **Real-Time Prices**: Working
✅ **User Privacy**: Working
✅ **Activity Isolation**: Working
✅ **AI Feature**: Accessible
✅ **Profile Activity**: User-specific
✅ **Price Ticker**: Displaying on all pages
✅ **Currency**: USD ($) everywhere

**All features operational and user-specific data is properly isolated!**
