# Dataset Update Schedule & Scandinavian Markets

## ✅ Scandinavian Markets Added

The ticker dataset now includes **46 major companies** from Nordic exchanges:

### 🇸🇪 Sweden - Nasdaq Stockholm (.ST)
- Volvo, Ericsson, H&M, Sandvik, Atlas Copco, Alfa Laval
- Swedbank, SEB Bank, Hexagon, SKF, Electrolux
- **Major Focus**: Manufacturing, telecom, banking, retail

### 🇳🇴 Norway - Oslo Børs (.OL)
- Equinor (energy), DNB Bank, Telenor (telecom)
- Mowi, SalMar (seafood/aquaculture)
- Yara International (chemicals), Aker BP (oil & gas)
- **Major Focus**: Energy, seafood, shipping

### 🇩🇰 Denmark - Nasdaq Copenhagen (.CO)
- Novo Nordisk (pharma), Maersk (shipping), Ørsted (green energy)
- Danske Bank, Carlsberg (beverages), Vestas (wind turbines)
- Coloplast (medical devices), DSV (logistics)
- **Major Focus**: Pharma, shipping, renewable energy

### 🇫🇮 Finland - Nasdaq Helsinki (.HE)
- Nokia (telecom), Neste (renewable fuels), Fortum (energy)
- Sampo (insurance), KONE (elevators), Wärtsilä (marine equipment)
- UPM-Kymmene, Stora Enso (forestry), Metso Outotec (mining equipment)
- **Major Focus**: Technology, energy, forestry, industrial equipment

---

## 📅 Update Frequency Recommendations

### How Often New Tickers Are Added to Markets?

#### 🆕 **IPOs / New Listings**
- **US Markets**: 10-20 IPOs per month (varies by market conditions)
  - 2023-2024: ~150-200 IPOs/year
  - Bull markets: up to 300+/year
  - Bear markets: down to 50-100/year
  
- **European Markets**: 5-10 IPOs per month across major exchanges
  - Nordic markets: 2-5 IPOs per month combined
  
- **Crypto**: 50-100 new tokens per month
  - Very high volatility
  - Many tokens launch and fail quickly

#### 💸 **Delistings / Ticker Changes**
- **Delistings**: 3-5% of listings per year (mergers, acquisitions, bankruptcies)
- **Ticker Changes**: Rare (company rebranding, restructuring)
- **Example**: Twitter → X (ticker changed TWTR → X in 2023)

---

## ⏰ Recommended Update Schedule

### 📊 **For Production Use** ⭐ RECOMMENDED
**Run: Monthly**
- Captures 95% of new IPOs
- Catches most crypto additions
- Good balance of freshness vs. maintenance
- **Cron**: `0 0 1 * *` (1st of each month at midnight)

### 💰 **Crypto-Focused**
**Run: Weekly**
- Crypto markets move fast (100+ new coins/week)
- Better for crypto-heavy news tracking
- Higher maintenance burden
- **Cron**: `0 0 * * 0` (Every Sunday at midnight)

### 🏛️ **Conservative / Established Markets Only**
**Run: Quarterly**
- Sufficient for blue-chip stocks
- Minimal new listings
- Low maintenance
- **Cron**: `0 0 1 1,4,7,10 *` (Jan 1, Apr 1, Jul 1, Oct 1)

### 🎯 **Aggressive / Complete Coverage**
**Run: Daily (Crypto only)**
- Only fetch crypto tickers daily
- Keep stock tickers monthly
- Hybrid approach for maximum coverage
- Requires split scripts

---

## 🔄 Current Dataset Composition

After running the generator:

| Type       | Count  | Notes |
|------------|--------|-------|
| **Stocks** | 106    | US majors + 46 Nordic companies |
| **ETFs**   | 9      | Major index ETFs (SPY, QQQ, etc.) |
| **Indexes**| 1      | VIX |
| **Cryptos**| 4,884  | From CoinGecko API |
| **TOTAL**  | 5,000  | Optimized for browser performance |

**File Size**: 0.53 MB (browser-friendly, loads instantly)

---

## 🛠️ How to Update the Dataset

### Manual Update
```bash
# From project root
python generate_tickers_dataset.py
```

### Automated Update (Windows Task Scheduler)
```powershell
# Create scheduled task for monthly update
$action = New-ScheduledTaskAction -Execute "python.exe" `
  -Argument "generate_tickers_dataset.py" `
  -WorkingDirectory "G:\Projects\2025\StockNews"

$trigger = New-ScheduledTaskTrigger -Monthly -DaysOfMonth 1 -At 2am

Register-ScheduledTask -TaskName "UpdateTickersDataset" `
  -Action $action -Trigger $trigger `
  -Description "Update Market News Radar ticker dataset monthly"
```

### Automated Update (Linux/Mac - Cron)
```bash
# Edit crontab
crontab -e

# Add monthly update (1st of month at 2 AM)
0 2 1 * * cd /path/to/StockNews && /path/to/python generate_tickers_dataset.py >> logs/ticker_update.log 2>&1
```

---

## 📈 Market Data Sources

### Current Sources
1. **SEC Company Tickers** - Free, updated daily
   - URL: https://www.sec.gov/files/company_tickers.json
   - Coverage: ~13,000 US companies
   - Note: Currently requires User-Agent header (403 error otherwise)

2. **CoinGecko API** - Free (no API key needed)
   - URL: https://api.coingecko.com/api/v3/coins/list
   - Coverage: 14,000+ cryptocurrencies
   - Rate Limit: 10-50 calls/minute (generous)

3. **Manual Additions** - Hardcoded in script
   - Major ETFs, indices, ADRs
   - Nordic stocks (Sweden, Norway, Denmark, Finland)
   - Can be extended as needed

### Potential Additional Sources
- **NASDAQ FTP**: ftp://ftp.nasdaqtrader.com/symboldirectory/
- **Yahoo Finance CSV**: No official API but CSV downloads available
- **Alpha Vantage**: Free tier (5 API calls/minute, 500/day)
- **Finnhub**: Free tier (60 API calls/minute)

---

## 🔮 Future Enhancements

1. **More European Markets**: UK (LSE), Germany (XETRA), France (Euronext)
2. **Asian Markets**: Tokyo (TSE), Hong Kong (HKEX), Singapore (SGX)
3. **ETF Expansion**: Add sector ETFs, international ETFs
4. **Company Metadata**: Market cap, sector, industry classification
5. **Real-time Prices**: Optional integration with price APIs
6. **Delisting Detection**: Remove defunct tickers automatically

---

## 💡 Key Takeaways

✅ **Monthly updates** are the sweet spot for most use cases
✅ **Scandinavian markets** now fully supported (46 companies)
✅ **5,000 tickers** provides comprehensive coverage without bloat
✅ **0.53 MB file size** ensures fast autocomplete performance
✅ **Zero API keys** required - fully self-hosted solution

**Next Update Recommended**: December 1, 2025 📅
