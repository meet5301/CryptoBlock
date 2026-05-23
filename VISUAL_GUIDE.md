# CryptoBlock - Visual Guide & What to Expect

## 🎬 Home Page Layout

```
┌─────────────────────────────────────────────────────────────────┐
│                         NAVBAR                                   │
│  Logo: CryptoPlus          [Login] [Register] [Dashboard]       │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                         HERO SECTION                             │
│                                                                   │
│  REVOLUTION CRYPTO PLATFORM                                      │
│                                                                   │
│  [Search crypto...] [Search]                                     │
│  [Live Chart] [Explore]                                          │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                      MARKET SECTION                              │
│                                                                   │
│  CoinDesk 20                                                      │
│                                                                   │
│  ┌──────────────────────────────────┐  ┌──────────────────────┐ │
│  │                                  │  │  BTC  ₹97,000 (+2%)  │ │
│  │                                  │  │  ETH  ₹3,200  (-1%)  │ │
│  │      MAIN CHART                  │  │  BNB  ₹580   (+0%)   │ │
│  │   (BTC Candlesticks)             │  │  SOL  ₹145   (+3%)   │ │
│  │                                  │  │  XRP  ₹0.52  (-2%)   │ │
│  │   Green/Red Candles              │  │  ...                 │ │
│  │   Auto-refresh 30s               │  │                      │ │
│  │                                  │  │  LIVE PRICES         │ │
│  │                                  │  │  (Updates every 3s)  │ │
│  └──────────────────────────────────┘  └──────────────────────┘ │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │ #  Name   Price      24h %    Market Cap                    │ │
│  │ 1  BTC    $97,000    +2.5%    $1.9T                         │ │
│  │ 2  ETH    $3,200     -1.2%    $385B                         │ │
│  │ 3  BNB    $580       +0.8%    $88B                          │ │
│  │ ...                                                          │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    MINI CHARTS SECTION                           │
│                                                                   │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐           │
│  │   BTC    │ │   ETH    │ │   BNB    │ │   SOL    │           │
│  │ [Chart]  │ │ [Chart]  │ │ [Chart]  │ │ [Chart]  │           │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘           │
│                                                                   │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐           │
│  │   XRP    │ │  DOGE    │ │   ADA    │ │   TRX    │           │
│  │ [Chart]  │ │ [Chart]  │ │ [Chart]  │ │ [Chart]  │           │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘           │
│                                                                   │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐           │
│  │  MATIC   │ │   LTC    │ │  AVAX    │ │  LINK    │           │
│  │ [Chart]  │ │ [Chart]  │ │ [Chart]  │ │ [Chart]  │           │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘           │
│                                                                   │
│  (Click any chart to open full trading modal)                    │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                   BLOCKCHAIN STATS BAR                           │
│                                                                   │
│  Total Blocks: 42  │  Chain Valid: ✓ YES  │  Pending: 5  │ Risk: 0.0
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

## 📊 Chart Details

### Main Chart (BTC)
```
Title: BTC / USD - Live

Price Scale (Right)
    ↑
    │  ┌─────┐
    │  │ ▲▲▲ │  Green candles = Price up
    │  │ ▼▼▼ │  Red candles = Price down
    │  └─────┘
    │
    └─────────────────→ Time Scale (Bottom)
    
Features:
- 96 candles (15-minute intervals)
- Interactive crosshair
- Zoom & pan support
- Auto-refresh every 30 seconds
```

### Mini Charts
```
Each mini chart shows:
- 96 candles (15-minute intervals)
- Compact 160px height
- Green/red color coding
- Click to expand to full modal
- Auto-refresh every 60 seconds
```

## 🎯 Trading Modal

When you click on any chart:

```
┌─────────────────────────────────────────────────────────────────┐
│  ×                                                               │
│                                                                   │
│  ┌──────────────────────────────┐  ┌──────────────────────────┐ │
│  │                              │  │  BTC / USD               │ │
│  │                              │  │                          │ │
│  │      FULL CHART              │  │  Quantity: [1]           │ │
│  │   (Candlestick)              │  │  Buy at: [97000]         │ │
│  │                              │  │  Stop Loss: [96000]      │ │
│  │   Green/Red Candles          │  │                          │ │
│  │   Larger view                │  │  [BUY]  [SELL]           │ │
│  │                              │  │                          │ │
│  │                              │  │  Today High: $97,500     │ │
│  │                              │  │  Today Low:  $96,800     │ │
│  │                              │  │  ATH: —                  │ │
│  │                              │  │  ATL: —                  │ │
│  │                              │  │                          │ │
│  └──────────────────────────────┘  └──────────────────────────┘ │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

## 🎨 Color Scheme

```
Background:     #0a1f44 (Dark Blue)
Accent:         #facc15 (Yellow)
Up/Profit:      #22c55e (Green)
Down/Loss:      #dc2626 (Red)
Text:           #cbd5f5 (Light Blue)
Grid:           rgba(255,255,255,.07) (Subtle White)
```

## 📈 Real-Time Updates

### Price Sidebar Updates
```
Before:                    After (3 seconds later):
BTC ₹97,000 (+2%)         BTC ₹97,150 (+2.1%)
ETH ₹3,200 (-1%)          ETH ₹3,195 (-1.1%)
BNB ₹580 (+0%)            BNB ₹582 (+0.3%)
```

### Chart Updates
```
Before:                    After (30-60 seconds):
[96 candles]              [96 candles - updated]
Last candle: $97,000      Last candle: $97,150
```

## 🔄 Data Flow Visualization

```
User Opens Home Page
        ↓
    ┌───────────────────────────────────┐
    │ 1. Load Main Chart (BTC)          │
    │    - Fetch 96 candles from API    │
    │    - Render candlestick chart     │
    │    - Auto-refresh every 30s       │
    └───────────────────────────────────┘
        ↓
    ┌───────────────────────────────────┐
    │ 2. Load Mini Charts (12 coins)    │
    │    - Fetch data for each coin     │
    │    - Render 12 mini charts        │
    │    - Auto-refresh every 60s       │
    └───────────────────────────────────┘
        ↓
    ┌───────────────────────────────────┐
    │ 3. Load Market Table              │
    │    - Fetch from CoinGecko API     │
    │    - Display 12 cryptocurrencies  │
    │    - Make rows clickable          │
    └───────────────────────────────────┘
        ↓
    ┌───────────────────────────────────┐
    │ 4. Connect WebSocket              │
    │    - Subscribe to all 12 coins    │
    │    - Receive price updates        │
    │    - Update sidebar every 3s      │
    └───────────────────────────────────┘
        ↓
    Page Ready for Interaction
```

## 🎬 User Interactions

### Scenario 1: View BTC Chart
```
1. User opens home page
2. Sees main BTC chart with candlesticks
3. Chart shows last 96 candles (15-min intervals)
4. Chart auto-refreshes every 30 seconds
5. User can zoom, pan, and hover for details
```

### Scenario 2: View Mini Chart
```
1. User scrolls down to mini charts section
2. Sees 12 small candlestick charts
3. Each chart shows 96 candles
4. User clicks on any mini chart
5. Full trading modal opens with that coin
```

### Scenario 3: Execute Trade
```
1. User clicks on a mini chart
2. Trading modal opens
3. User enters quantity (e.g., 1)
4. User enters stop-loss price (optional)
5. User clicks BUY or SELL
6. Trade executes
7. Success notification appears
```

### Scenario 4: Monitor Prices
```
1. User watches right sidebar
2. Prices update every 3 seconds
3. Colors change based on 24h change
4. Green = up, Red = down
5. User can see real-time market movement
```

## 📱 Responsive Behavior

### Desktop (1920px)
```
┌─────────────────────────────────────────────────────┐
│ Main Chart (75%)        │ Sidebar (25%)             │
│                         │ Live Prices               │
│                         │ (Updates every 3s)        │
└─────────────────────────────────────────────────────┘
```

### Tablet (768px)
```
┌─────────────────────────────────────────────────────┐
│ Main Chart (100%)                                   │
├─────────────────────────────────────────────────────┤
│ Sidebar (100%)                                      │
│ Live Prices (Scrollable)                            │
└─────────────────────────────────────────────────────┘
```

### Mobile (375px)
```
┌─────────────────────────────────────────────────────┐
│ Main Chart (100%)                                   │
├─────────────────────────────────────────────────────┤
│ Sidebar (100%)                                      │
│ Live Prices (Scrollable)                            │
├─────────────────────────────────────────────────────┤
│ Mini Charts (1 column)                              │
└─────────────────────────────────────────────────────┘
```

## ✨ Expected Behavior

### On Page Load
- ✅ Main chart loads with BTC data
- ✅ Mini charts load with 12 coins
- ✅ Market table populates
- ✅ WebSocket connects
- ✅ Prices start updating

### Every 3 Seconds
- ✅ Sidebar prices update
- ✅ Colors change if needed
- ✅ No page refresh

### Every 30 Seconds
- ✅ Main chart refreshes
- ✅ New candles appear
- ✅ Chart auto-fits

### Every 60 Seconds
- ✅ Mini charts refresh
- ✅ New data loaded

### On User Click
- ✅ Mini chart → Full modal opens
- ✅ Market row → Full modal opens
- ✅ Buy/Sell → Trade executes
- ✅ Search → Chart opens

## 🎯 Success Indicators

You'll know everything is working when:

✅ Charts display candlesticks (not blank)
✅ Prices update in real-time (sidebar)
✅ Colors change (green/red)
✅ Can click charts to open modal
✅ Buy/Sell buttons work
✅ No errors in browser console
✅ WebSocket shows "connected" in DevTools

---

**Everything is ready!** 🚀

Open http://localhost:5000 and enjoy!
