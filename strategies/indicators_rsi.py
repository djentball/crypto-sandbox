import requests
from db.indicators_util import calculate_rsi, fetch_binance_data


def generate_signal(current_rsi, prev_rsi, user_id="c6a5c630-2ab6-423b-aa02-4ab69d1da6e3"):
    signal = "WAIT"
    if current_rsi is None or prev_rsi is None:
        return "WAIT"

    if current_rsi < 45:
        if prev_rsi < current_rsi - 1:
            signal = "BUY"
            requests.post('https://api-aio.alwaysdata.net/crypto/trade/buy', json={
                "user_id": user_id, "symbol": "BTCUSDT", "quantity": 0.0004
            })
        else:
            signal = "WAIT_LOW"

    elif current_rsi > 60:
        if prev_rsi > current_rsi + 1:
            signal = "SELL"
            requests.post('https://api-aio.alwaysdata.net/crypto/trade/sell', json={
                "user_id": user_id, "symbol": "BTCUSDT", "quantity": 0.0004
            })
        else:
            signal = "WAIT_HIGH"

    return signal


timestamps, closes = fetch_binance_data()
rsi = calculate_rsi(closes, 14)

# Виводимо останні 10 значень
for i in range(len(rsi) - 10, len(rsi)):
    entry = rsi[i]
    prev_entry = rsi[i - 1] if i - 1 >= 0 else {"rsi": None}

    idx = entry["index"]
    rsi_value = entry["rsi"]
    prev_rsi_value = prev_entry["rsi"]

    print(f"{idx}: close={closes[idx]:.2f}, RSI={rsi_value:.2f} (prev={prev_rsi_value})")
    signal = generate_signal(rsi_value, prev_rsi_value)
    print("   Signal:", signal)

