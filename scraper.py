
# scraper.py
def fetch_latest_result(mode, short_period):
    full_period = "2506010" + short_period
    # Mock result; real scraper would login and fetch result from KWG
    return full_period, {
        "number": 5,
        "color": "🟪 Violet",
        "size": "Small"
    }
