# CryptoBlock - Live Crypto Trading Platform

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- MongoDB (running locally)
- Node.js (optional, for frontend development)

### Installation & Running

#### Option 1: Using Batch Script (Windows)
```bash
# Double-click run.bat
# Or from command prompt:
run.bat
```

#### Option 2: Manual Start
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Make sure MongoDB is running
mongod

# 3. Run the app
python app.py

# 4. Open browser
# http://localhost:5000
```

## 📊 Features

### Live Charts
- **Main Chart**: Real-time BTC candlestick chart (15-min intervals)
- **Mini Charts**: 12 crypto coins with live candlestick charts
- **Market Table**: Top cryptocurrencies with prices and 24h changes
- **Big Chart Modal**: Full trading interface with buy/sell buttons

### Real-Time Updates
- WebSocket-based live price updates (every 3 seconds)
- Auto-refreshing charts (30-60 second intervals)
- Live market data from CoinGecko & Binance APIs

### Trading Features
- Buy/Sell orders
- Stop-loss automation
- SIP (Systematic Investment Plan)
- Trade history & P&L tracking
- Wallet management

### Blockchain
- Proof-of-Work mining
- Transaction recording
- Chain validation
- Merkle root calculation

### AI Monitoring
- Anomaly detection
- Risk scoring
- Suspicious transaction flagging

## 🔧 Configuration

### config.py
```python
MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "cryptoplus"
SECRET_KEY = "cryptofusion_secret"
DEBUG = True
MINING_DIFFICULTY = 3
INITIAL_BALANCE = 100000
REDIS_URL = "redis://localhost:6379/0"
```

### Environment Setup
```bash
# Create .env file (optional)
FLASK_ENV=development
FLASK_DEBUG=True
```

## 📁 Project Structure

```
CryptoBlock/
├── app.py                 # Main Flask application
├── config.py             # Configuration settings
├── price_engine.py       # Real-time price fetching
├── run.bat              # Windows startup script
├── requirements.txt     # Python dependencies
│
├── core/                # Blockchain logic
│   ├── blockchain.py
│   ├── block.py
│   ├── transaction.py
│   ├── wallet.py
│   └── order_executor.py
│
├── api/                 # API routes
│   ├── routes/
│   │   ├── auth.py
│   │   ├── wallet.py
│   │   ├── blockchain.py
│   │   ├── orders.py
│   │   └── ...
│   └── middleware/
│
├── database/            # Database models
│   ├── mongo.py
│   ├── models/
│   └── cache/
│
├── ai/                  # AI/ML modules
│   ├── detector.py
│   ├── model.py
│   └── risk_scorer.py
│
├── static/              # Frontend assets
│   ├── css/
│   │   └── home.css
│   └── js/
│       └── home.js
│
└── templates/           # HTML templates
    ├── home.html
    ├── dashboard.html
    ├── portfolio.html
    └── ...
```

## 🌐 API Endpoints

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login user
- `GET /auth/logout` - Logout user

### Trading
- `POST /api/trade` - Execute buy/sell trade
- `GET /api/prices` - Get all crypto prices
- `GET /api/prices/<symbol>` - Get specific coin price

### Wallet
- `GET /wallet/detail` - Get wallet details
- `GET /wallet/history` - Get transaction history

### Blockchain
- `GET /blockchain/chain` - Get blockchain
- `GET /blockchain/stats` - Get blockchain stats

## 🔌 WebSocket Events

### Client → Server
```javascript
socket.emit('subscribe', { symbol: 'BTC' });
```

### Server → Client
```javascript
socket.on('price_tick', (data) => {
  // { symbol, price, change_24h, timestamp }
});
```

## 🐛 Troubleshooting

### Issue: "MongoDB connection refused"
**Solution:**
```bash
# Start MongoDB
mongod

# Or if using MongoDB as service
net start MongoDB
```

### Issue: "Port 5000 already in use"
**Solution:**
```bash
# Kill process on port 5000
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Or change port in app.py
socketio.run(app, port=5001)
```

### Issue: "Charts not loading"
**Solution:**
1. Check browser console for errors (F12)
2. Verify Lightweight Charts library is loaded
3. Check if Binance API is accessible
4. Try clearing browser cache

### Issue: "WebSocket connection failed"
**Solution:**
1. Check if Flask-SocketIO is installed
2. Verify CORS settings in app.py
3. Check firewall settings
4. Try disabling browser extensions

### Issue: "Price updates not working"
**Solution:**
1. Check if price_engine is running
2. Verify CoinGecko API is accessible
3. Check browser console for WebSocket errors
4. Restart the app

## 📊 Database Collections

- `users` - User profiles and wallets
- `trades` - Buy/Sell trades
- `transactions` - Blockchain transactions
- `orders` - Pending/executed orders
- `sip` - SIP records
- `profit_loss` - Trade P&L tracking
- `notifications` - User notifications
- `transfers` - Cash transfers between users

## 🎨 Styling

- **Theme**: Dark blue (#0a1f44)
- **Accent**: Yellow (#facc15)
- **Up**: Green (#22c55e)
- **Down**: Red (#dc2626)

## 📱 Responsive Design

- Desktop: Full layout with all features
- Tablet: Adjusted grid layout
- Mobile: Stacked layout with touch-friendly buttons

## 🔐 Security Features

- Password hashing with Werkzeug
- Session management
- CSRF protection
- Input validation
- SQL injection prevention (using MongoDB)

## 🚀 Performance Optimizations

- Lazy loading of charts
- Efficient database indexing
- WebSocket for real-time updates
- Caching with Redis
- Minified CSS/JS

## 📈 Monitoring

### Blockchain Stats
- Total blocks
- Chain validity
- Pending transactions
- Average risk score

### Trading Stats
- Open trades
- Closed trades
- P&L tracking
- SIP progress

## 🔄 Background Workers

1. **Price Updater** - Fetches prices every 60 seconds
2. **SIP Executor** - Executes SIPs every 60 seconds
3. **Stop-loss Watcher** - Checks stop-loss every 30 seconds
4. **Live Tick Emitter** - Sends price updates every 3 seconds

## 📝 Logs

Logs are printed to console. For file logging, modify app.py:

```python
import logging
logging.basicConfig(filename='app.log', level=logging.INFO)
```

## 🤝 Contributing

1. Create a feature branch
2. Make your changes
3. Test thoroughly
4. Submit a pull request

## 📄 License

MIT License - See LICENSE file for details

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Review browser console errors
3. Check server logs
4. Create an issue on GitHub

## 🎯 Roadmap

- [ ] Mobile app (React Native)
- [ ] Advanced charting tools
- [ ] Technical indicators
- [ ] Price alerts
- [ ] Social trading
- [ ] API for third-party integrations
- [ ] Multi-language support
- [ ] Dark/Light theme toggle

## ✨ Credits

- Lightweight Charts - TradingView
- CoinGecko API - Cryptocurrency data
- Binance API - OHLC data
- Flask - Web framework
- MongoDB - Database

---

**Happy Trading! 🚀**
