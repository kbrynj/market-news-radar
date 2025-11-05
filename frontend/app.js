/**
 * Market News Radar - Frontend JavaScript
 * Handles API calls, WebSocket, infinite scroll, and UI updates
 */

// State
let articles = [];
let currentOffset = 0;
let isLoading = false;
let hasMore = true;
let currentSearch = '';
let currentMinScore = null;
let currentTickerFilter = null;
let ws = null;
let autoRefreshInterval = null;

// Helper: Get Admin Token from localStorage
function getAdminToken() {
    return localStorage.getItem('adminToken') || '';
}

// Helper: Set Admin Token in localStorage
function setAdminToken(token) {
    if (token) {
        localStorage.setItem('adminToken', token);
    } else {
        localStorage.removeItem('adminToken');
    }
}

// Helper: Escape HTML
function esc(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

// Theme Switching
function setupThemeToggle() {
    const themeToggle = document.getElementById('theme-toggle');
    const themeIcon = themeToggle.querySelector('.theme-icon');
    
    // Load saved theme or default to dark
    const savedTheme = localStorage.getItem('theme') || 'dark';
    applyTheme(savedTheme);
    
    // Toggle theme on button click
    themeToggle.addEventListener('click', () => {
        const currentTheme = document.documentElement.dataset.theme || 'dark';
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        applyTheme(newTheme);
        localStorage.setItem('theme', newTheme);
    });
    
    function applyTheme(theme) {
        document.documentElement.dataset.theme = theme;
        // Update icon: moon for dark mode, sun for light mode
        themeIcon.textContent = theme === 'dark' ? '🌙' : '☀️';
    }
}

// Helper: API Fetch
async function api(endpoint, options = {}) {
    try {
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers
        };
        
        // Add admin token for non-GET requests
        const method = (options.method || 'GET').toUpperCase();
        if (method !== 'GET') {
            const token = getAdminToken();
            if (token) {
                headers['x-admin-token'] = token;
            }
        }
        
        const response = await fetch(endpoint, {
            headers,
            ...options
        });
        
        if (!response.ok) {
            const error = await response.json().catch(() => ({}));
            throw new Error(error.detail || `HTTP ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

// Helper: Show Toast
function showToast(message, type = 'info') {
    const toast = document.getElementById('toast');
    const toastMessage = document.getElementById('toast-message');
    
    toastMessage.textContent = message;
    toast.className = `toast show ${type}`;
    
    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

// Helper: Format timestamp
function formatTimestamp(timestamp) {
    const date = new Date(timestamp * 1000);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);
    
    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    
    return date.toLocaleDateString();
}

// Helper: Get sentiment chip class
function getSentimentClass(sentiment) {
    if (sentiment > 0.1) return 'pos';
    if (sentiment < -0.1) return 'neg';
    return 'neutral';
}

// Helper: Format sentiment value
function formatSentiment(sentiment) {
    const value = sentiment.toFixed(2);
    if (sentiment > 0.1) return `😊 ${value}`;
    if (sentiment < -0.1) return `😟 ${value}`;
    return `😐 ${value}`;
}

// ============ WebSocket ============

function connectWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws`;
    
    ws = new WebSocket(wsUrl);
    
    ws.onopen = () => {
        console.log('WebSocket connected');
        updateConnectionStatus('connected');
    };
    
    ws.onmessage = (event) => {
        try {
            const data = JSON.parse(event.data);
            console.log('WebSocket message:', data);
            
            if (data.type === 'refresh') {
                showToast(`${data.inserted} new articles available!`, 'success');
                reloadArticles();
            }
        } catch (error) {
            console.error('WebSocket message error:', error);
        }
    };
    
    ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        updateConnectionStatus('disconnected');
    };
    
    ws.onclose = () => {
        console.log('WebSocket closed, reconnecting...');
        updateConnectionStatus('connecting');
        setTimeout(connectWebSocket, 3000);
    };
}

function updateConnectionStatus(status) {
    const statusBadge = document.getElementById('connection-status');
    statusBadge.className = `status-badge status-${status}`;
    
    const statusText = {
        connected: '⚡ Live',
        connecting: '⏳ Connecting...',
        disconnected: '❌ Disconnected'
    };
    
    statusBadge.textContent = statusText[status] || statusText.connecting;
}

// ============ Settings ============

async function loadSettings() {
    try {
        const settings = await api('/api/settings');
        
        document.getElementById('refresh-interval').value = settings.refresh_interval || 300;
        document.getElementById('min-score-default').value = settings.min_score || 1;
        document.getElementById('strong-words').value = settings.strong_words || '';
    } catch (error) {
        showToast('Failed to load settings', 'error');
    }
}

async function saveSettings(event) {
    event.preventDefault();
    
    const formData = new FormData(event.target);
    const settings = {
        refresh_interval: parseInt(formData.get('refresh_interval')),
        min_score: parseInt(formData.get('min_score')),
        strong_words: formData.get('strong_words')
    };
    
    try {
        await api('/api/settings', {
            method: 'PUT',
            body: JSON.stringify(settings)
        });
        
        showToast('Settings saved successfully', 'success');
    } catch (error) {
        showToast('Failed to save settings', 'error');
    }
}

// ============ Feeds ============

async function loadFeeds() {
    try {
        const data = await api('/api/feeds');
        const feedsList = document.getElementById('feeds-list');
        
        feedsList.innerHTML = data.feeds.map(feed => `
            <li>
                <span>${esc(feed.name)}</span>
                <button onclick="deleteFeed(${feed.id})" aria-label="Delete feed">×</button>
            </li>
        `).join('');
    } catch (error) {
        showToast('Failed to load feeds', 'error');
    }
}

async function addFeed(event) {
    event.preventDefault();
    
    const name = document.getElementById('feed-name').value.trim();
    const url = document.getElementById('feed-url').value.trim();
    
    if (!name || !url) return;
    
    try {
        await api('/api/feeds', {
            method: 'POST',
            body: JSON.stringify({ name, url })
        });
        
        document.getElementById('feed-name').value = '';
        document.getElementById('feed-url').value = '';
        
        showToast('Feed added successfully', 'success');
        loadFeeds();
    } catch (error) {
        showToast('Failed to add feed', 'error');
    }
}

async function deleteFeed(id) {
    if (!confirm('Delete this feed?')) return;
    
    try {
        await api(`/api/feeds/${id}`, { method: 'DELETE' });
        showToast('Feed deleted', 'success');
        loadFeeds();
    } catch (error) {
        showToast('Failed to delete feed', 'error');
    }
}

// ============ Tickers ============

async function loadTickers() {
    try {
        const data = await api('/api/tickers');
        const tickersList = document.getElementById('tickers-list');
        
        tickersList.innerHTML = data.tickers.map(ticker => `
            <li class="ticker-item">
                <div class="ticker-info">
                    <strong>${esc(ticker.symbol)}</strong>
                    ${ticker.company_names ? `<br><small style="color: var(--muted);">${esc(ticker.company_names)}</small>` : ''}
                </div>
                <button onclick="deleteTicker(${ticker.id})" aria-label="Delete ticker">×</button>
            </li>
        `).join('');
        
        // Also populate the ticker filter dropdown
        const tickerFilterSelect = document.getElementById('ticker-filter-select');
        if (tickerFilterSelect) {
            // Keep the current selection if any
            const currentValue = tickerFilterSelect.value;
            
            tickerFilterSelect.innerHTML = '<option value="">All Tickers</option>' + 
                data.tickers.map(ticker => 
                    `<option value="${esc(ticker.symbol)}">${esc(ticker.symbol)}</option>`
                ).join('');
            
            // Restore selection if it still exists
            if (currentValue && data.tickers.some(t => t.symbol === currentValue)) {
                tickerFilterSelect.value = currentValue;
            }
        }
    } catch (error) {
        showToast('Failed to load tickers', 'error');
    }
}

async function addTicker(event) {
    event.preventDefault();
    
    const symbol = document.getElementById('ticker-symbol').value.trim().toUpperCase();
    const companyNames = document.getElementById('ticker-companies').value.trim().toLowerCase();
    
    if (!symbol) return;
    
    try {
        await api('/api/tickers', {
            method: 'POST',
            body: JSON.stringify({ 
                symbol,
                company_names: companyNames
            })
        });
        
        document.getElementById('ticker-symbol').value = '';
        document.getElementById('ticker-companies').value = '';
        
        showToast(`Ticker ${symbol} added successfully`, 'success');
        loadTickers();
    } catch (error) {
        showToast('Failed to add ticker', 'error');
    }
}

async function deleteTicker(id) {
    if (!confirm('Delete this ticker?')) return;
    
    try {
        await api(`/api/tickers/${id}`, { method: 'DELETE' });
        showToast('Ticker deleted', 'success');
        loadTickers();
    } catch (error) {
        showToast('Failed to delete ticker', 'error');
    }
}

// ============ Keywords ============

async function loadKeywords() {
    try {
        const data = await api('/api/keywords');
        const keywordsList = document.getElementById('keywords-list');
        
        keywordsList.innerHTML = data.keywords.map(keyword => `
            <li>
                <span>${esc(keyword.word)}</span>
                <button onclick="deleteKeyword(${keyword.id})" aria-label="Delete keyword">×</button>
            </li>
        `).join('');
    } catch (error) {
        showToast('Failed to load keywords', 'error');
    }
}

async function addKeyword(event) {
    event.preventDefault();
    
    const word = document.getElementById('keyword-word').value.trim().toLowerCase();
    
    if (!word) return;
    
    try {
        await api('/api/keywords', {
            method: 'POST',
            body: JSON.stringify({ word })
        });
        
        document.getElementById('keyword-word').value = '';
        
        showToast('Keyword added successfully', 'success');
        loadKeywords();
    } catch (error) {
        showToast('Failed to add keyword', 'error');
    }
}

async function deleteKeyword(id) {
    if (!confirm('Delete this keyword?')) return;
    
    try {
        await api(`/api/keywords/${id}`, { method: 'DELETE' });
        showToast('Keyword deleted', 'success');
        loadKeywords();
    } catch (error) {
        showToast('Failed to delete keyword', 'error');
    }
}

// ============ Articles ============

async function loadArticles(append = false) {
    if (isLoading) return;
    
    isLoading = true;
    
    // Show loading indicator
    const container = document.getElementById('articles-container');
    if (!append) {
        container.innerHTML = '<div class="loading-indicator"><div class="spinner"></div><p>Loading articles...</p></div>';
    }
    
    try {
        const params = new URLSearchParams({
            limit: 50,
            offset: append ? currentOffset : 0
        });
        
        if (currentSearch) {
            params.append('q', currentSearch);
        }
        
        if (currentMinScore !== null && currentMinScore !== '') {
            params.append('min_score', currentMinScore);
        }
        
        const data = await api(`/api/articles?${params}`);
        
        if (!append) {
            articles = data.articles;
            currentOffset = 0;
        } else {
            articles = [...articles, ...data.articles];
        }
        
        currentOffset += data.articles.length;
        hasMore = currentOffset < data.total;
        
        renderArticles();
        updateResultsCount(data.total);
        
        // Show/hide load more trigger
        const loadMoreTrigger = document.getElementById('load-more-trigger');
        if (hasMore) {
            loadMoreTrigger.classList.add('visible');
        } else {
            loadMoreTrigger.classList.remove('visible');
        }
        
    } catch (error) {
        showToast('Failed to load articles', 'error');
        container.innerHTML = '<div class="loading-indicator"><p>Failed to load articles</p></div>';
    } finally {
        isLoading = false;
    }
}

function renderArticles() {
    const container = document.getElementById('articles-container');
    
    // Filter articles by ticker if filter is active
    let filteredArticles = articles;
    if (currentTickerFilter) {
        filteredArticles = articles.filter(article => {
            if (!article.tickers) return false;
            const articleTickers = article.tickers.split(',').filter(t => t);
            return articleTickers.includes(currentTickerFilter);
        });
    }
    
    if (filteredArticles.length === 0) {
        const message = currentTickerFilter 
            ? `No articles found for ticker: ${currentTickerFilter}`
            : 'No articles found';
        container.innerHTML = `<div class="loading-indicator"><p>${message}</p></div>`;
        return;
    }
    
    container.innerHTML = filteredArticles.map(article => {
        const tickers = article.tickers ? article.tickers.split(',').filter(t => t) : [];
        const sentimentClass = getSentimentClass(article.sentiment);
        
        // Debug logging
        if (tickers.length > 0) {
            console.log('Article with tickers:', article.title, 'Tickers:', tickers);
        }
        
        return `
            <article class="card">
                <div class="meta">
                    <span class="feed-name">${esc(article.feed_name)}</span>
                    <span class="timestamp">${formatTimestamp(article.published_ts)}</span>
                </div>
                
                <h3>
                    <a href="${esc(article.url)}" target="_blank" rel="noopener noreferrer">
                        ${esc(article.title)}
                    </a>
                </h3>
                
                ${article.summary ? `<p class="summary">${esc(article.summary)}</p>` : ''}
                
                ${tickers.length > 0 ? `
                    <div class="chips">
                        <strong style="font-size: 0.75rem; color: var(--muted); margin-right: 0.5rem;">📈 Mentioned:</strong>
                        ${tickers.map(ticker => 
                            `<span class="chip ticker" data-ticker="${esc(ticker)}" onclick="highlightTicker('${esc(ticker)}')" title="Click to highlight all ${esc(ticker)} articles">${esc(ticker)}</span>`
                        ).join('')}
                    </div>
                ` : ''}
                
                <div class="foot">
                    <span>Score: <strong class="score" title="Relevance: 2pts/ticker + 1pt/keyword + 1pt/strong word">${article.score}</strong></span>
                    <span class="chip ${sentimentClass}" title="Sentiment: ${article.sentiment.toFixed(3)}">
                        ${formatSentiment(article.sentiment)}
                    </span>
                </div>
            </article>
        `;
    }).join('');
}

function updateResultsCount(total) {
    const resultsCount = document.getElementById('results-count');
    resultsCount.textContent = `${total} article${total !== 1 ? 's' : ''}`;
}

function reloadArticles() {
    currentOffset = 0;
    hasMore = true;
    loadArticles(false);
}

// ============ Manual Refresh ============

async function manualRefresh() {
    const btn = document.getElementById('refresh-btn');
    btn.disabled = true;
    btn.textContent = '⏳ Refreshing...';
    
    try {
        const result = await api('/api/refresh', { method: 'POST' });
        showToast(`Refresh complete: ${result.inserted} new articles`, 'success');
        reloadArticles();
    } catch (error) {
        showToast('Refresh failed', 'error');
    } finally {
        btn.disabled = false;
        btn.textContent = '🔄 Refresh Now';
    }
}

// ============ Prune Articles ============

async function pruneArticles() {
    if (!confirm('Delete all articles older than 7 days?')) return;
    
    try {
        const result = await api('/api/articles?days=7', { method: 'DELETE' });
        showToast(`Deleted ${result.deleted} articles`, 'success');
        reloadArticles();
    } catch (error) {
        showToast('Failed to delete articles', 'error');
    }
}

// ============ Search & Filter ============

function setupSearchAndFilter() {
    const searchInput = document.getElementById('search-input');
    const minScoreSelect = document.getElementById('min-score-select');
    const tickerFilterSelect = document.getElementById('ticker-filter-select');
    
    let searchTimeout;
    
    searchInput.addEventListener('input', (e) => {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
            currentSearch = e.target.value.trim();
            reloadArticles();
        }, 500);
    });
    
    minScoreSelect.addEventListener('change', (e) => {
        currentMinScore = e.target.value ? parseInt(e.target.value) : null;
        reloadArticles();
    });
    
    tickerFilterSelect.addEventListener('change', (e) => {
        currentTickerFilter = e.target.value || null;
        renderArticles(); // Just re-render, don't reload from API
    });
}

// ============ Infinite Scroll ============

function setupInfiniteScroll() {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting && hasMore && !isLoading) {
                loadArticles(true);
            }
        });
    }, {
        rootMargin: '100px'
    });
    
    const trigger = document.getElementById('load-more-trigger');
    observer.observe(trigger);
}

// ============ Auto Refresh ============

function setupAutoRefresh() {
    // Auto-refresh every 30 seconds
    autoRefreshInterval = setInterval(() => {
        console.log('Auto-refresh triggered');
        reloadArticles();
    }, 30000);
}

// ============ Info Modal ============

function setupModal() {
    const modal = document.getElementById('info-modal');
    const infoBtn = document.getElementById('info-btn');
    const closeBtn = modal.querySelector('.modal-close');
    
    infoBtn.addEventListener('click', () => {
        modal.classList.add('show');
        modal.setAttribute('aria-hidden', 'false');
    });
    
    closeBtn.addEventListener('click', () => {
        modal.classList.remove('show');
        modal.setAttribute('aria-hidden', 'true');
    });
    
    // Close on outside click
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.classList.remove('show');
            modal.setAttribute('aria-hidden', 'true');
        }
    });
    
    // Close on Escape key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && modal.classList.contains('show')) {
            modal.classList.remove('show');
            modal.setAttribute('aria-hidden', 'true');
        }
    });
}

// ============ Ticker Highlighting ============

let highlightedTicker = null;

function highlightTicker(ticker) {
    const tickerFilterSelect = document.getElementById('ticker-filter-select');
    
    // Toggle filter
    if (currentTickerFilter === ticker) {
        // Remove filter
        currentTickerFilter = null;
        if (tickerFilterSelect) tickerFilterSelect.value = '';
        highlightedTicker = null;
        showToast(`Showing all tickers`, 'info');
    } else {
        // Set filter
        currentTickerFilter = ticker;
        if (tickerFilterSelect) tickerFilterSelect.value = ticker;
        highlightedTicker = ticker;
        showToast(`Filtering articles for ${ticker}`, 'info');
    }
    
    // Re-render articles with filter
    renderArticles();
}

// ============ Ticker Autocomplete ============

let autocompleteTimeout = null;
let selectedAutocompleteIndex = -1;

function setupTickerAutocomplete() {
    const input = document.getElementById('ticker-symbol');
    const dropdown = document.getElementById('ticker-autocomplete');
    
    if (!input || !dropdown) return;
    
    // Handle input changes (with debounce)
    input.addEventListener('input', (e) => {
        const query = e.target.value.trim();
        
        // Clear timeout
        clearTimeout(autocompleteTimeout);
        
        if (query.length < 1) {
            hideAutocomplete();
            return;
        }
        
        // Debounce: wait 300ms after user stops typing
        autocompleteTimeout = setTimeout(() => {
            searchTickers(query);
        }, 300);
    });
    
    // Handle keyboard navigation
    input.addEventListener('keydown', (e) => {
        const items = dropdown.querySelectorAll('.autocomplete-item');
        
        if (e.key === 'ArrowDown') {
            e.preventDefault();
            selectedAutocompleteIndex = Math.min(selectedAutocompleteIndex + 1, items.length - 1);
            updateAutocompleteSelection(items);
        } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            selectedAutocompleteIndex = Math.max(selectedAutocompleteIndex - 1, -1);
            updateAutocompleteSelection(items);
        } else if (e.key === 'Enter' && selectedAutocompleteIndex >= 0) {
            e.preventDefault();
            items[selectedAutocompleteIndex].click();
        } else if (e.key === 'Escape') {
            hideAutocomplete();
        }
    });
    
    // Hide dropdown when clicking outside
    document.addEventListener('click', (e) => {
        if (!input.contains(e.target) && !dropdown.contains(e.target)) {
            hideAutocomplete();
        }
    });
}

async function searchTickers(query) {
    const dropdown = document.getElementById('ticker-autocomplete');
    
    try {
        const response = await fetch(`/api/search/tickers?q=${encodeURIComponent(query)}`);
        
        if (!response.ok) {
            console.error('Failed to search tickers:', response.statusText);
            hideAutocomplete();
            return;
        }
        
        const data = await response.json();
        displayAutocompleteResults(data.results);
        
    } catch (error) {
        console.error('Error searching tickers:', error);
        hideAutocomplete();
    }
}

function displayAutocompleteResults(results) {
    const dropdown = document.getElementById('ticker-autocomplete');
    
    if (!results || results.length === 0) {
        dropdown.innerHTML = '<div class="autocomplete-item" style="color: var(--muted);">No results found</div>';
        dropdown.removeAttribute('hidden');
        return;
    }
    
    dropdown.innerHTML = results.map(ticker => `
        <div class="autocomplete-item" data-symbol="${ticker.symbol}" data-name="${ticker.name}">
            <div class="autocomplete-item-main">
                <div class="autocomplete-symbol">${ticker.symbol}</div>
                <div class="autocomplete-name">${ticker.name}</div>
            </div>
            <div class="autocomplete-type">${ticker.type}</div>
        </div>
    `).join('');
    
    // Add click handlers
    dropdown.querySelectorAll('.autocomplete-item').forEach((item, index) => {
        item.addEventListener('click', () => {
            selectTicker(item.dataset.symbol, item.dataset.name);
        });
    });
    
    dropdown.removeAttribute('hidden');
    selectedAutocompleteIndex = -1;
}

function updateAutocompleteSelection(items) {
    items.forEach((item, index) => {
        if (index === selectedAutocompleteIndex) {
            item.classList.add('active');
            item.scrollIntoView({ block: 'nearest' });
        } else {
            item.classList.remove('active');
        }
    });
}

function selectTicker(symbol, name) {
    const input = document.getElementById('ticker-symbol');
    const companiesInput = document.getElementById('ticker-companies');
    
    // Set symbol
    input.value = symbol;
    
    // Set company name (convert to lowercase, remove "Inc", "Corp", etc.)
    const cleanName = name.toLowerCase()
        .replace(/\s+(inc|corp|corporation|ltd|limited|plc|llc|class [a-z])\.?$/i, '')
        .trim();
    companiesInput.value = cleanName;
    
    hideAutocomplete();
    
    // Focus the companies input for review
    companiesInput.focus();
}

function hideAutocomplete() {
    const dropdown = document.getElementById('ticker-autocomplete');
    if (dropdown) {
        dropdown.setAttribute('hidden', '');
        dropdown.innerHTML = '';
    }
    selectedAutocompleteIndex = -1;
}

// ============ Event Listeners ============

function setupEventListeners() {
    // Forms
    document.getElementById('general-settings-form').addEventListener('submit', saveSettings);
    document.getElementById('add-feed-form').addEventListener('submit', addFeed);
    document.getElementById('add-ticker-form').addEventListener('submit', addTicker);
    document.getElementById('add-keyword-form').addEventListener('submit', addKeyword);
    
    // Buttons
    document.getElementById('refresh-btn').addEventListener('click', manualRefresh);
    document.getElementById('prune-btn').addEventListener('click', pruneArticles);
    
    // Admin Token input
    const adminTokenInput = document.getElementById('admin-token');
    if (adminTokenInput) {
        // Load saved token on startup
        adminTokenInput.value = getAdminToken();
        
        // Save token when it changes
        adminTokenInput.addEventListener('change', (e) => {
            setAdminToken(e.target.value.trim());
            if (e.target.value.trim()) {
                showToast('Admin token saved', 'success');
            } else {
                showToast('Admin token cleared', 'info');
            }
        });
    }
    
    // Modal
    setupModal();
}

// ============ Initialization ============

async function init() {
    console.log('Initializing Market News Radar...');
    
    // Setup event listeners
    setupEventListeners();
    setupSearchAndFilter();
    setupInfiniteScroll();
    setupAutoRefresh();
    setupTickerAutocomplete();
    setupThemeToggle();
    
    // Check tip banner
    checkTipBanner();
    
    // Load initial data
    await Promise.all([
        loadSettings(),
        loadFeeds(),
        loadTickers(),
        loadKeywords(),
        loadArticles()
    ]);
    
    // Connect WebSocket
    connectWebSocket();
    
    console.log('Initialization complete');
}

// Start the app when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}

// ============ Tip Banner ============

function closeTipBanner() {
    const banner = document.getElementById('tip-banner');
    if (banner) {
        banner.classList.add('hidden');
        // Remember user closed it
        localStorage.setItem('tipBannerClosed', 'true');
    }
}

function checkTipBanner() {
    const banner = document.getElementById('tip-banner');
    if (banner && localStorage.getItem('tipBannerClosed') === 'true') {
        banner.classList.add('hidden');
    }
}

// Make functions available globally (for inline onclick handlers)
window.deleteFeed = deleteFeed;
window.deleteTicker = deleteTicker;
window.deleteKeyword = deleteKeyword;
window.highlightTicker = highlightTicker;
window.closeTipBanner = closeTipBanner;
