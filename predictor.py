import asyncio
from collections import Counter
from scraper import get_latest_results

def get_color(num):
    if num in [3, 6, 9]:
        return "🟥 Red"
    elif num in [1, 4, 7]:
        return "🟩 Green"
    else:
        return "🟪 Violet"

def get_size(num):
    return "Big" if num >= 5 else "Small"

def check_opposite_pattern(recent_colors):
    pattern = "".join(c[1] for c in recent_colors[-5:])
    opposites = {
        "RRGGR": "🟥 Red",
        "RRGGG": "🟩 Green",
        "RRRRR": "🟩 Green",
        "GGGGG": "🟥 Red",
        "RGRGR": "🟩 Green",
        "GRGRG": "🟥 Red",
        "GRRGG": "🟥 Red"
        # Add more mappings as per your algorithm image
    }
    return opposites.get(pattern, None)

async def predict_next(mode="1Min"):
    try:
        data = await get_latest_results(limit=20, mode=mode)
        if len(data) < 10:
            return {"skip": True}, 0

        # Extract trends
        colors = [item["color"] for item in data]
        sizes = [item["size"] for item in data]
        numbers = [item["number"] for item in data]

        # Analyze last 5–10 colors for known patterns
        raw_sequence = "".join(["R" if c == "🟥 Red" else "G" if c == "🟩 Green" else "V" for c in colors])
        last_pattern = raw_sequence[-5:]

        # Pattern-based override
        color_from_pattern = check_opposite_pattern(colors)
        if color_from_pattern:
            color = color_from_pattern
        else:
            color = Counter(colors).most_common(1)[0][0]

        size = Counter(sizes).most_common(1)[0][0]
        number = Counter(numbers).most_common(1)[0][0]

        # Confidence = based on repetition frequency
        confidence = round(((colors.count(color) + sizes.count(size) + numbers.count(number)) / (3 * len(data))) * 100)

        if confidence < 75:
            return {"skip": True}, confidence

        return {
            "color": color,
            "size": size,
            "number": number,
            "skip": False
        }, confidence

    except Exception as e:
        print(f"[PREDICTOR ERROR] {e}")
        return {"skip": True}, 0
