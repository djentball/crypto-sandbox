import requests
import numpy as np

USER_ID = "c6a5c630-2ab6-423b-aa02-4ab69d1da6e3"
SYMBOL = "BTCUSDT"


def fetch_binance_data(symbol="BTCUSDT", interval="1h", limit=300):  # limit зменшено
    url = f"https://api.binance.com/api/v3/klines"
    params = {"symbol": symbol, "interval": interval, "limit": limit}
    response = requests.get(url, params=params)
    data = response.json()

    closes = np.array([float(item[4]) for item in data], dtype=np.float64)
    timestamps = [int(item[0]) for item in data]
    return timestamps, closes


def calculate_ema(prices, window):
    ema = np.empty_like(prices)
    alpha = 2 / (window + 1)
    ema[window - 1] = np.mean(prices[:window])
    for i in range(window, len(prices)):
        ema[i] = prices[i] * alpha + ema[i - 1] * (1 - alpha)
    ema[:window - 1] = np.nan
    return ema


def calculate_rsi(prices, window=14):
    deltas = np.diff(prices)
    gains = np.where(deltas > 0, deltas, 0)
    losses = np.where(deltas < 0, -deltas, 0)

    avg_gain = np.full(prices.shape, np.nan, dtype=np.float64)
    avg_loss = np.full(prices.shape, np.nan, dtype=np.float64)

    avg_gain[window] = np.mean(gains[:window])
    avg_loss[window] = np.mean(losses[:window])

    for i in range(window + 1, len(prices)):
        avg_gain[i] = (avg_gain[i - 1] * (window - 1) + gains[i - 1]) / window
        avg_loss[i] = (avg_loss[i - 1] * (window - 1) + losses[i - 1]) / window

    rs = np.divide(avg_gain, avg_loss, out=np.zeros_like(avg_gain), where=avg_loss != 0)
    rsi = 100 - (100 / (1 + rs))
    rsi[:window] = np.nan
    return rsi


def generate_signal(ema_9, ema_21, rsi, index):
    if np.isnan(ema_9[index]) or np.isnan(ema_21[index]) or np.isnan(rsi[index]):
        return "WAIT"

    if ema_9[index] > ema_21[index] and rsi[index] < 40:
        requests.post("https://api-aio.alwaysdata.net/crypto/trade/buy", json={
            "user_id": USER_ID, "symbol": SYMBOL, "quantity": 0.0007
        })
        return "BUY"

    if ema_9[index] < ema_21[index] and rsi[index] > 60:
        requests.post("https://api-aio.alwaysdata.net/crypto/trade/sell", json={
            "user_id": USER_ID, "symbol": SYMBOL, "quantity": 0.0007
        })
        return "SELL"

    return "WAIT"


# --- Run ---
timestamps, closes = fetch_binance_data(SYMBOL)
ema_9 = calculate_ema(closes, 9)
ema_21 = calculate_ema(closes, 21)
rsi = calculate_rsi(closes, 14)

for i in range(len(closes) - 10, len(closes)):
    e9 = f"{ema_9[i]:.2f}" if not np.isnan(ema_9[i]) else "nan"
    e21 = f"{ema_21[i]:.2f}" if not np.isnan(ema_21[i]) else "nan"
    r = f"{rsi[i]:.2f}" if not np.isnan(rsi[i]) else "nan"
    print(f"{i}: close={closes[i]:.2f}, EMA_9={e9}, EMA_21={e21}, RSI={r}")
    signal = generate_signal(ema_9, ema_21, rsi, i)
    print("   Signal:", signal)
