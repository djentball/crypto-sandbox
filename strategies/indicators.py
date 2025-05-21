import requests
import math

# === Функція для завантаження даних ===
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

# === Генерація сигналу ===
def generate_signal(close, ema_9, ema_21, rsi, user_id="c6a5c630-2ab6-423b-aa02-4ab69d1da6e3"):
    signal = "WAIT"
    if ema_9 and ema_21 and rsi:
        if ema_9 > ema_21 and rsi < 40:
            requests.post('https://api-aio.alwaysdata.net/crypto/trade/buy', json={
                "user_id": user_id, "symbol": "BTCUSDT", "quantity": 0.0007
            })
            signal = "BUY"
        elif ema_9 < ema_21 and rsi > 60:
            requests.post('https://api-aio.alwaysdata.net/crypto/trade/sell', json={
                "user_id": user_id, "symbol": "BTCUSDT", "quantity": 0.0007
            })
            signal = "SELL"
    return signal

# === Основна логіка ===
timestamps, closes = fetch_binance_data()
ema_9 = calculate_ema(closes, 9)
ema_21 = calculate_ema(closes, 21)
rsi = calculate_rsi(closes, 14)

for i in range(len(closes) - 10, len(closes)):
    print(
        f"{i}: close={closes[i]:.2f}, EMA_9={ema_9[i]}, EMA_21={ema_21[i]}, RSI={rsi[i]}"
    )
    signal = generate_signal(closes[i], ema_9[i], ema_21[i], rsi[i])
    print("   Signal:", signal)
