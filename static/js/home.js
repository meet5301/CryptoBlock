/* ============================================================
   home.js - Live Crypto Trading Platform
   ============================================================ */

console.log('[App] Starting home.js...');

const bigChartModal = document.getElementById("bigChartModal");
const buyBtn = document.getElementById("buyBtn");
const sellBtn = document.getElementById("sellBtn");

const SLUG = {
  BTC: 'bitcoin', ETH: 'ethereum', BNB: 'binancecoin',
  SOL: 'solana', XRP: 'ripple', DOGE: 'dogecoin',
  ADA: 'cardano', TRX: 'tron', MATIC: 'matic-network',
  LTC: 'litecoin', AVAX: 'avalanche-2', LINK: 'chainlink'
};

// Fetch real OHLC data from Binance API
async function fetchBinanceData(symbol, interval = '15m', limit = 500) {
  let sym = symbol.toUpperCase();
  if (sym === 'MATIC') sym = 'POL'; // Binance renamed MATIC to POL
  const url = `https://api.binance.com/api/v3/klines?symbol=${sym}USDT&interval=${interval}&limit=${limit}`;
  try {
    const response = await fetch(url);
    if (!response.ok) return [];
    const data = await response.json();
    const INR_RATE = 83.5;
    return data.map(d => ({
      time: (d[0] / 1000) + (new Date().getTimezoneOffset() * -60), // Adjust to local timezone for lightweight-charts
      open: parseFloat(d[1]) * INR_RATE,
      high: parseFloat(d[2]) * INR_RATE,
      low: parseFloat(d[3]) * INR_RATE,
      close: parseFloat(d[4]) * INR_RATE,
      value: parseFloat(d[4]) * INR_RATE // for line charts
    }));
  } catch (e) {
    console.warn('[API] Binance fetch failed for', sym, e);
    return [];
  }
}

// Load market table
async function loadMarketTable() {
  const ids = Object.values(SLUG).join(',');
  const url = `https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids=${ids}&order=market_cap_desc&per_page=12&sparkline=false`;
  try {
    const r = await fetch(url);
    const list = await r.json();
    const tbody = document.getElementById('marketTableBody');
    if (!tbody) return;
    tbody.innerHTML = list.map((c, i) => `
      <tr onclick="openMarketFromCoin('${c.id}','${c.symbol.toUpperCase()}');" style="cursor:pointer">
        <td>${i + 1}</td>
        <td><b>${c.symbol.toUpperCase()}</b></td>
        <td>$${c.current_price ? c.current_price.toLocaleString() : 'N/A'}</td>
        <td class="${c.price_change_percentage_24h >= 0 ? 'up' : 'down'}">
          ${c.price_change_percentage_24h >= 0 ? '+' : ''}${c.price_change_percentage_24h ? c.price_change_percentage_24h.toFixed(2) : 'N/A'}%
        </td>
        <td>$${c.market_cap ? (c.market_cap / 1e9).toFixed(1) : 'N/A'}B</td>
      </tr>`).join('');
  } catch (e) {
    console.warn('[Market] Error loading table');
  }
}

loadMarketTable();
setInterval(loadMarketTable, 60000);

/* ============================================================
   CHART TOOLBAR GENERATOR
   ============================================================ */
function createToolbar(container, defaultTf, onChange) {
  let existing = container.querySelector('.chart-toolbar');
  if (existing) existing.remove();
  
  const tb = document.createElement('div');
  tb.className = 'chart-toolbar';
  tb.style.cssText = 'display:flex;gap:8px;padding:12px;background:rgba(10,31,68,0.6);border-bottom:1px solid rgba(250,204,21,0.2);flex-wrap:wrap;align-items:center;font-size:12px;z-index:10;position:relative;';
  
  const timeframes = ['1m', '5m', '15m', '1h', '4h', '1d', '1w'];
  timeframes.forEach(tf => {
    const btn = document.createElement('button');
    btn.innerText = tf;
    const isActive = tf === defaultTf;
    btn.style.cssText = `padding:6px 12px;border:1px solid ${isActive ? '#facc15' : 'rgba(250,204,21,0.3)'};background:${isActive ? 'rgba(250,204,21,0.2)' : 'transparent'};color:${isActive ? '#facc15' : '#cbd5f5'};border-radius:4px;cursor:pointer;font-weight:600;transition:all 0.2s`;
    
    btn.onclick = () => {
      Array.from(tb.querySelectorAll('button')).forEach(b => {
        b.style.borderColor = 'rgba(250,204,21,0.3)';
        b.style.background = 'transparent';
        b.style.color = '#cbd5f5';
      });
      btn.style.borderColor = '#facc15';
      btn.style.background = 'rgba(250,204,21,0.2)';
      btn.style.color = '#facc15';
      onChange(tf);
    };
    tb.appendChild(btn);
  });
  
  container.insertBefore(tb, container.firstChild);
}

/* ============================================================
   MAIN CHART (Crypto Index - Custom)
   ============================================================ */
let mainChart = null;
let mainSeries = null;
let mainVolumeSeries = null;
let mainInterval = '1d';
let mainUpdater = null;

function getCustomTimeFormatter(interval) {
  return (time) => {
    let d;
    if (typeof time === 'object' && time !== null) {
      d = new Date(time.year, time.month - 1, time.day);
    } else {
      d = new Date(time * 1000);
    }
    
    if (interval.includes('m')) {
      return d.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: false }) + ' m';
    } else if (interval.includes('h')) {
      return d.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: false }) + ' h';
    } else if (interval.includes('d')) {
      return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }) + ' d';
    } else if (interval.includes('w')) {
      return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }) + ' w';
    }
    return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  };
}

async function fetchIndexData(interval) {
  const btc = await fetchBinanceData('BTC', interval, 500);
  const eth = await fetchBinanceData('ETH', interval, 500);
  if (!btc.length) return [];
  return btc.map((b, i) => {
    const e = eth[i] || b;
    return {
      time: b.time,
      open: (b.open + e.open) / 2,
      high: (b.high + e.high) / 2,
      low: (b.low + e.low) / 2,
      close: (b.close + e.close) / 2,
      value: (b.value + e.value) / 2
    };
  });
}

async function loadMainChartData() {
  const data = await fetchIndexData(mainInterval);
  if (data.length > 0) {
    mainSeries.setData(data);
    mainVolumeSeries.setData(data.map(d => ({
      time: d.time,
      value: Math.random() * 1000, 
      color: d.close >= d.open ? 'rgba(34, 197, 94, 0.5)' : 'rgba(239, 68, 68, 0.5)'
    })));
    mainChart.timeScale().fitContent();
  }
}

async function initMainChart() {
  const container = document.querySelector('.main-chart-container');
  const el = document.getElementById('mainChartDiv');
  if (!el || !container) return;
  
  el.innerHTML = '';
  
  createToolbar(container, mainInterval, async (tf) => {
    mainInterval = tf;
    mainChart.applyOptions({
      timeScale: { tickMarkFormatter: getCustomTimeFormatter(mainInterval) }
    });
    await loadMainChartData();
  });

  mainChart = LightweightCharts.createChart(el, {
    layout: { background: { type: 'solid', color: 'transparent' }, textColor: '#cbd5f5' },
    grid: { vertLines: { color: 'rgba(255,255,255,0.05)' }, horzLines: { color: 'rgba(255,255,255,0.05)' } },
    crosshair: { mode: LightweightCharts.CrosshairMode.Normal },
    leftPriceScale: { visible: true, borderColor: 'rgba(255,255,255,0.1)' },
    rightPriceScale: { visible: false },
    timeScale: { 
      visible: true,
      borderColor: 'rgba(255,255,255,0.1)', 
      timeVisible: true,
      tickMarkFormatter: getCustomTimeFormatter(mainInterval)
    }
  });
  
  mainSeries = mainChart.addCandlestickSeries({
    upColor: '#22c55e', downColor: '#dc2626', borderVisible: false,
    wickUpColor: '#22c55e', wickDownColor: '#dc2626'
  });
  
  mainVolumeSeries = mainChart.addHistogramSeries({
    priceFormat: { type: 'volume' },
    priceScaleId: '', 
    scaleMargins: { top: 0.8, bottom: 0 }
  });

  new ResizeObserver(entries => {
    if (entries.length === 0 || entries[0].target !== el) return;
    const newRect = entries[0].contentRect;
    mainChart.applyOptions({ width: newRect.width, height: newRect.height });
  }).observe(el);

  await loadMainChartData();

  if (mainUpdater) clearInterval(mainUpdater);
  mainUpdater = setInterval(async () => {
    await loadMainChartData();
  }, 60000);
}

/* ============================================================
   MINI CHARTS
   ============================================================ */
const miniCharts = {};
let miniUpdater = null;

async function initMiniCharts() {
  const elements = document.querySelectorAll('.mini-chart-div');
  console.log('[Mini Charts] Found', elements.length, 'containers');
  
  for (const el of elements) {
    const sym = el.dataset.sym;
    if (!sym) continue;

    el.innerHTML = ''; // clear

    const mChart = LightweightCharts.createChart(el, {
      layout: { background: { type: 'solid', color: 'transparent' }, textColor: '#cbd5f5', fontSize: 9 },
      grid: { vertLines: { visible: false }, horzLines: { visible: false } },
      leftPriceScale: { visible: true, borderColor: 'rgba(255,255,255,0.1)' },
      rightPriceScale: { visible: false },
      timeScale: { 
        visible: true, 
        borderColor: 'rgba(255,255,255,0.1)',
        timeVisible: true,
        tickMarkFormatter: getCustomTimeFormatter('1d')
      },
      crosshair: { mode: LightweightCharts.CrosshairMode.Normal },
      handleScroll: false,
      handleScale: false,
    });
    const mSeries = mChart.addCandlestickSeries({
      upColor: '#22c55e', downColor: '#dc2626', borderVisible: false,
      wickUpColor: '#22c55e', wickDownColor: '#dc2626'
    });

    miniCharts[sym] = { chart: mChart, series: mSeries };

    new ResizeObserver(entries => {
      if (entries.length === 0 || entries[0].target !== el) return;
      const newRect = entries[0].contentRect;
      mChart.applyOptions({ width: newRect.width, height: newRect.height });
    }).observe(el);

    try {
      const data = await fetchBinanceData(sym, '1d', 730); // 2 years of daily candles
      if (data.length > 0) {
        mSeries.setData(data);
        mChart.timeScale().fitContent();
      }
    } catch (e) {}
  }

  if (miniUpdater) clearInterval(miniUpdater);
  miniUpdater = setInterval(async () => {
    for (const el of elements) {
      const sym = el.dataset.sym;
      if (!sym || !miniCharts[sym]) continue;
      try {
        const data = await fetchBinanceData(sym, '1h', 2);
        if (data.length > 0) {
          miniCharts[sym].series.update(data[data.length - 1]);
        }
      } catch (e) {}
    }
  }, 30000); // 30s update for sparklines
}

/* ============================================================
   BIG POPUP CHART
   ============================================================ */
let bigChart = null;
let bigSeries = null;
let bigVolumeSeries = null;
let bigCoinId = 'bitcoin', bigCurrentPrice = 0, bigSym = 'BTC';
let bigInterval = '1d';
let bigUpdater = null;

async function loadBigChartData() {
  const data = await fetchBinanceData(bigSym, bigInterval, 730); // Default to 2 years
  if (data.length > 0) {
    bigSeries.setData(data);
    bigVolumeSeries.setData(data.map(d => ({
      time: d.time, value: d.volume || Math.random() * 100,
      color: d.close >= d.open ? 'rgba(34, 197, 94, 0.5)' : 'rgba(239, 68, 68, 0.5)'
    })));
    bigCurrentPrice = data[data.length - 1].close;
    
    const hi = Math.max(...data.map(c => c.high));
    const lo = Math.min(...data.map(c => c.low));
    const highEl = document.getElementById('todayHigh');
    const lowEl = document.getElementById('todayLow');
    if (highEl) highEl.innerText = '$' + hi.toFixed(2);
    if (lowEl) lowEl.innerText = '$' + lo.toFixed(2);
    
    bigChart.timeScale().fitContent();
  }
}

async function loadBigChart(coinId, sym) {
  bigCoinId = coinId;
  bigSym = sym;
  const titleEl = document.getElementById('bigCoinTitle');
  if (titleEl) titleEl.innerText = sym + ' / USD';

  const el = document.getElementById('bigChartDiv');
  const container = el.parentElement;
  if (!el || !container) return;
  
  el.innerHTML = '';
  
  createToolbar(container, bigInterval, async (tf) => {
    bigInterval = tf;
    bigChart.applyOptions({
      timeScale: { tickMarkFormatter: getCustomTimeFormatter(bigInterval) }
    });
    await loadBigChartData();
  });

  bigChart = LightweightCharts.createChart(el, {
    layout: { background: { type: 'solid', color: 'transparent' }, textColor: '#cbd5f5' },
    grid: { vertLines: { color: 'rgba(255,255,255,0.05)' }, horzLines: { color: 'rgba(255,255,255,0.05)' } },
    crosshair: { mode: LightweightCharts.CrosshairMode.Normal },
    leftPriceScale: { visible: true, borderColor: 'rgba(255,255,255,0.1)' },
    rightPriceScale: { visible: false },
    timeScale: { 
      visible: true,
      borderColor: 'rgba(255,255,255,0.1)', 
      timeVisible: true,
      tickMarkFormatter: getCustomTimeFormatter(bigInterval)
    }
  });
  
  bigSeries = bigChart.addCandlestickSeries({
    upColor: '#22c55e', downColor: '#dc2626', borderVisible: false,
    wickUpColor: '#22c55e', wickDownColor: '#dc2626'
  });

  bigVolumeSeries = bigChart.addHistogramSeries({
    priceFormat: { type: 'volume' },
    priceScaleId: '',
    scaleMargins: { top: 0.8, bottom: 0 }
  });

  new ResizeObserver(entries => {
    if (entries.length === 0 || entries[0].target !== el) return;
    const newRect = entries[0].contentRect;
    bigChart.applyOptions({ width: newRect.width, height: newRect.height });
  }).observe(el);
  
  await loadBigChartData();

  if (bigUpdater) clearInterval(bigUpdater);
  bigUpdater = setInterval(async () => {
    if (bigChartModal && bigChartModal.classList.contains('active') && bigSym) {
      const data = await fetchBinanceData(bigSym, bigInterval, 2);
      if (data.length > 0 && bigSeries) {
        const d = data[data.length - 1];
        bigSeries.update(d);
        bigVolumeSeries.update({
          time: d.time, value: d.volume || Math.random() * 100,
          color: d.close >= d.open ? 'rgba(34, 197, 94, 0.5)' : 'rgba(239, 68, 68, 0.5)'
        });
        bigCurrentPrice = d.close;
      }
    }
  }, 5000);
}

/* ============================================================
   MODAL FUNCTIONS
   ============================================================ */
function openMarketFromCoin(coinId, sym) {
  if (bigChartModal) {
    bigChartModal.style.display = 'flex';
    bigChartModal.classList.add('active');
  }
  loadBigChart(coinId, sym);
}

function closeBigChart() {
  if (bigChartModal) {
    bigChartModal.style.display = 'none';
    bigChartModal.classList.remove('active');
  }
}

// Add click on main chart to open Big Chart modal
const mainChartDivEl = document.getElementById('mainChartDiv');
if (mainChartDivEl) {
  mainChartDivEl.addEventListener('dblclick', () => openMarketFromCoin('bitcoin', 'BTC'));
}

/* ============================================================
   TRADE FUNCTIONS
   ============================================================ */
function showTradePopup(type, price) {
  const box = document.createElement('div');
  const isBuy = type === 'BUY';
  box.innerHTML = `<div style="
    position:fixed;top:30px;right:30px;padding:16px 26px;
    border-radius:14px;font-weight:900;z-index:99999;
    background:${isBuy ? 'rgba(34,197,94,.25)' : 'rgba(239,68,68,.25)'};
    border:1px solid ${isBuy ? 'rgba(34,197,94,.6)' : 'rgba(239,68,68,.6)'};
    color:${isBuy ? '#bbf7d0' : '#fecaca'};
    backdrop-filter:blur(14px);">
    ${type} executed @ $${price.toFixed(2)}
  </div>`;
  document.body.appendChild(box);
  setTimeout(() => box.remove(), 3000);
}

function trade(action) {
  const qtyEl = document.getElementById('qtyInput');
  const slEl = document.getElementById('slInput');
  if (!qtyEl || !slEl) {
    alert('Trade inputs not found');
    return;
  }
  const price = Number(bigCurrentPrice.toFixed(4));
  fetch('/api/trade', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      coin: bigSym,
      price: price,
      qty: Number(qtyEl.value) || 1,
      stoploss: Number(slEl.value) || 0,
      action: action
    })
  })
  .then(r => r.json())
  .then(d => {
    if (d.error) {
      alert('Error: ' + d.error);
    } else {
      showTradePopup(action, price);
      qtyEl.value = '1';
      slEl.value = '';
    }
  })
  .catch(e => {
    console.warn('[Trade] Error:', e);
    showTradePopup(action, price);
  });
}

if (buyBtn) buyBtn.addEventListener('click', () => trade('BUY'));
if (sellBtn) sellBtn.addEventListener('click', () => trade('SELL'));

/* ============================================================
   SEARCH
   ============================================================ */
function searchCrypto() {
  const searchEl = document.getElementById('searchInput');
  if (!searchEl) return;
  const q = searchEl.value.trim().toUpperCase();
  const coinId = SLUG[q];
  if (coinId) {
    openMarketFromCoin(coinId, q);
    searchEl.value = '';
  } else {
    alert('Coin not found. Try: BTC, ETH, BNB, SOL, XRP, DOGE, ADA, TRX, MATIC, LTC, AVAX, LINK');
  }
}

const searchInput = document.getElementById('searchInput');
if (searchInput) {
  searchInput.addEventListener('keydown', e => {
    if (e.key === 'Enter') searchCrypto();
  });
}

function goMarket() {
  const marketEl = document.getElementById('market');
  if (marketEl) {
    marketEl.scrollIntoView({ behavior: 'smooth' });
  }
}

/* ============================================================
   WEBSOCKET - LIVE PRICES (UI Table/Ticker updates)
   ============================================================ */
try {
  const socket = io();

  socket.on('connect', () => {
    console.log('[WebSocket] Connected');
    const symbols = ['BTC', 'ETH', 'BNB', 'SOL', 'XRP', 'DOGE', 'ADA', 'TRX', 'MATIC', 'LTC', 'AVAX', 'LINK'];
    symbols.forEach(sym => {
      socket.emit('subscribe', { symbol: sym });
    });
  });

  socket.on('price_tick', (data) => {
    const { symbol, price, change_24h } = data;
    const chg = change_24h || 0;
    const cls = chg >= 0 ? 'chg-up' : 'chg-dn';
    const sign = chg >= 0 ? '+' : '';
    
    ['tp-','tp2-'].forEach(p => {
      const el = document.getElementById(p + symbol);
      if (el) el.textContent = '₹' + price.toLocaleString('en-IN');
    });
    
    ['tc-','tc2-'].forEach(p => {
      const el = document.getElementById(p + symbol);
      if (el) { 
        el.textContent = sign + chg.toFixed(2) + '%'; 
        el.className = 'chg ' + cls; 
      }
    });
  });

  socket.on('error', (err) => {
    console.warn('[WebSocket] Error:', err);
  });
} catch (e) {
  console.warn('[WebSocket] Setup error:', e);
}

/* ============================================================
   INITIALIZATION
   ============================================================ */
console.log('[App] Initializing charts...');

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    initMainChart();
    initMiniCharts();
  });
} else {
  initMainChart();
  initMiniCharts();
}
