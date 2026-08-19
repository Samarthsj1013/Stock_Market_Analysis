NIFTY50_STOCKS = {
    # IT
    "TCS.NS":           {"name": "Tata Consultancy Services", "sector": "IT"},
    "INFY.NS":          {"name": "Infosys",                   "sector": "IT"},
    "WIPRO.NS":         {"name": "Wipro",                     "sector": "IT"},
    "HCLTECH.NS":       {"name": "HCL Technologies",          "sector": "IT"},
    "TECHM.NS":         {"name": "Tech Mahindra",             "sector": "IT"},

    # Banking & Finance
    "HDFCBANK.NS":      {"name": "HDFC Bank",                 "sector": "Banking"},
    "ICICIBANK.NS":     {"name": "ICICI Bank",                "sector": "Banking"},
    "KOTAKBANK.NS":     {"name": "Kotak Mahindra Bank",       "sector": "Banking"},
    "AXISBANK.NS":      {"name": "Axis Bank",                 "sector": "Banking"},
    "SBIN.NS":          {"name": "State Bank of India",       "sector": "Banking"},
    "BAJFINANCE.NS":    {"name": "Bajaj Finance",             "sector": "Banking"},
    "BAJAJFINSV.NS":    {"name": "Bajaj Finserv",             "sector": "Banking"},

    # Oil & Energy
    "RELIANCE.NS":      {"name": "Reliance Industries",       "sector": "Energy"},
    "ONGC.NS":          {"name": "ONGC",                      "sector": "Energy"},
    "BPCL.NS":          {"name": "BPCL",                      "sector": "Energy"},
    "POWERGRID.NS":     {"name": "Power Grid Corporation",    "sector": "Energy"},
    "NTPC.NS":          {"name": "NTPC",                      "sector": "Energy"},

    # Auto
    "MARUTI.NS":        {"name": "Maruti Suzuki",             "sector": "Auto"},
    "TATAMOTORS.NS":    {"name": "Tata Motors",               "sector": "Auto"},
    "M&M.NS":           {"name": "Mahindra & Mahindra",       "sector": "Auto"},
    "EICHERMOT.NS":     {"name": "Eicher Motors",             "sector": "Auto"},
    "HEROMOTOCO.NS":    {"name": "Hero MotoCorp",             "sector": "Auto"},

    # Pharma
    "SUNPHARMA.NS":     {"name": "Sun Pharmaceutical",        "sector": "Pharma"},
    "DRREDDY.NS":       {"name": "Dr. Reddy's Laboratories",  "sector": "Pharma"},
    "CIPLA.NS":         {"name": "Cipla",                     "sector": "Pharma"},
    "DIVISLAB.NS":      {"name": "Divi's Laboratories",       "sector": "Pharma"},

    # FMCG
    "HINDUNILVR.NS":    {"name": "Hindustan Unilever",        "sector": "FMCG"},
    "ITC.NS":           {"name": "ITC",                       "sector": "FMCG"},
    "NESTLEIND.NS":     {"name": "Nestle India",              "sector": "FMCG"},
    "BRITANNIA.NS":     {"name": "Britannia Industries",      "sector": "FMCG"},

    # Metals & Mining
    "TATASTEEL.NS":     {"name": "Tata Steel",                "sector": "Metals"},
    "JSWSTEEL.NS":      {"name": "JSW Steel",                 "sector": "Metals"},
    "HINDALCO.NS":      {"name": "Hindalco Industries",       "sector": "Metals"},
    "COALINDIA.NS":     {"name": "Coal India",                "sector": "Metals"},

    # Telecom
    "BHARTIARTL.NS":    {"name": "Bharti Airtel",             "sector": "Telecom"},

    # Infrastructure & Construction
    "LARSENTOUBRO.NS":  {"name": "Larsen & Toubro",           "sector": "Infrastructure"},
    "ULTRACEMCO.NS":    {"name": "UltraTech Cement",          "sector": "Infrastructure"},
    "GRASIM.NS":        {"name": "Grasim Industries",         "sector": "Infrastructure"},
    "ADANIENT.NS":      {"name": "Adani Enterprises",         "sector": "Infrastructure"},
    "ADANIPORTS.NS":    {"name": "Adani Ports",               "sector": "Infrastructure"},

    # Consumer & Retail
    "TITAN.NS":         {"name": "Titan Company",             "sector": "Consumer"},
    "ASIANPAINT.NS":    {"name": "Asian Paints",              "sector": "Consumer"},
    "BAJAJ-AUTO.NS":    {"name": "Bajaj Auto",                "sector": "Consumer"},

    # Financial Services
    "HDFCLIFE.NS":      {"name": "HDFC Life Insurance",       "sector": "Finance"},
    "SBILIFE.NS":       {"name": "SBI Life Insurance",        "sector": "Finance"},
    "INDUSINDBK.NS":    {"name": "IndusInd Bank",             "sector": "Finance"},

    # Healthcare
    "APOLLOHOSP.NS":    {"name": "Apollo Hospitals",          "sector": "Healthcare"},

    # Others
    "LT.NS":            {"name": "L&T",                       "sector": "Infrastructure"},
    "WIPRO.NS":         {"name": "Wipro",                     "sector": "IT"},
}

SECTORS = sorted(set(v["sector"] for v in NIFTY50_STOCKS.values()))

def get_tickers():
    return list(NIFTY50_STOCKS.keys())

def get_ticker_label(ticker):
    return NIFTY50_STOCKS.get(ticker, {}).get("name", ticker.replace(".NS", ""))

def get_sector(ticker):
    return NIFTY50_STOCKS.get(ticker, {}).get("sector", "Unknown")

def get_tickers_by_sector(sector):
    return [t for t, v in NIFTY50_STOCKS.items() if v["sector"] == sector]

def search_stocks(query: str):
    query = query.lower()
    results = {}
    for ticker, info in NIFTY50_STOCKS.items():
        if query in ticker.lower() or query in info["name"].lower():
            results[ticker] = info
    return results