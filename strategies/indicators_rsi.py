import requests
from db.indicators_util import calculate_rsi, calculate_ema, fetch_binance_data


def generate_signal(close, ema_9, ema_21, rsi, user_id="c6a5c630-2ab6-423b-aa02-4ab69d1da6e3"):
    signal = "WAIT"
    if rsi:
        if rsi < 42:
            requests.post('https://api-aio.alwaysdata.net/crypto/trade/buy', json={
                "user_id": user_id, "symbol": "BTCUSDT", "quantity": 0.0007
            })
            signal = "BUY"
        elif rsi > 60:
            requests.post('https://api-aio.alwaysdata.net/crypto/trade/sell', json={
                "user_id": user_id, "symbol": "BTCUSDT", "quantity": 0.0007
            })
            signal = "SELL"
    return signal


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
