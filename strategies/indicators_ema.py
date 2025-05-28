import requests

from db.indicators_util import fetch_binance_data, calculate_ema


timestamps, closes = fetch_binance_data()
ema_9 = calculate_ema(closes, 9)
ema_21 = calculate_ema(closes, 21)
user_id = "07e6fb06-2491-4ebd-8435-547f052b0047"
quantity = 0.0007

if ema_9 > ema_21:
    requests.post('https://api-aio.alwaysdata.net/crypto/trade/buy', json={
        "user_id": user_id, "symbol": "BTCUSDT", "quantity": quantity
    })
    signal = "BUY"
elif ema_9 < ema_21:
    requests.post('https://api-aio.alwaysdata.net/crypto/trade/sell', json={
        "user_id": user_id, "symbol": "BTCUSDT", "quantity": quantity
    })
    signal = "SELL"
else:
    signal = "WAIT"

print(signal)
