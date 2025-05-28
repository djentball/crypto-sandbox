import requests


def fetch_binance_data(symbol="BTCUSDT", interval="1h", limit=500):
    url = f"https://api.binance.com/api/v3/klines"
    params = {"symbol": symbol, "interval": interval, "limit": limit}
    response = requests.get(url, params=params)
    data = response.json()
    closes = [float(candle[4]) for candle in data]
    timestamps = [int(candle[0]) for candle in data]
    return timestamps, closes


# === EMA ===
def calculate_ema(values, window):
    ema = []
    k = 2 / (window + 1)
    sma = sum(values[:window]) / window
    ema.append(sma)
    for price in values[window:]:
        ema.append(price * k + ema[-1] * (1 - k))
    return [None] * (window - 1) + ema


# === RSI ===
def calculate_rsi(values, window):
    gains = []
    losses = []

    for i in range(1, window + 1):
        change = values[i] - values[i - 1]
        gains.append(max(0, change))
        losses.append(max(0, -change))

    avg_gain = sum(gains) / window
    avg_loss = sum(losses) / window

    rsi = []
    if avg_loss == 0:
        rsi.append(100)
    else:
        rs = avg_gain / avg_loss
        rsi.append(100 - (100 / (1 + rs)))

    for i in range(window + 1, len(values)):
        change = values[i] - values[i - 1]
        gain = max(0, change)
        loss = max(0, -change)

        avg_gain = (avg_gain * (window - 1) + gain) / window
        avg_loss = (avg_loss * (window - 1) + loss) / window

        if avg_loss == 0:
            rsi.append(100)
        else:
            rs = avg_gain / avg_loss
            rsi.append(100 - (100 / (1 + rs)))

    return [None] * window + rsi