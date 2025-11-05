"""
Test script to verify company name matching logic works correctly.
This script tests the enhanced ticker detection with company name mappings.
"""
import sys
sys.path.insert(0, 'backend')

from backend.scraper import calculate_score, COMPANY_TO_TICKER

def test_company_matching():
    """Test that company names are properly matched to tickers."""
    
    # Test data
    test_cases = [
        {
            "text": "Apple announced record quarterly earnings today.",
            "expected_ticker": "AAPL",
            "description": "Apple mentioned in article"
        },
        {
            "text": "Tesla CEO Elon Musk announced new factory plans.",
            "expected_ticker": "TSLA", 
            "description": "Tesla mentioned in article"
        },
        {
            "text": "Microsoft and Google are competing in AI space.",
            "expected_tickers": ["MSFT", "GOOGL"],
            "description": "Multiple companies mentioned"
        },
        {
            "text": "Bitcoin hit a new all-time high today.",
            "expected_ticker": "BTC",
            "description": "Bitcoin mentioned (crypto)"
        },
        {
            "text": "Netflix subscriber growth exceeded expectations.",
            "expected_ticker": "NFLX",
            "description": "Netflix mentioned"
        },
        {
            "text": "The S&P 500 index reached record levels.",
            "expected_ticker": "SPY",
            "description": "S&P 500 mentioned"
        },
        {
            "text": "Meta Platforms (formerly Facebook) reported earnings.",
            "expected_ticker": "META",
            "description": "Meta/Facebook mentioned"
        },
        {
            "text": "NVIDIA stock surged on AI chip demand.",
            "expected_ticker": "NVDA",
            "description": "NVIDIA mentioned (ticker in text)"
        }
    ]
    
    # Mock database company mappings
    db_company_mapping = {
        'apple': 'AAPL',
        'apple inc': 'AAPL',
        'microsoft': 'MSFT',
        'microsoft corp': 'MSFT',
        'google': 'GOOGL',
        'alphabet': 'GOOGL',
        'alphabet inc': 'GOOGL',
        'amazon': 'AMZN',
        'amazon.com': 'AMZN',
        'tesla': 'TSLA',
        'tesla inc': 'TSLA',
        'meta': 'META',
        'facebook': 'META',
        'meta platforms': 'META',
        'nvidia': 'NVDA',
        'nvidia corp': 'NVDA',
        'bitcoin': 'BTC',
        'btc': 'BTC',
        'ethereum': 'ETH',
        'eth': 'ETH',
        'netflix': 'NFLX',
        'netflix inc': 'NFLX',
        's&p 500': 'SPY',
        's&p': 'SPY',
        'spdr': 'SPY'
    }
    
    # Merge static and dynamic mappings (simulating scraper logic)
    active_company_mapping = {**COMPANY_TO_TICKER, **db_company_mapping}
    
    print("=" * 80)
    print("COMPANY NAME MATCHING TEST SUITE")
    print("=" * 80)
    print(f"\nTotal company mappings available: {len(active_company_mapping)}")
    print(f"  - Static mappings: {len(COMPANY_TO_TICKER)}")
    print(f"  - Database mappings: {len(db_company_mapping)}")
    print("\n" + "-" * 80)
    
    passed = 0
    failed = 0
    
    for i, test in enumerate(test_cases, 1):
        text = test["text"]
        description = test["description"]
        
        # Get all possible tickers to check against
        all_tickers = list(set(active_company_mapping.values()))
        
        # Calculate score (which includes company name matching)
        score, matched_tickers = calculate_score(
            text=text,
            tickers=all_tickers,  # Pass all tickers for matching
            keywords=[],
            strong_words=[],
            company_mapping=active_company_mapping
        )
        
        # Check if expected ticker(s) were found
        if "expected_tickers" in test:
            expected = set(test["expected_tickers"])
            found = set(matched_tickers)
            success = expected.issubset(found)
        else:
            expected = test["expected_ticker"]
            success = expected in matched_tickers
        
        status = "✓ PASS" if success else "✗ FAIL"
        
        if success:
            passed += 1
        else:
            failed += 1
        
        print(f"\nTest {i}: {status}")
        print(f"  Description: {description}")
        print(f"  Text: \"{text}\"")
        print(f"  Expected: {test.get('expected_ticker') or test.get('expected_tickers')}")
        print(f"  Found: {matched_tickers if matched_tickers else 'None'}")
        print(f"  Score: {score}")
    
    print("\n" + "=" * 80)
    print(f"TEST RESULTS: {passed} passed, {failed} failed out of {len(test_cases)} tests")
    print("=" * 80)
    
    return failed == 0

def show_available_mappings():
    """Display all available company-to-ticker mappings."""
    print("\n" + "=" * 80)
    print("AVAILABLE COMPANY NAME MAPPINGS (Static)")
    print("=" * 80)
    
    # Group by ticker
    ticker_to_companies = {}
    for company, ticker in COMPANY_TO_TICKER.items():
        if ticker not in ticker_to_companies:
            ticker_to_companies[ticker] = []
        ticker_to_companies[ticker].append(company)
    
    for ticker in sorted(ticker_to_companies.keys()):
        companies = ", ".join(sorted(ticker_to_companies[ticker]))
        print(f"  {ticker:6} <- {companies}")
    
    print(f"\nTotal: {len(COMPANY_TO_TICKER)} company name variations mapping to {len(ticker_to_companies)} tickers")
    print("=" * 80)

if __name__ == "__main__":
    print("\n🔍 Testing Company Name Matching Feature\n")
    
    # Show available mappings
    show_available_mappings()
    
    # Run tests
    success = test_company_matching()
    
    if success:
        print("\n✅ All tests passed! Company name matching is working correctly.")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed. Check the output above for details.")
        sys.exit(1)
