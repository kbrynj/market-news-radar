#!/usr/bin/env python3
"""
Generate comprehensive tickers dataset from free sources.
Run this script periodically to update the ticker database.

Sources:
- SEC Company Tickers (US stocks) - ~13,000 companies
- Scandinavian Markets (Nordic stocks) - Major companies from SE, NO, DK, FI  
- CoinGecko API (cryptocurrencies) - 14,000+ coins
- Manual additions (ETFs, indices, popular tickers)

Update Frequency Recommendations:
====================================
📅 NEW LISTINGS / IPOs
   - Run monthly to catch new companies going public
   - US: ~10-20 IPOs per month
   - Crypto: 50-100 new tokens per month
   
💰 CRYPTO MARKETS  
   - Run weekly (very dynamic, new tokens constantly)
   - CoinGecko adds ~100+ new coins weekly
   
📊 STOCK MARKETS
   - Run quarterly for major markets (US, Europe)
   - Delistings and ticker changes are rare
   - Annual update sufficient if focused only on established companies

⚡ RECOMMENDED SCHEDULE
   - Production: Run monthly (good balance)
   - Crypto-focused: Run weekly
   - Conservative: Run quarterly
"""
import aiohttp
import asyncio
import json
from typing import List, Dict

# Manual additions for important tickers
MANUAL_TICKERS = [
    # Major ETFs
    {"symbol": "SPY", "name": "SPDR S&P 500 ETF Trust", "type": "ETF", "exchange": "NYSE"},
    {"symbol": "QQQ", "name": "Invesco QQQ Trust", "type": "ETF", "exchange": "NASDAQ"},
    {"symbol": "DIA", "name": "SPDR Dow Jones Industrial Average ETF", "type": "ETF", "exchange": "NYSE"},
    {"symbol": "IWM", "name": "iShares Russell 2000 ETF", "type": "ETF", "exchange": "NYSE"},
    {"symbol": "VTI", "name": "Vanguard Total Stock Market ETF", "type": "ETF", "exchange": "NYSE"},
    {"symbol": "VOO", "name": "Vanguard S&P 500 ETF", "type": "ETF", "exchange": "NYSE"},
    {"symbol": "GLD", "name": "SPDR Gold Trust", "type": "ETF", "exchange": "NYSE"},
    {"symbol": "SLV", "name": "iShares Silver Trust", "type": "ETF", "exchange": "NYSE"},
    {"symbol": "TLT", "name": "iShares 20+ Year Treasury Bond ETF", "type": "ETF", "exchange": "NASDAQ"},
    {"symbol": "VIX", "name": "CBOE Volatility Index", "type": "INDEX", "exchange": "CBOE"},
    
    # Popular International ADRs
    {"symbol": "BABA", "name": "Alibaba Group Holding", "type": "STOCK", "exchange": "NYSE"},
    {"symbol": "NIO", "name": "NIO Inc", "type": "STOCK", "exchange": "NYSE"},
    {"symbol": "TSM", "name": "Taiwan Semiconductor Manufacturing", "type": "STOCK", "exchange": "NYSE"},
]


async def fetch_sec_tickers() -> List[Dict]:
    """Fetch US company tickers from SEC."""
    print("📊 Fetching SEC company tickers...")
    url = "https://www.sec.gov/files/company_tickers.json"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, headers=headers, timeout=30) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # SEC format: {0: {cik_str, ticker, title}, 1: {...}, ...}
                    tickers = []
                    for item in data.values():
                        tickers.append({
                            "symbol": item["ticker"].upper(),
                            "name": item["title"],
                            "type": "STOCK",
                            "exchange": "US"
                        })
                    
                    print(f"  ✅ Found {len(tickers)} US stocks")
                    return tickers
                else:
                    print(f"  ⚠️  Failed to fetch SEC data: HTTP {response.status}")
                    print(f"  ℹ️  Using manual stock list as fallback...")
                    return get_fallback_stocks()
        except Exception as e:
            print(f"  ⚠️  Error fetching SEC data: {e}")
            print(f"  ℹ️  Using manual stock list as fallback...")
            return get_fallback_stocks()


def get_fallback_stocks() -> List[Dict]:
    """Fallback list of major US stocks if SEC API fails."""
    return [
        # Tech
        {"symbol": "AAPL", "name": "Apple Inc", "type": "STOCK", "exchange": "NASDAQ"},
        {"symbol": "MSFT", "name": "Microsoft Corporation", "type": "STOCK", "exchange": "NASDAQ"},
        {"symbol": "GOOGL", "name": "Alphabet Inc Class A", "type": "STOCK", "exchange": "NASDAQ"},
        {"symbol": "GOOG", "name": "Alphabet Inc Class C", "type": "STOCK", "exchange": "NASDAQ"},
        {"symbol": "AMZN", "name": "Amazon.com Inc", "type": "STOCK", "exchange": "NASDAQ"},
        {"symbol": "META", "name": "Meta Platforms Inc", "type": "STOCK", "exchange": "NASDAQ"},
        {"symbol": "TSLA", "name": "Tesla Inc", "type": "STOCK", "exchange": "NASDAQ"},
        {"symbol": "NVDA", "name": "NVIDIA Corporation", "type": "STOCK", "exchange": "NASDAQ"},
        {"symbol": "NFLX", "name": "Netflix Inc", "type": "STOCK", "exchange": "NASDAQ"},
        {"symbol": "AMD", "name": "Advanced Micro Devices Inc", "type": "STOCK", "exchange": "NASDAQ"},
        {"symbol": "INTC", "name": "Intel Corporation", "type": "STOCK", "exchange": "NASDAQ"},
        {"symbol": "CRM", "name": "Salesforce Inc", "type": "STOCK", "exchange": "NYSE"},
        {"symbol": "ORCL", "name": "Oracle Corporation", "type": "STOCK", "exchange": "NYSE"},
        {"symbol": "ADBE", "name": "Adobe Inc", "type": "STOCK", "exchange": "NASDAQ"},
        {"symbol": "CSCO", "name": "Cisco Systems Inc", "type": "STOCK", "exchange": "NASDAQ"},
        {"symbol": "IBM", "name": "International Business Machines", "type": "STOCK", "exchange": "NYSE"},
        {"symbol": "QCOM", "name": "QUALCOMM Inc", "type": "STOCK", "exchange": "NASDAQ"},
        {"symbol": "TXN", "name": "Texas Instruments Inc", "type": "STOCK", "exchange": "NASDAQ"},
        {"symbol": "AVGO", "name": "Broadcom Inc", "type": "STOCK", "exchange": "NASDAQ"},
        
        # Finance
        {"symbol": "JPM", "name": "JPMorgan Chase & Co", "type": "STOCK", "exchange": "NYSE"},
        {"symbol": "BAC", "name": "Bank of America Corp", "type": "STOCK", "exchange": "NYSE"},
        {"symbol": "WFC", "name": "Wells Fargo & Company", "type": "STOCK", "exchange": "NYSE"},
        {"symbol": "GS", "name": "Goldman Sachs Group Inc", "type": "STOCK", "exchange": "NYSE"},
        {"symbol": "MS", "name": "Morgan Stanley", "type": "STOCK", "exchange": "NYSE"},
        {"symbol": "C", "name": "Citigroup Inc", "type": "STOCK", "exchange": "NYSE"},
        {"symbol": "BRK.A", "name": "Berkshire Hathaway Inc Class A", "type": "STOCK", "exchange": "NYSE"},
        {"symbol": "BRK.B", "name": "Berkshire Hathaway Inc Class B", "type": "STOCK", "exchange": "NYSE"},
        {"symbol": "V", "name": "Visa Inc", "type": "STOCK", "exchange": "NYSE"},
        {"symbol": "MA", "name": "Mastercard Inc", "type": "STOCK", "exchange": "NYSE"},
        {"symbol": "AXP", "name": "American Express Company", "type": "STOCK", "exchange": "NYSE"},
        {"symbol": "BLK", "name": "BlackRock Inc", "type": "STOCK", "exchange": "NYSE"},
        {"symbol": "SCHW", "name": "Charles Schwab Corporation", "type": "STOCK", "exchange": "NYSE"},
        
        # Healthcare
        {"symbol": "JNJ", "name": "Johnson & Johnson", "type": "STOCK", "exchange": "NYSE"},
        {"symbol": "UNH", "name": "UnitedHealth Group Inc", "type": "STOCK", "exchange": "NYSE"},
        {"symbol": "PFE", "name": "Pfizer Inc", "type": "STOCK", "exchange": "NYSE"},
        {"symbol": "ABBV", "name": "AbbVie Inc", "type": "STOCK", "exchange": "NYSE"},
        {"symbol": "LLY", "name": "Eli Lilly and Company", "type": "STOCK", "exchange": "NYSE"},
        {"symbol": "MRK", "name": "Merck & Co Inc", "type": "STOCK", "exchange": "NYSE"},
        {"symbol": "TMO", "name": "Thermo Fisher Scientific Inc", "type": "STOCK", "exchange": "NYSE"},
        {"symbol": "ABT", "name": "Abbott Laboratories", "type": "STOCK", "exchange": "NYSE"},
        {"symbol": "DHR", "name": "Danaher Corporation", "type": "STOCK", "exchange": "NYSE"},
        {"symbol": "BMY", "name": "Bristol-Myers Squibb Company", "type": "STOCK", "exchange": "NYSE"},
        {"symbol": "AMGN", "name": "Amgen Inc", "type": "STOCK", "exchange": "NASDAQ"},
        {"symbol": "GILD", "name": "Gilead Sciences Inc", "type": "STOCK", "exchange": "NASDAQ"},
        
        # Consumer
        {"symbol": "WMT", "name": "Walmart Inc", "type": "STOCK", "exchange": "NYSE"},
        {"symbol": "HD", "name": "Home Depot Inc", "type": "STOCK", "exchange": "NYSE"},
        {"symbol": "COST", "name": "Costco Wholesale Corporation", "type": "STOCK", "exchange": "NASDAQ"},
        {"symbol": "PG", "name": "Procter & Gamble Company", "type": "STOCK", "exchange": "NYSE"},
        {"symbol": "KO", "name": "Coca-Cola Company", "type": "STOCK", "exchange": "NYSE"},
        {"symbol": "PEP", "name": "PepsiCo Inc", "type": "STOCK", "exchange": "NASDAQ"},
        {"symbol": "NKE", "name": "NIKE Inc", "type": "STOCK", "exchange": "NYSE"},
        {"symbol": "MCD", "name": "McDonald's Corporation", "type": "STOCK", "exchange": "NYSE"},
        {"symbol": "SBUX", "name": "Starbucks Corporation", "type": "STOCK", "exchange": "NASDAQ"},
        {"symbol": "DIS", "name": "Walt Disney Company", "type": "STOCK", "exchange": "NYSE"},
        {"symbol": "TGT", "name": "Target Corporation", "type": "STOCK", "exchange": "NYSE"},
        {"symbol": "LOW", "name": "Lowe's Companies Inc", "type": "STOCK", "exchange": "NYSE"},
        
        # Energy
        {"symbol": "XOM", "name": "Exxon Mobil Corporation", "type": "STOCK", "exchange": "NYSE"},
        {"symbol": "CVX", "name": "Chevron Corporation", "type": "STOCK", "exchange": "NYSE"},
        {"symbol": "COP", "name": "ConocoPhillips", "type": "STOCK", "exchange": "NYSE"},
        {"symbol": "SLB", "name": "Schlumberger NV", "type": "STOCK", "exchange": "NYSE"},
        {"symbol": "EOG", "name": "EOG Resources Inc", "type": "STOCK", "exchange": "NYSE"},
        {"symbol": "PXD", "name": "Pioneer Natural Resources Company", "type": "STOCK", "exchange": "NYSE"},
        
        # Industrial
        {"symbol": "BA", "name": "Boeing Company", "type": "STOCK", "exchange": "NYSE"},
        {"symbol": "CAT", "name": "Caterpillar Inc", "type": "STOCK", "exchange": "NYSE"},
        {"symbol": "GE", "name": "General Electric Company", "type": "STOCK", "exchange": "NYSE"},
        {"symbol": "MMM", "name": "3M Company", "type": "STOCK", "exchange": "NYSE"},
        {"symbol": "HON", "name": "Honeywell International Inc", "type": "STOCK", "exchange": "NASDAQ"},
        {"symbol": "UPS", "name": "United Parcel Service Inc", "type": "STOCK", "exchange": "NYSE"},
        {"symbol": "RTX", "name": "Raytheon Technologies Corporation", "type": "STOCK", "exchange": "NYSE"},
        {"symbol": "LMT", "name": "Lockheed Martin Corporation", "type": "STOCK", "exchange": "NYSE"},
        
        # Telecom
        {"symbol": "T", "name": "AT&T Inc", "type": "STOCK", "exchange": "NYSE"},
        {"symbol": "VZ", "name": "Verizon Communications Inc", "type": "STOCK", "exchange": "NYSE"},
        {"symbol": "TMUS", "name": "T-Mobile US Inc", "type": "STOCK", "exchange": "NASDAQ"},
        {"symbol": "CMCSA", "name": "Comcast Corporation", "type": "STOCK", "exchange": "NASDAQ"},
        
        # Auto
        {"symbol": "F", "name": "Ford Motor Company", "type": "STOCK", "exchange": "NYSE"},
        {"symbol": "GM", "name": "General Motors Company", "type": "STOCK", "exchange": "NYSE"},
        
        # Payments/Fintech  
        {"symbol": "PYPL", "name": "PayPal Holdings Inc", "type": "STOCK", "exchange": "NASDAQ"},
        {"symbol": "SQ", "name": "Block Inc", "type": "STOCK", "exchange": "NYSE"},
        {"symbol": "COIN", "name": "Coinbase Global Inc", "type": "STOCK", "exchange": "NASDAQ"},
    ]


async def fetch_scandinavian_tickers() -> List[Dict]:
    """Fetch major Scandinavian market tickers."""
    print("🇸🇪 🇳🇴 🇩🇰 🇫🇮 Fetching Scandinavian market tickers...")
    
    # Major companies from Nordic exchanges
    # Note: Ticker format includes exchange suffix (.ST, .OL, .CO, .HE)
    nordic_stocks = [
        # 🇸🇪 Sweden - Nasdaq Stockholm (.ST)
        {"symbol": "VOLV-B.ST", "name": "Volvo AB", "type": "STOCK", "exchange": "Stockholm"},
        {"symbol": "ERIC-B.ST", "name": "Ericsson", "type": "STOCK", "exchange": "Stockholm"},
        {"symbol": "SEB-A.ST", "name": "Skandinaviska Enskilda Banken", "type": "STOCK", "exchange": "Stockholm"},
        {"symbol": "SWED-A.ST", "name": "Swedbank", "type": "STOCK", "exchange": "Stockholm"},
        {"symbol": "HM-B.ST", "name": "H&M Hennes & Mauritz", "type": "STOCK", "exchange": "Stockholm"},
        {"symbol": "SAND.ST", "name": "Sandvik", "type": "STOCK", "exchange": "Stockholm"},
        {"symbol": "ABB.ST", "name": "ABB Ltd", "type": "STOCK", "exchange": "Stockholm"},
        {"symbol": "ATCO-A.ST", "name": "Atlas Copco", "type": "STOCK", "exchange": "Stockholm"},
        {"symbol": "ALFA.ST", "name": "Alfa Laval", "type": "STOCK", "exchange": "Stockholm"},
        {"symbol": "ESSITY-B.ST", "name": "Essity", "type": "STOCK", "exchange": "Stockholm"},
        {"symbol": "TELIA.ST", "name": "Telia Company", "type": "STOCK", "exchange": "Stockholm"},
        {"symbol": "SKF-B.ST", "name": "SKF", "type": "STOCK", "exchange": "Stockholm"},
        {"symbol": "ELUX-B.ST", "name": "Electrolux", "type": "STOCK", "exchange": "Stockholm"},
        {"symbol": "HEXA-B.ST", "name": "Hexagon", "type": "STOCK", "exchange": "Stockholm"},
        {"symbol": "INVE-B.ST", "name": "Investor", "type": "STOCK", "exchange": "Stockholm"},
        {"symbol": "AZN.ST", "name": "AstraZeneca", "type": "STOCK", "exchange": "Stockholm"},
        
        # 🇳🇴 Norway - Oslo Børs (.OL)
        {"symbol": "EQNR.OL", "name": "Equinor", "type": "STOCK", "exchange": "Oslo"},
        {"symbol": "DNB.OL", "name": "DNB Bank", "type": "STOCK", "exchange": "Oslo"},
        {"symbol": "MOWI.OL", "name": "Mowi", "type": "STOCK", "exchange": "Oslo"},
        {"symbol": "TEL.OL", "name": "Telenor", "type": "STOCK", "exchange": "Oslo"},
        {"symbol": "YAR.OL", "name": "Yara International", "type": "STOCK", "exchange": "Oslo"},
        {"symbol": "ORK.OL", "name": "Orkla", "type": "STOCK", "exchange": "Oslo"},
        {"symbol": "SALM.OL", "name": "SalMar", "type": "STOCK", "exchange": "Oslo"},
        {"symbol": "NHY.OL", "name": "Norsk Hydro", "type": "STOCK", "exchange": "Oslo"},
        {"symbol": "AKRBP.OL", "name": "Aker BP", "type": "STOCK", "exchange": "Oslo"},
        {"symbol": "SCATC.OL", "name": "Scatec", "type": "STOCK", "exchange": "Oslo"},
        
        # 🇩🇰 Denmark - Nasdaq Copenhagen (.CO)
        {"symbol": "NOVO-B.CO", "name": "Novo Nordisk", "type": "STOCK", "exchange": "Copenhagen"},
        {"symbol": "MAERSK-B.CO", "name": "A.P. Moller - Maersk", "type": "STOCK", "exchange": "Copenhagen"},
        {"symbol": "ORSTED.CO", "name": "Ørsted", "type": "STOCK", "exchange": "Copenhagen"},
        {"symbol": "DANSKE.CO", "name": "Danske Bank", "type": "STOCK", "exchange": "Copenhagen"},
        {"symbol": "CARLB.CO", "name": "Carlsberg", "type": "STOCK", "exchange": "Copenhagen"},
        {"symbol": "VWS.CO", "name": "Vestas Wind Systems", "type": "STOCK", "exchange": "Copenhagen"},
        {"symbol": "COLO-B.CO", "name": "Coloplast", "type": "STOCK", "exchange": "Copenhagen"},
        {"symbol": "DSV.CO", "name": "DSV", "type": "STOCK", "exchange": "Copenhagen"},
        {"symbol": "TRYG.CO", "name": "Tryg", "type": "STOCK", "exchange": "Copenhagen"},
        {"symbol": "JYSK.CO", "name": "Jyske Bank", "type": "STOCK", "exchange": "Copenhagen"},
        
        # 🇫🇮 Finland - Nasdaq Helsinki (.HE)
        {"symbol": "NOKIA.HE", "name": "Nokia", "type": "STOCK", "exchange": "Helsinki"},
        {"symbol": "NESTE.HE", "name": "Neste", "type": "STOCK", "exchange": "Helsinki"},
        {"symbol": "FORTUM.HE", "name": "Fortum", "type": "STOCK", "exchange": "Helsinki"},
        {"symbol": "SAMPO.HE", "name": "Sampo", "type": "STOCK", "exchange": "Helsinki"},
        {"symbol": "UPM.HE", "name": "UPM-Kymmene", "type": "STOCK", "exchange": "Helsinki"},
        {"symbol": "STERV.HE", "name": "Stora Enso", "type": "STOCK", "exchange": "Helsinki"},
        {"symbol": "KNEBV.HE", "name": "KONE", "type": "STOCK", "exchange": "Helsinki"},
        {"symbol": "WRT1V.HE", "name": "Wärtsilä", "type": "STOCK", "exchange": "Helsinki"},
        {"symbol": "ELISA.HE", "name": "Elisa", "type": "STOCK", "exchange": "Helsinki"},
        {"symbol": "METSO.HE", "name": "Metso Outotec", "type": "STOCK", "exchange": "Helsinki"},
    ]
    
    print(f"  ✅ Added {len(nordic_stocks)} Scandinavian stocks")
    return nordic_stocks


async def fetch_crypto_tickers() -> List[Dict]:
    """Fetch cryptocurrency tickers from CoinGecko."""
    print("💰 Fetching cryptocurrency tickers...")
    url = "https://api.coingecko.com/api/v3/coins/list"
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, timeout=30) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    tickers = []
                    seen_symbols = set()
                    
                    for coin in data:
                        symbol = coin["symbol"].upper()
                        
                        # Skip duplicates and very obscure coins
                        if symbol in seen_symbols or len(symbol) > 10:
                            continue
                        
                        seen_symbols.add(symbol)
                        tickers.append({
                            "symbol": symbol,
                            "name": coin["name"],
                            "type": "CRYPTO",
                            "exchange": "CRYPTO"
                        })
                    
                    print(f"  ✅ Found {len(tickers)} cryptocurrencies")
                    return tickers
                else:
                    print(f"  ❌ Failed to fetch crypto data: HTTP {response.status}")
                    return []
        except Exception as e:
            print(f"  ❌ Error fetching crypto data: {e}")
            return []


def deduplicate_tickers(tickers: List[Dict]) -> List[Dict]:
    """Remove duplicate tickers, keeping the most relevant entry."""
    print("🔄 Deduplicating tickers...")
    
    # Group by symbol
    symbol_map = {}
    for ticker in tickers:
        symbol = ticker["symbol"]
        
        if symbol not in symbol_map:
            symbol_map[symbol] = ticker
        else:
            # Prefer: STOCK > ETF > CRYPTO > others
            existing = symbol_map[symbol]
            priority = {"STOCK": 0, "ETF": 1, "CRYPTO": 2, "INDEX": 3}
            
            existing_priority = priority.get(existing["type"], 10)
            new_priority = priority.get(ticker["type"], 10)
            
            if new_priority < existing_priority:
                symbol_map[symbol] = ticker
    
    result = list(symbol_map.values())
    print(f"  ✅ {len(result)} unique tickers (removed {len(tickers) - len(result)} duplicates)")
    return result


def optimize_dataset(tickers: List[Dict], max_entries: int = 5000) -> List[Dict]:
    """
    Optimize dataset size by keeping most relevant tickers.
    Priority: Major stocks, ETFs, crypto, then others.
    """
    print(f"⚡ Optimizing dataset (target: {max_entries} entries)...")
    
    # Known major companies and popular tickers
    priority_symbols = {
        # FAANG+
        "AAPL", "MSFT", "GOOGL", "GOOG", "AMZN", "META", "NVDA", "TSLA",
        # Tech giants
        "NFLX", "AMD", "INTC", "CRM", "ORCL", "ADBE", "CSCO", "IBM",
        # Finance
        "JPM", "BAC", "WFC", "GS", "MS", "C", "BRK.A", "BRK.B", "V", "MA",
        # Healthcare
        "JNJ", "PFE", "UNH", "ABBV", "LLY", "MRK", "TMO", "ABT",
        # Consumer
        "WMT", "HD", "COST", "NKE", "SBUX", "MCD", "DIS", "KO", "PEP",
        # Energy
        "XOM", "CVX", "COP", "SLB",
        # ETFs
        "SPY", "QQQ", "DIA", "IWM", "VTI", "VOO", "GLD", "SLV", "TLT",
        # Crypto
        "BTC", "ETH", "USDT", "BNB", "XRP", "ADA", "SOL", "DOGE", "DOT", "MATIC",
        # Scandinavian - Major companies
        "NOKIA.HE", "NOVO-B.CO", "EQNR.OL", "VOLV-B.ST", "ERIC-B.ST", 
        "MAERSK-B.CO", "ORSTED.CO", "NESTE.HE", "HM-B.ST", "DNB.OL",
    }
    
    # Separate into priority and others
    priority = []
    regular = []
    
    for ticker in tickers:
        if ticker["symbol"] in priority_symbols or ticker["type"] in ["ETF", "INDEX"]:
            priority.append(ticker)
        else:
            regular.append(ticker)
    
    # Sort regular by symbol (alphabetical) for easier searching
    regular.sort(key=lambda x: x["symbol"])
    
    # Take all priority + as many regular as fit
    if len(priority) + len(regular) <= max_entries:
        result = priority + regular
    else:
        result = priority + regular[:max_entries - len(priority)]
    
    print(f"  ✅ Final dataset: {len(result)} tickers ({len(priority)} priority, {len(result) - len(priority)} regular)")
    return result


async def generate_dataset():
    """Main function to generate the ticker dataset."""
    print("=" * 80)
    print("Generating Comprehensive Ticker Dataset")
    print("=" * 80)
    
    # Fetch from all sources
    all_tickers = []
    
    # SEC US stocks
    sec_tickers = await fetch_sec_tickers()
    all_tickers.extend(sec_tickers)
    
    # Scandinavian markets
    nordic_tickers = await fetch_scandinavian_tickers()
    all_tickers.extend(nordic_tickers)
    
    # Crypto
    crypto_tickers = await fetch_crypto_tickers()
    all_tickers.extend(crypto_tickers)
    
    # Manual additions
    print(f"➕ Adding {len(MANUAL_TICKERS)} manual entries (ETFs, indices)...")
    all_tickers.extend(MANUAL_TICKERS)
    
    print(f"\n📦 Total tickers collected: {len(all_tickers)}")
    
    # Deduplicate
    unique_tickers = deduplicate_tickers(all_tickers)
    
    # Optimize size
    optimized = optimize_dataset(unique_tickers, max_entries=5000)
    
    # Sort alphabetically for easier searching
    optimized.sort(key=lambda x: x["symbol"])
    
    # Save to file
    output_file = "backend/tickers.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(optimized, f, indent=2, ensure_ascii=False)
    
    # Calculate file size
    import os
    file_size = os.path.getsize(output_file) / (1024 * 1024)  # MB
    
    print("\n" + "=" * 80)
    print(f"✅ SUCCESS!")
    print(f"   File: {output_file}")
    print(f"   Size: {file_size:.2f} MB")
    print(f"   Tickers: {len(optimized)}")
    print("=" * 80)
    
    # Print sample
    print("\n📋 Sample entries:")
    for ticker in optimized[:10]:
        print(f"   {ticker['symbol']:15} - {ticker['name'][:50]:50} ({ticker['type']})")
    
    # Print breakdown by type
    stocks = sum(1 for t in optimized if t['type'] == 'STOCK')
    etfs = sum(1 for t in optimized if t['type'] == 'ETF')
    cryptos = sum(1 for t in optimized if t['type'] == 'CRYPTO')
    indexes = sum(1 for t in optimized if t['type'] == 'INDEX')
    
    print("\n📊 Dataset breakdown:")
    print(f"   Stocks: {stocks}")
    print(f"   ETFs: {etfs}")
    print(f"   Indexes: {indexes}")
    print(f"   Cryptos: {cryptos}")
    
    return optimized


if __name__ == "__main__":
    asyncio.run(generate_dataset())
