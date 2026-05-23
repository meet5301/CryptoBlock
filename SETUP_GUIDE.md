# CryptoBlock - Complete Setup & Run Guide

## ✅ Pre-Requisites Check

### 1. Python Installation
```bash
python --version
# Should show Python 3.8 or higher
```

### 2. MongoDB Status
```bash
# Check if MongoDB is running
tasklist | findstr mongod

# If not running, start it:
mongod
```

### 3. Dependencies
```bash
# Install all required packages
pip install -r requirements.txt
```

## 🚀 Running the Application

### Method 1: Using Batch Script (Recommended for Windows)
```bash
# Simply double-click: run.bat
# Or from command prompt:
cd c:\Users\Meet\OneDrive\Desktop\CryptoBlock
run.bat
```

### Method 2: Manual Start
```bash
# Step 1: Navigate to project directory
cd c:\Users\Meet\OneDrive\Desktop\CryptoBlock

# Step 2: Start the app
python app.py

# Step 3: Open browser
# http://localhost:5000
```

### Method 3: Using Python IDE
1. Open `app.py` in your IDE (VS Code, PyCharm, etc.)
2. Click "Run" button
3. Open http://localhost:5000 in browser

## 📊 What You'll See

### Home Page Features
✅ **Main Chart** - Live BTC candlestick chart
✅ **Mini Charts** - 12 crypto coins with live charts
✅ **Market Table** - Top cryptocurrencies
✅ **Live Prices** - Real-time price updates
✅ **Blockchain Stats** - Total blocks, chain validity, pending txns

### Interactive Features
- Click on any mini chart to open full trading modal
- Click on market table rows to view detailed charts
- Use search bar to find specific coins
- Buy/Sell buttons in the trading modal
- Set stop-loss prices

## 🔧 Configuration

### Default Settings (config.py)
```python
MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "cryptoplus"
SECRET_KEY = "cryptofusion_secret"
DEBUG = True
INITIAL_BALANCE = 100000
```

### Change Port (if needed)
Edit `app.py` last line:
```python
socketio.run(app, debug=True, port=5001)  # Change 5001 to your port
```

## 📈 Testing the Charts

### 1. Verify Main Chart Loads
- Go to http://localhost:5000/home
- You should see a candlestick chart at the top
- Chart should show BTC data with green/red candles

### 2. Verify Mini Charts Load
- Scroll down to see 12 mini charts
- Each should show a small candlestick chart
- Click any mini chart to open full view

### 3. Verify Live Prices Update
- Look at the right sidebar with prices
- Prices should update every 3 seconds
- Color should change (green/red) based on 24h change

### 4. Verify Market Table
- Scroll down to see market table
- Should show 12 cryptocurrencies
- Click any row to open trading modal

## 🎯 First Time Setup Checklist

- [ ] Python 3.8+ installed
- [ ] MongoDB running
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] No errors in test_startup.py
- [ ] App starts without errors
- [ ] Home page loads in browser
- [ ] Charts are visible
- [ ] Prices are updating
- [ ] Can click on charts to open modal

## 🐛 Common Issues & Solutions

### Issue 1: "ModuleNotFoundError: No module named 'flask'"
```bash
# Solution: Install dependencies
pip install -r requirements.txt
```

### Issue 2: "Connection refused" (MongoDB)
```bash
# Solution: Start MongoDB
mongod
# Or if installed as service:
net start MongoDB
```

### Issue 3: "Address already in use"
```bash
# Solution: Kill process on port 5000
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

### Issue 4: Charts not showing
```
Solution:
1. Open browser DevTools (F12)
2. Check Console tab for errors
3. Check Network tab for failed requests
4. Clear browser cache (Ctrl+Shift+Delete)
5. Restart the app
```

### Issue 5: Prices not updating
```
Solution:
1. Check if WebSocket is connected (DevTools → Network → WS)
2. Check if price_engine is running
3. Verify CoinGecko API is accessible
4. Restart the app
```

## 📊 Data Sources

### Live Charts
- **Source**: Binance API
- **Interval**: 15 minutes
- **Update**: Every 30-60 seconds

### Live Prices
- **Source**: CoinGecko API
- **Update**: Every 3 seconds via WebSocket

### Market Data
- **Source**: CoinGecko API
- **Update**: On page load

## 🔌 WebSocket Connection

The app uses WebSocket for real-time price updates:
- **Connection**: Automatic on page load
- **Subscription**: Auto-subscribes to all 12 coins
- **Update Rate**: Every 3 seconds
- **Fallback**: If WebSocket fails, uses polling

## 📱 Browser Compatibility

✅ Chrome/Chromium (Recommended)
✅ Firefox
✅ Safari
✅ Edge
⚠️ IE11 (Not supported)

## 🎨 Customization

### Change Theme Colors
Edit `static/css/home.css`:
```css
body { background: #0a1f44; }  /* Main background */
.btn-yellow { background: #facc15; }  /* Accent color */
.up { color: #22c55e; }  /* Up color */
.down { color: #dc2626; }  /* Down color */
```

### Add More Coins
Edit `app.py` COINS dictionary:
```python
COINS = {
    "BTC": {"name": "Bitcoin", "coingecko_id": "bitcoin"},
    # Add more coins here
}
```

## 🚀 Performance Tips

1. **Use Chrome** - Best performance
2. **Close unused tabs** - Reduces memory usage
3. **Disable extensions** - Can interfere with WebSocket
4. **Clear cache regularly** - Improves loading speed
5. **Use wired connection** - Better than WiFi for real-time updates

## 📝 Logs & Debugging

### View Console Logs
```bash
# Terminal will show:
[PriceEngine] Updated 12 prices
[INFO] User logged in: user@example.com
[WARNING] API rate limit approaching
```

### Enable Debug Mode
Edit `app.py`:
```python
app = Flask(__name__)
app.debug = True  # Enable debug mode
```

## 🔐 Security Notes

1. **Change SECRET_KEY** in production
2. **Use HTTPS** in production
3. **Enable authentication** for all routes
4. **Validate all inputs** on backend
5. **Use environment variables** for sensitive data

## 📞 Getting Help

1. **Check README.md** - General information
2. **Check LIVE_CHARTS_SETUP.md** - Chart-specific setup
3. **Check ERROR_FIXES.md** - Common errors and fixes
4. **Check browser console** - JavaScript errors
5. **Check server logs** - Backend errors

## ✨ Next Steps

After successful setup:
1. Create a user account (Register)
2. Login to your account
3. Explore the dashboard
4. Try buying/selling crypto
5. Check your portfolio
6. Set up SIP investments

## 🎉 You're All Set!

Your CryptoBlock application is now ready to use!

**Access the app at: http://localhost:5000**

Enjoy trading! 🚀

---

**Need help?** Check the troubleshooting section or review the error logs.
