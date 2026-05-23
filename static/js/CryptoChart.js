/* ============================================================
   CryptoChart.js - Professional Candlestick Chart Library
   Original Implementation - No Copyright Issues
   ============================================================ */

class CryptoChart {
  constructor(container, options = {}) {
    this.container = typeof container === 'string' ? document.getElementById(container) : container;
    this.width = options.width || this.container.clientWidth || 800;
    this.height = options.height || this.container.clientHeight || 480;
    this.data = [];
    this.timeframe = options.timeframe || '15m';
    this.options = {
      upColor: '#22c55e',
      downColor: '#dc2626',
      gridColor: 'rgba(255,255,255,0.07)',
      textColor: '#cbd5f5',
      backgroundColor: 'transparent',
      showMA: true,
      showBB: false,
      showRSI: false,
      ...options
    };
    
    this.svg = null;
    this.drawings = [];
    this.init();
  }
  
  init() {
    this.container.innerHTML = '';
    const wrapper = document.createElement('div');
    wrapper.style.cssText = 'width:100%;height:100%;display:flex;flex-direction:column;background:transparent';
    
    // Toolbar
    const toolbar = document.createElement('div');
    toolbar.style.cssText = 'display:flex;gap:8px;padding:12px;background:rgba(10,31,68,0.6);border-bottom:1px solid rgba(250,204,21,0.2);flex-wrap:wrap;align-items:center;font-size:12px';
    
    const timeframes = ['1m', '5m', '15m', '1h', '4h', '1d', '1w'];
    let tfHtml = timeframes.map(tf => `<button class="tf-btn" data-tf="${tf}" style="padding:6px 12px;border:1px solid ${tf === this.timeframe ? '#facc15' : 'rgba(250,204,21,0.3)'};background:${tf === this.timeframe ? 'rgba(250,204,21,0.2)' : 'transparent'};color:${tf === this.timeframe ? '#facc15' : '#cbd5f5'};border-radius:4px;cursor:pointer;font-weight:600;transition:all 0.2s">${tf}</button>`).join('');
    
    toolbar.innerHTML = tfHtml + `
      <div style="flex:1"></div>
      <label style="display:flex;align-items:center;gap:6px;color:#cbd5f5;cursor:pointer;margin-right:10px">
        <input type="checkbox" class="indicator-check" data-ind="ma" ${this.options.showMA ? 'checked' : ''} style="cursor:pointer"> MA
      </label>
      <label style="display:flex;align-items:center;gap:6px;color:#cbd5f5;cursor:pointer;margin-right:10px">
        <input type="checkbox" class="indicator-check" data-ind="bb" ${this.options.showBB ? 'checked' : ''} style="cursor:pointer"> BB
      </label>
      <label style="display:flex;align-items:center;gap:6px;color:#cbd5f5;cursor:pointer">
        <input type="checkbox" class="indicator-check" data-ind="rsi" ${this.options.showRSI ? 'checked' : ''} style="cursor:pointer"> RSI
      </label>
    `;
    
    const chartContainer = document.createElement('div');
    chartContainer.style.cssText = 'flex:1;position:relative;overflow:hidden';
    
    this.svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    this.svg.setAttribute('width', '100%');
    this.svg.setAttribute('height', '100%');
    this.svg.setAttribute('viewBox', `0 0 ${this.width} ${this.height}`);
    this.svg.setAttribute('preserveAspectRatio', 'xMidYMid meet');
    this.svg.setAttribute('style', `background: ${this.options.backgroundColor};cursor:crosshair`);
    
    chartContainer.appendChild(this.svg);
    wrapper.appendChild(toolbar);
    wrapper.appendChild(chartContainer);
    this.container.appendChild(wrapper);
    
    this.attachToolbarEvents(toolbar);
    this.attachChartEvents();
  }
  
  attachToolbarEvents(toolbar) {
    toolbar.querySelectorAll('.tf-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        this.timeframe = e.target.dataset.tf;
        toolbar.querySelectorAll('.tf-btn').forEach(b => {
          const isActive = b.dataset.tf === this.timeframe;
          b.style.borderColor = isActive ? '#facc15' : 'rgba(250,204,21,0.3)';
          b.style.background = isActive ? 'rgba(250,204,21,0.2)' : 'transparent';
          b.style.color = isActive ? '#facc15' : '#cbd5f5';
        });
        this.render();
      });
    });
    
    toolbar.querySelectorAll('.indicator-check').forEach(check => {
      check.addEventListener('change', (e) => {
        const ind = e.target.dataset.ind;
        if (ind === 'ma') this.options.showMA = e.target.checked;
        if (ind === 'bb') this.options.showBB = e.target.checked;
        if (ind === 'rsi') this.options.showRSI = e.target.checked;
        this.render();
      });
    });
  }
  
  attachChartEvents() {
    this.svg.addEventListener('mousemove', (e) => this.handleMouseMove(e));
    this.svg.addEventListener('mouseleave', () => this.removeTooltip());
  }
  
  handleMouseMove(e) {
    const rect = this.svg.getBoundingClientRect();
    const x = (e.clientX - rect.left) / rect.width * this.width;
    const y = (e.clientY - rect.top) / rect.height * this.height;
    
    this.showTooltip(x, y);
  }
  
  showTooltip(x, y) {
    const padding = 50;
    const chartWidth = this.width - (padding * 2);
    const candleCount = this.data.length;
    const candleWidth = (chartWidth / candleCount) * 0.8;
    
    for (let i = 0; i < candleCount; i++) {
      const candleX = padding + (chartWidth / candleCount) * i + (chartWidth / candleCount) * 0.1;
      if (x >= candleX && x <= candleX + candleWidth) {
        const d = this.data[i];
        this.showCandleTooltip(candleX + candleWidth / 2, y, d);
        return;
      }
    }
    this.removeTooltip();
  }
  
  showCandleTooltip(x, y, candle) {
    let existing = document.getElementById('chart-tooltip');
    if (!existing) {
      existing = document.createElement('div');
      existing.id = 'chart-tooltip';
      this.container.appendChild(existing);
    }
    
    existing.style.cssText = `position:absolute;left:${x}px;top:${y}px;background:rgba(10,31,68,0.95);border:1px solid rgba(250,204,21,0.5);padding:8px 12px;border-radius:6px;font-size:11px;color:#cbd5f5;pointer-events:none;z-index:1000;white-space:nowrap;transform:translate(-50%,-100%);margin-top:-10px`;
    existing.innerHTML = `O: $${candle.o.toFixed(2)} | H: $${candle.h.toFixed(2)} | L: $${candle.l.toFixed(2)} | C: $${candle.c.toFixed(2)}`;
  }
  
  removeTooltip() {
    const tooltip = document.getElementById('chart-tooltip');
    if (tooltip) tooltip.remove();
  }
  
  setData(data) {
    this.data = data;
    this.render();
  }
  
  calculateMA(period = 20) {
    const ma = [];
    for (let i = 0; i < this.data.length; i++) {
      if (i < period - 1) {
        ma.push(null);
      } else {
        const sum = this.data.slice(i - period + 1, i + 1).reduce((acc, d) => acc + d.c, 0);
        ma.push(sum / period);
      }
    }
    return ma;
  }
  
  calculateBB(period = 20, stdDev = 2) {
    const ma = this.calculateMA(period);
    const bb = { upper: [], middle: [], lower: [] };
    
    for (let i = 0; i < this.data.length; i++) {
      if (i < period - 1) {
        bb.upper.push(null);
        bb.middle.push(null);
        bb.lower.push(null);
      } else {
        const prices = this.data.slice(i - period + 1, i + 1).map(d => d.c);
        const mean = prices.reduce((a, b) => a + b) / period;
        const variance = prices.reduce((a, b) => a + Math.pow(b - mean, 2), 0) / period;
        const std = Math.sqrt(variance);
        
        bb.middle.push(mean);
        bb.upper.push(mean + std * stdDev);
        bb.lower.push(mean - std * stdDev);
      }
    }
    return bb;
  }
  
  render() {
    if (!this.data || this.data.length === 0) return;
    
    this.svg.innerHTML = '';
    
    const prices = this.data.map(d => [d.o, d.h, d.l, d.c]).flat();
    const minPrice = Math.min(...prices);
    const maxPrice = Math.max(...prices);
    const range = maxPrice - minPrice || 1;
    
    const padding = 50;
    const chartWidth = this.width - (padding * 2);
    const chartHeight = this.height - (padding * 2);
    
    // Background
    const bg = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
    bg.setAttribute('width', this.width);
    bg.setAttribute('height', this.height);
    bg.setAttribute('fill', this.options.backgroundColor);
    this.svg.appendChild(bg);
    
    // Grid
    this.drawGrid(padding, chartWidth, chartHeight, minPrice, maxPrice, range);
    
    // Indicators
    if (this.options.showMA) this.drawMA(padding, chartWidth, chartHeight, minPrice, range);
    if (this.options.showBB) this.drawBB(padding, chartWidth, chartHeight, minPrice, range);
    
    // Candlesticks
    this.drawCandlesticks(padding, chartWidth, chartHeight, minPrice, range);
    
    // Axes
    this.drawAxes(padding, chartWidth, chartHeight);
  }
  
  drawGrid(padding, chartWidth, chartHeight, minPrice, maxPrice, range) {
    for (let i = 0; i <= 5; i++) {
      const y = padding + (chartHeight / 5) * i;
      
      const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
      line.setAttribute('x1', padding);
      line.setAttribute('y1', y);
      line.setAttribute('x2', this.width - padding);
      line.setAttribute('y2', y);
      line.setAttribute('stroke', this.options.gridColor);
      line.setAttribute('stroke-width', '1');
      this.svg.appendChild(line);
      
      const price = maxPrice - (range / 5) * i;
      const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
      text.setAttribute('x', padding - 15);
      text.setAttribute('y', y + 5);
      text.setAttribute('text-anchor', 'end');
      text.setAttribute('font-size', '12');
      text.setAttribute('fill', this.options.textColor);
      text.textContent = '$' + (price > 1 ? price.toFixed(0) : price.toFixed(4));
      this.svg.appendChild(text);
    }
    
    for (let i = 0; i <= 5; i++) {
      const x = padding + (chartWidth / 5) * i;
      const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
      line.setAttribute('x1', x);
      line.setAttribute('y1', padding);
      line.setAttribute('x2', x);
      line.setAttribute('y2', this.height - padding);
      line.setAttribute('stroke', this.options.gridColor);
      line.setAttribute('stroke-width', '1');
      this.svg.appendChild(line);
    }
  }
  
  drawMA(padding, chartWidth, chartHeight, minPrice, range) {
    const ma = this.calculateMA(20);
    const candleCount = this.data.length;
    const candleWidth = (chartWidth / candleCount) * 0.8;
    const spacing = (chartWidth / candleCount) * 0.2;
    
    let pathData = '';
    for (let i = 0; i < ma.length; i++) {
      if (ma[i] !== null) {
        const x = padding + (chartWidth / candleCount) * i + spacing / 2 + candleWidth / 2;
        const y = padding + chartHeight - ((ma[i] - minPrice) / range) * chartHeight;
        pathData += (pathData ? ' L' : 'M') + x + ',' + y;
      }
    }
    
    const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
    path.setAttribute('d', pathData);
    path.setAttribute('stroke', '#f59e0b');
    path.setAttribute('stroke-width', '2');
    path.setAttribute('fill', 'none');
    path.setAttribute('opacity', '0.7');
    this.svg.appendChild(path);
  }
  
  drawBB(padding, chartWidth, chartHeight, minPrice, range) {
    const bb = this.calculateBB(20, 2);
    const candleCount = this.data.length;
    const candleWidth = (chartWidth / candleCount) * 0.8;
    const spacing = (chartWidth / candleCount) * 0.2;
    
    ['upper', 'middle', 'lower'].forEach((band, idx) => {
      let pathData = '';
      for (let i = 0; i < bb[band].length; i++) {
        if (bb[band][i] !== null) {
          const x = padding + (chartWidth / candleCount) * i + spacing / 2 + candleWidth / 2;
          const y = padding + chartHeight - ((bb[band][i] - minPrice) / range) * chartHeight;
          pathData += (pathData ? ' L' : 'M') + x + ',' + y;
        }
      }
      
      const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
      path.setAttribute('d', pathData);
      path.setAttribute('stroke', idx === 1 ? '#8b5cf6' : '#6366f1');
      path.setAttribute('stroke-width', idx === 1 ? '2' : '1');
      path.setAttribute('fill', 'none');
      path.setAttribute('opacity', '0.6');
      path.setAttribute('stroke-dasharray', idx === 1 ? '0' : '3,3');
      this.svg.appendChild(path);
    });
  }
  
  drawCandlesticks(padding, chartWidth, chartHeight, minPrice, range) {
    const candleCount = this.data.length;
    const candleWidth = (chartWidth / candleCount) * 0.8;
    const spacing = (chartWidth / candleCount) * 0.2;
    
    for (let i = 0; i < candleCount; i++) {
      const d = this.data[i];
      const x = padding + (chartWidth / candleCount) * i + spacing / 2;
      
      const openY = padding + chartHeight - ((d.o - minPrice) / range) * chartHeight;
      const closeY = padding + chartHeight - ((d.c - minPrice) / range) * chartHeight;
      const highY = padding + chartHeight - ((d.h - minPrice) / range) * chartHeight;
      const lowY = padding + chartHeight - ((d.l - minPrice) / range) * chartHeight;
      
      const color = d.c >= d.o ? this.options.upColor : this.options.downColor;
      
      // Wick
      const wick = document.createElementNS('http://www.w3.org/2000/svg', 'line');
      wick.setAttribute('x1', x + candleWidth / 2);
      wick.setAttribute('y1', highY);
      wick.setAttribute('x2', x + candleWidth / 2);
      wick.setAttribute('y2', lowY);
      wick.setAttribute('stroke', color);
      wick.setAttribute('stroke-width', '1');
      wick.setAttribute('opacity', '0.8');
      this.svg.appendChild(wick);
      
      // Body
      const bodyHeight = Math.max(Math.abs(closeY - openY), 2);
      const body = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
      body.setAttribute('x', x);
      body.setAttribute('y', Math.min(openY, closeY));
      body.setAttribute('width', candleWidth);
      body.setAttribute('height', bodyHeight);
      body.setAttribute('fill', color);
      body.setAttribute('stroke', color);
      body.setAttribute('stroke-width', '1');
      body.setAttribute('opacity', '0.9');
      this.svg.appendChild(body);
    }
  }
  
  drawAxes(padding, chartWidth, chartHeight) {
    const xAxis = document.createElementNS('http://www.w3.org/2000/svg', 'line');
    xAxis.setAttribute('x1', padding);
    xAxis.setAttribute('y1', this.height - padding);
    xAxis.setAttribute('x2', this.width - padding);
    xAxis.setAttribute('y2', this.height - padding);
    xAxis.setAttribute('stroke', this.options.gridColor);
    xAxis.setAttribute('stroke-width', '2');
    this.svg.appendChild(xAxis);
    
    const yAxis = document.createElementNS('http://www.w3.org/2000/svg', 'line');
    yAxis.setAttribute('x1', padding);
    yAxis.setAttribute('y1', padding);
    yAxis.setAttribute('x2', padding);
    yAxis.setAttribute('y2', this.height - padding);
    yAxis.setAttribute('stroke', this.options.gridColor);
    yAxis.setAttribute('stroke-width', '2');
    this.svg.appendChild(yAxis);
  }
  
  destroy() {
    if (this.svg) {
      this.svg.remove();
    }
    this.removeTooltip();
  }
}

if (typeof module !== 'undefined' && module.exports) {
  module.exports = CryptoChart;
}
