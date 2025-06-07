# predictor.py

from scraper import get_latest_results
from collections import Counter

def predict_next():
    data = get_latest_results(limit=10)
    if len(data) < 5:
        return {"skip": True}, 0

    colors = [item["color"] for item in data]
    sizes = [item["size"] for item in data]
    numbers = [item["number"] for item in data]

    color_common = Counter(colors).most_common(1)[0]
    size_common = Counter(sizes).most_common(1)[0]
    number_common = Counter(numbers).most_common(1)[0]

    # Confidence scoring: how frequently the top value appeared
    confidence = round(((color_common[1] + size_common[1] + number_common[1]) / (3 * len(data))) * 100)

    if confidence < 75:
        return {"skip": True}, confidence

    return {
        "color": color_common[0],
        "size": size_common[0],
        "number": number_common[0],
        "skip": False
    }, confidence
