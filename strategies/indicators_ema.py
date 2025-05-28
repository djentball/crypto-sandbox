import requests
from db.indicators_util import fetch_binance_data, calculate_ema

user_id = "07e6fb06-2491-4ebd-8435-547f052b0047"
quantity = 0.0007
symbol = "BTCUSDT"
url = "https://api-aio.alwaysdata.net/crypto/trade"

closes = fetch_binance_data()[1]
ema_9, ema_21 = calculate_ema(closes, 9), calculate_ema(closes, 21)
last_9, last_21 = ema_9[-1], ema_21[-1]

action = (
    "buy" if last_9 > last_21 else
    "sell" if last_9 < last_21 else
    None
)

if action:
    requests.post(f"{url}/{action}", json={
        "user_id": user_id,
        "symbol": symbol,
        "quantity": quantity
    })

signal = action.upper() if action else "WAIT"
print(f"EMA_9: {last_9:,.2f} EMA_21: {last_21:,.2f}  {signal=}")
