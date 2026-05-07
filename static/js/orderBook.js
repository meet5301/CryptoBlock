'use strict';

class OrderBook {
  constructor(containerId, options = {}) {
    this.container = document.getElementById(containerId);
    if (!this.container) return;
    this.symbol  = (options.symbol || 'BTC').toUpperCase();
    this.socket  = options.socket || null;
    this.maxRows = options.maxRows || 10;
    this._data   = { bids: [], asks: [], spread: 0, price: 0 };
    this._build();
    this._fetch();
    if (this.socket) {
      this.socket.on('orderbook_update', d => {
        if (d.symbol === this.symbol) this._render(d);
      });
    }
  }

  _build() {
    this.container.innerHTML = `
      <div class="orderbook-wrapper">
        <div class="orderbook-header">
          <span class="orderbook-title">Order Book &mdash; ${this.symbol}</span>
          <span class="orderbook-spread">Spread: <span id="ob-spread-${this.symbol}">&#8212;</span></span>
        </div>
        <div class="orderbook-cols">
          <span>Price (INR)</span>
          <span style="text-align:right">Qty</span>
          <span style="text-align:right">Total</span>
        </div>
        <div id="ob-asks-${this.symbol}"></div>
        <div class="orderbook-mid" id="ob-mid-${this.symbol}">&#8212;</div>
        <div id="ob-bids-${this.symbol}"></div>
      </div>`;
  }

  _fetch() {
    fetch(`/api/charts/orderbook/${this.symbol}`)
      .then(r => r.json())
      .then(d => this._render(d))
      .catch(() => {});
  }

  _render(data) {
    this._data = data;
    const { bids = [], asks = [], spread = 0, price = 0 } = data;
    const maxTotal = Math.max(...bids.map(b => b.total), ...asks.map(a => a.total), 1);

    const asksEl   = document.getElementById(`ob-asks-${this.symbol}`);
    const bidsEl   = document.getElementById(`ob-bids-${this.symbol}`);
    const midEl    = document.getElementById(`ob-mid-${this.symbol}`);
    const spreadEl = document.getElementById(`ob-spread-${this.symbol}`);
    if (!asksEl) return;

    // Asks reversed so lowest ask is nearest mid
    asksEl.innerHTML = [...asks].reverse().slice(0, this.maxRows).map(a => {
      const pct = (a.total / maxTotal * 100).toFixed(1);
      return `<div class="orderbook-row ask">
        <div class="orderbook-depth-bar" style="width:${pct}%"></div>
        <span class="ob-price">${this._fmt(a.price)}</span>
        <span class="ob-qty">${Number(a.qty).toFixed(4)}</span>
        <span class="ob-total">${this._fmt(a.total)}</span>
      </div>`;
    }).join('');

    if (midEl) midEl.innerHTML = `<span style="color:#1D9E75">&#8377;${this._fmt(price)}</span>`;

    bidsEl.innerHTML = bids.slice(0, this.maxRows).map(b => {
      const pct = (b.total / maxTotal * 100).toFixed(1);
      return `<div class="orderbook-row bid">
        <div class="orderbook-depth-bar" style="width:${pct}%"></div>
        <span class="ob-price">${this._fmt(b.price)}</span>
        <span class="ob-qty">${Number(b.qty).toFixed(4)}</span>
        <span class="ob-total">${this._fmt(b.total)}</span>
      </div>`;
    }).join('');

    if (spreadEl) spreadEl.textContent = `\u20b9${this._fmt(spread)}`;
  }

  _fmt(n) {
    if (n == null) return '\u2014';
    return Number(n).toLocaleString('en-IN', { maximumFractionDigits: 2 });
  }

  loadSymbol(symbol) {
    this.symbol = symbol.toUpperCase();
    this._build();
    this._fetch();
  }

  refresh() { this._fetch(); }
}

window.OrderBook = OrderBook;
