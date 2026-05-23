# Live Crypto Charts Setup - Complete Guide

## ✅ What's Been Implemented

### 1. **Main Chart - Live BTC Candlestick Chart**
- **Location:** Home page top section
- **Data Source:** Binance API (15-minute intervals)
- **Auto-Refresh:** Every 30 seconds
- **Features:**
  - Real candlestick visualization
  - Green candles = price up
  - Red candles = price down
  - Interactive crosshair
  - Responsive sizing

### 2. **Mini Charts - 12 Crypto Coins**
- **Coins:** BTC, ETH, BNB, SOL, XRP, DOGE, ADA, TRX, MATIC, LTC, AVAX, LINK
- **Chart Type:** Candlestick charts (15-minute data)
- **Auto-Refresh:** Every 60 seconds
- **Features:**
  - Click to open full chart modal
  - Color-coded (green/red)
  - Compact 160px height

### 3. **Live Price Sidebar**
- **Update Method:** WebSocket (real-time)
- **Refresh Rate:** Every 3 seconds via SocketIO
- **Shows:**
  - Current price in INR
  - 24h change percentage
  - Color indicator (green/red)

### 4. **Market Table**
- **Data Source:** CoinGecko API
- **Shows:** 12 top cryptocurrencies
- **Columns:** Rank, Name, Price, 24h %, Market Cap
- **Clickable:** Click any row to open full chart

### 5. **Big Chart Modal**
- **Trigger:** Click on mini chart or market table row
- **Chart Type:** Candlestick with full trading panel
- **Features:**
  - Buy/Sell buttons
  - Stop-loss input
  - Quantity input
  - Today's High/Low stats

## 🔄 Data Flow

```
Binance API (OHLC Data)
    ↓
Lightweight Charts Library
    ↓
Main Chart + Mini Charts (Updated every 30-60s)

Backend Price Engine (CoinGecko)
    ↓
WebSocket (SocketIO)
    ↓
Live Price Sidebar (Updated every 3s)
```

## 📊 Chart Libraries Used

1. **Lightweight Charts** - Professional candlestick charts
   - Lightweight and fast
   - Dark theme support
   - Responsive
   - No watermarks

2. **Socket.IO** - Real-time WebSocket communication
   - Live price updates
   - Room-based subscriptions
   - Automatic reconnection

## 🚀 How It Works

### Main Chart Loading
```javascript
1. Page loads → initMainChart() called
2. Fetches 96 candles (15m intervals) from Binance
3. Renders candlestick chart
4. Auto-refreshes every 30 seconds
5. Handles window resize
```

### Mini Charts Loading
```javascript
1. For each coin card:
   - Fetch OHLC data from Binance
   - Create candlestick chart
   - Set data and fit content
   - Auto-refresh every 60 seconds
```

### Live Price Updates
```javascript
1. WebSocket connects to backend
2. Subscribe to all 12 coin symbols
3. Receive price_tick events every 3 seconds
4. Update sidebar prices in real-time
```

## 🎨 Styling

- **Dark Theme:** Dark blue background (#0a1f44)
- **Accent Color:** Yellow (#facc15)
- **Up Color:** Green (#22c55e)
- **Down Color:** Red (#dc2626)
- **Grid:** Subtle white lines (7% opacity)

## 📱 Responsive Design

- Main chart: 75% width on desktop
- Side panel: 25% width on desktop
- Mini charts: 4-column grid
- Auto-adjusts on window resize

## ⚡ Performance Optimizations

1. **Lazy Loading:** Charts only load when visible
2. **Efficient Updates:** Only update changed data
3. **CORS Handling:** Proper error handling for API calls
4. **Memory Management:** Remove old chart instances before creating new ones
5. **Debounced Resize:** Resize handler checks if chart exists

## 🔧 Configuration

### Binance API Endpoints
- Main chart: `https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=15m&limit=96`
- Mini charts: `https://api.binance.com/api/v3/klines?symbol={SYMBOL}USDT&interval=15m&limit=96`

### WebSocket Events
- **subscribe:** Subscribe to coin price updates
- **price_tick:** Receive live price data
- **disconnect:** Handle connection loss

## 🐛 Error Handling

- ✅ Null checks for all DOM elements
- ✅ Try-catch blocks for API calls
- ✅ Fallback UI for failed charts
- ✅ Console warnings for debugging
- ✅ Empty array returns instead of crashes

## 📝 Files Modified

1. **home.html** - Added WebSocket script, updated main chart div
2. **home.js** - Complete rewrite with:
   - Live candlestick charts
   - WebSocket integration
   - Error handling
   - Auto-refresh logic
3. **home.css** - Minor positioning updates

## 🎯 Next Steps (Optional)

1. Add more timeframes (1h, 4h, 1d)
2. Add technical indicators (MA, RSI, MACD)
3. Add volume bars to charts
4. Add price alerts
5. Add chart drawing tools
6. Add more coins

## ✨ Features Highlight

✅ Real-time candlestick charts
✅ Live price updates via WebSocket
✅ 12 major cryptocurrencies
✅ Auto-refresh every 30-60 seconds
✅ Responsive design
✅ Dark theme
✅ Error handling
✅ No external dependencies (except Lightweight Charts & Socket.IO)
✅ Professional UI
✅ Mobile friendly

## 🚀 Ready to Use!

Your home page now displays live crypto charts with real-time price updates. Users can:
- View live candlestick charts
- See 24h price changes
- Click charts to open trading modal
- Buy/Sell directly from charts
- Track multiple cryptocurrencies simultaneously
