import pandas as pd
import requests
import ta


# User id c6a5c630-2ab6-423b-aa02-4ab69d1da6e3
def fetch_binance_data(symbol="BTCUSDT", interval="1h", limit=500):
    url = f"https://api.binance.com/api/v3/klines"
    params = {"symbol": symbol, "interval": interval, "limit": limit}
    response = requests.get(url, params=params)
    data = response.json()
    df = pd.DataFrame(data, columns=[
        "timestamp", "open", "high", "low", "close", "volume",
        "close_time", "quote_asset_volume", "number_of_trades",
        "taker_buy_base_asset_volume", "taker_buy_quote_asset_volume", "ignore"
    ])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    df["close"] = df["close"].astype(float)
    return df[["timestamp", "close"]]


def calculate_indicators(df):
    df["EMA_9"] = ta.trend.ema_indicator(df["close"], window=9)
    df["EMA_21"] = ta.trend.ema_indicator(df["close"], window=21)
    df["RSI"] = ta.momentum.rsi(df["close"], window=14)
    return df


def generate_signal(row):
    if row["EMA_9"] > row["EMA_21"] and row["RSI"] < 40:
        body = {
            "user_id": "c6a5c630-2ab6-423b-aa02-4ab69d1da6e3",
            "symbol": "BTCUSDT",
            "quantity": 0.0007
        }
        r = requests.post('https://api-aio.alwaysdata.net/crypto/trade/buy', json=body)
        return "BUY"
    elif row["EMA_9"] < row["EMA_21"] and row["RSI"] > 60:
        body = {
            "user_id": "c6a5c630-2ab6-423b-aa02-4ab69d1da6e3",
            "symbol": "BTCUSDT",
            "quantity": 0.0007
        }
        r = requests.post('https://api-aio.alwaysdata.net/crypto/trade/sell', json=body)
        return "SELL"
    return "WAIT"


df = fetch_binance_data()
df = calculate_indicators(df)
df["Signal"] = df.apply(generate_signal, axis=1)

table = df[["timestamp", "close", "EMA_9", "EMA_21", "RSI", "Signal"]]
print(table.tail(10))
print("Останній сигнал:", df["Signal"].iloc[-1])


