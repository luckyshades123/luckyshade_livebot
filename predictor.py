# predictor.py
import random

def predict_next():
    confidence = random.randint(70, 99)

    if confidence < 75:
        return "SKIP", confidence

    color = random.choice(["🟩 Green", "🟥 Red", "🟪 Violet"])
    size = random.choice(["Big", "Small"])
    number = random.choice(list(range(10)))

    return {
        "color": color,
        "size": size,
        "number": number
    }, confidence
