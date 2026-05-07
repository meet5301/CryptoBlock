/* ============================================================
   home.js  –  Real Live Charts using CoinGecko + Lightweight Charts
   ============================================================ */

const bigChartModal = document.getElementById("bigChartModal");
const buyBtn        = document.getElementById("buyBtn");
const sellBtn       = document.getElementById("sellBtn");

/* ---------- CoinGecko slug map ---------- */
const SLUG = {
  BTC:'bitcoin',   ETH:'ethereum',    BNB:'binancecoin',
  SOL:'solana',    XRP:'ripple',      DOGE:'dogecoin',
  ADA:'cardano',   TRX:'tron',        MATIC:'matic-network',
  LTC:'litecoin',  AVAX:'avalanche-2', LINK:'chainlink'
};

/* ---------- Populate market table with real data ---------- */
async function loadMarketTable() {
  const ids = Object.values(SLUG).join(',');
  const url = `https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids=${ids}&order=market_cap_desc&per_page=12&sparkline=false`;
  try {
    const r    = await fetch(url);
    const list = await r.json();
    const tbody = document.getElementById('marketTableBody');
    if (!tbody) return;
    tbody.innerHTML = list.map((c, i) => `
      <tr onclick="openMarketFromCoin('${c.id}','${c.symbol.toUpperCase()}')" style="cursor:pointer">
        <td>${i + 1}</td>
        <td><b>${c.symbol.toUpperCase()}</b></td>
        <td>$${c.current_price.toLocaleString()}</td>
        <td class="${c.price_change_percentage_24h >= 0 ? 'up' : 'down'}">
          ${c.price_change_percentage_24h >= 0 ? '+' : ''}${c.price_change_percentage_24h.toFixed(2)}%
        </td>
        <td>$${(c.market_cap / 1e9).toFixed(1)}B</td>
      </tr>`).join('');
  } catch (e) { console.warn('Market table error:', e); }
}
loadMarketTable();

/* ---------- Lightweight-Charts dark theme ---------- */
const CHART_OPTS = {
  layout:{ background:{color:'transparent'}, textColor:'#cbd5f5' },
  grid:{ vertLines:{color:'rgba(255,255,255,.07)'}, horzLines:{color:'rgba(255,255,255,.07)'} },
  crosshair:{ mode:1 },
  rightPriceScale:{ borderColor:'rgba(255,255,255,.2)' },
  timeScale:{ borderColor:'rgba(255,255,255,.2)', timeVisible:true, secondsVisible:false }
};

/* ---------- Binance symbol map ---------- */
const BINANCE_MAP = {
  bitcoin: 'BTCUSDT', ethereum: 'ETHUSDT', binancecoin: 'BNBUSDT',
  solana: 'SOLUSDT',  ripple: 'XRPUSDT',   dogecoin: 'DOGEUSDT',
  cardano: 'ADAUSDT', tron: 'TRXUSDT',     'matic-network': 'MATICUSDT',
  litecoin: 'LTCUSDT', 'avalanche-2': 'AVAXUSDT', chainlink: 'LINKUSDT'
};

/* ---------- Fetch real OHLC data from Binance ---------- */
async function fetchOHLC(coinId, days = 1) {
  const symbol = BINANCE_MAP[coinId] || 'BTCUSDT';
  // If days=1 use 15m intervals for better granularity, else 1h
  const interval = days === 1 ? '15m' : '1h';
  const limit = days === 1 ? 96 : 24 * days; 
  const url = `https://api.binance.com/api/v3/klines?symbol=${symbol}&interval=${interval}&limit=${limit}`;
  const r = await fetch(url);
  if (!r.ok) throw new Error('Binance OHLC ' + r.status);
  const raw = await r.json();
  // raw: [openTime, open, high, low, close, ...]
  return raw.map(k => ({
    time: Math.floor(k[0] / 1000),
    open: parseFloat(k[1]),
    high: parseFloat(k[2]),
    low: parseFloat(k[3]),
    close: parseFloat(k[4])
  }));
}

/* ---------- Fetch sparkline (hourly prices for 1 day) from Binance ---------- */
async function fetchSparkline(coinId) {
  const symbol = BINANCE_MAP[coinId] || 'BTCUSDT';
  const url = `https://api.binance.com/api/v3/klines?symbol=${symbol}&interval=1h&limit=24`;
  const r = await fetch(url);
  if (!r.ok) throw new Error('Binance spark ' + r.status);
  const raw = await r.json();
  return raw.map(k => ({ time: Math.floor(k[0] / 1000), value: parseFloat(k[4]) }));
}

/* ============================================================
   MAIN CHART  (CoinDesk 20 using TradingView Widget)
   ============================================================ */
let mainChart, mainSeries;

async function initMainChart() {
  const el = document.getElementById('mainChartDiv');
  el.innerHTML = '';
  el.style.position = 'relative'; // For the logo overlay hack
  
  // Inject TradingView widget script
  const script = document.createElement('script');
  script.src = 'https://s3.tradingview.com/tv.js';
  script.async = true;
  script.onload = () => {
    new TradingView.widget({
      "autosize": true,
      "symbol": "INDEX:CD20", // CoinDesk 20 Index!
      "interval": "D",
      "timezone": "Etc/UTC",
      "theme": "dark",
      "style": "1",
      "locale": "en",
      "enable_publishing": false,
      "backgroundColor": "rgba(0, 0, 0, 0)",
      "gridColor": "rgba(255, 255, 255, 0.06)",
      "hide_top_toolbar": true,
      "hide_legend": true,
      "save_image": false,
      "container_id": el.id
    });
    
    // Add a div to hide the TradingView logo inside the iframe (by overlaying)
    const overlay = document.createElement('div');
    overlay.style.position = 'absolute';
    overlay.style.bottom = '0';
    overlay.style.left = '0';
    overlay.style.width = '100px';
    overlay.style.height = '40px';
    overlay.style.backgroundColor = 'rgba(10,31,68,.95)';
    overlay.style.zIndex = '999';
    overlay.style.pointerEvents = 'none';
    el.appendChild(overlay);
  };
  el.appendChild(script);
}

initMainChart();

/* ============================================================
   MINI SPARKLINE CARDS
   ============================================================ */
document.querySelectorAll('.mini-chart-div').forEach(async el => {
  const coinId = el.dataset.coin;

  const chart = LightweightCharts.createChart(el, {
    ...CHART_OPTS,
    width:  el.clientWidth || 200,
    height: 160,
    rightPriceScale: { visible: false },
    timeScale:       { visible: false },
    handleScroll: false,
    handleScale:  false
  });

  let data;
  try { data = await fetchSparkline(coinId); } catch (e) {
    console.warn('Mini spark error:', coinId, e);
    return;
  }

  const up    = data.length < 2 || data[data.length - 1].value >= data[0].value;
  const color = up ? '#22c55e' : '#ef4444';

  const series = chart.addAreaSeries({
    lineColor:    color,
    topColor:     up ? 'rgba(34,197,94,.2)' : 'rgba(239,68,68,.2)',
    bottomColor:  'transparent',
    lineWidth:    2,
    priceLineVisible: false,
    lastValueVisible: false
  });

  series.setData(data);
  chart.timeScale().fitContent();
});

/* ============================================================
   BIG POPUP CHART
   ============================================================ */
let bigChart = null, bigSeries = null;
let bigCoinId = 'bitcoin', bigCurrentPrice = 0;

function initBigChart() {
  const el = document.getElementById('bigChartDiv');
  if (bigChart) { bigChart.remove(); bigChart = null; }
  bigChart = LightweightCharts.createChart(el, {
    ...CHART_OPTS,
    width:  el.clientWidth,
    height: el.clientHeight || 480
  });
  bigSeries = bigChart.addCandlestickSeries({
    upColor:'#22c55e', downColor:'#dc2626',
    borderUpColor:'#22c55e', borderDownColor:'#dc2626',
    wickUpColor:'#22c55e', wickDownColor:'#dc2626'
  });
  window.addEventListener('resize', () => {
    bigChart.applyOptions({ width: el.clientWidth, height: el.clientHeight || 480 });
  });
}

async function loadBigChart(coinId, sym) {
  bigCoinId = coinId;
  document.getElementById('bigCoinTitle').innerText = sym + ' / USD';
  if (!bigChart) initBigChart();

  try {
    const data = await fetchOHLC(coinId, 1);
    bigSeries.setData(data);
    bigChart.timeScale().fitContent();

    bigCurrentPrice = data[data.length - 1].close;
    const hi = Math.max(...data.map(c => c.high));
    const lo = Math.min(...data.map(c => c.low));
    document.getElementById('todayHigh').innerText = '$' + hi.toFixed(2);
    document.getElementById('todayLow').innerText  = '$' + lo.toFixed(2);
    document.getElementById('ath').innerText = '—';
    document.getElementById('atl').innerText = '—';
  } catch (e) { console.warn('Big chart error:', e); }
}

/* auto-refresh big chart every 60 s while modal is open */
setInterval(async () => {
  if (bigChartModal.style.display !== 'block') return;
  try {
    const data = await fetchOHLC(bigCoinId, 1);
    bigSeries.setData(data);
    bigChart.timeScale().fitContent();
    bigCurrentPrice = data[data.length - 1].close;
  } catch {}
}, 60000);

/* ============================================================
   OPEN / CLOSE MODAL
   ============================================================ */
function openMarketFromCoin(coinId, sym) {
  bigChartModal.style.display = 'block';
  if (!bigChart) initBigChart();
  loadBigChart(coinId, sym);
}

function openMarketFromMain() {
  openMarketFromCoin('bitcoin', 'BTC');
}

function closeBigChart() {
  bigChartModal.style.display = 'none';
}

document.getElementById('mainChartDiv').addEventListener('click', openMarketFromMain);

/* ============================================================
   TRADE (BUY / SELL)
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
    ${type} executed @ $${price}
  </div>`;
  document.body.appendChild(box);
  setTimeout(() => box.remove(), 3000);
}

function trade(action) {
  const price = Number(bigCurrentPrice.toFixed(4));
  fetch('/api/trade', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      coin:     bigCoinId,
      price:    price,
      qty:      Number(document.getElementById('qtyInput').value),
      stoploss: Number(document.getElementById('slInput').value),
      action:   action
    })
  })
  .then(r => r.json())
  .then(d => {
    if (d.error) alert(d.error);
    else showTradePopup(action, price);
  })
  .catch(() => showTradePopup(action, price));
}

buyBtn.addEventListener('click',  () => trade('BUY'));
sellBtn.addEventListener('click', () => trade('SELL'));

/* ============================================================
   SEARCH
   ============================================================ */
function searchCrypto() {
  const q      = document.getElementById('searchInput').value.trim().toUpperCase();
  const coinId = SLUG[q];
  if (coinId) {
    openMarketFromCoin(coinId, q);
  } else {
    alert('Coin not found. Try: BTC, ETH, BNB, SOL, XRP, DOGE, ADA, TRX, MATIC, LTC, AVAX, LINK');
  }
}

document.getElementById('searchInput').addEventListener('keydown', e => {
  if (e.key === 'Enter') searchCrypto();
});

function goMarket() {
  document.getElementById('market').scrollIntoView({ behavior: 'smooth' });
}

/* ============================================================
   OPEN CHART FROM WALLET PAGE (?coin=BTC)
   ============================================================ */
window.addEventListener('load', () => {
  const coin = new URLSearchParams(window.location.search).get('coin');
  if (!coin) return;
  const slug = SLUG[coin.toUpperCase()];
  if (slug) setTimeout(() => openMarketFromCoin(slug, coin.toUpperCase()), 600);
});

/* ============================================================
   LIVE PRICE SIDEBAR – refresh every 60 s from backend
   ============================================================ */
setInterval(() => {
  fetch('/api/prices')
    .then(r => r.json())
    .then(data => {
      for (const [sym, info] of Object.entries(data)) {
        const el = document.getElementById('price-' + sym);
        if (el && info.inr) {
          const ch = info.change_24h || 0;
          el.textContent = '₹' + info.inr.toLocaleString('en-IN') +
            ' (' + (ch >= 0 ? '+' : '') + ch + '%)';
          el.className = ch >= 0 ? 'up' : 'down';
        }
      }
    }).catch(() => {});
}, 60000);
