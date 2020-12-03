import websocket, json, pprint, talib
import numpy as np
import config
from binance.client import Client
from binance.enums import *

client = Client(config.API_KEY, config.SECRET_KEY)

SOCKET = "wss://stream.binance.com:9443/ws/btcgbp@kline_1m"
RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30
TRADE_SYMBOL = 'BTCGBP'
TRADE_AMOUNT = 0.001040

closes = []
in_position = False

def order(symbol, side, quantity, order_type=ORDER_TYPE_MARKET):
    try:
        order = client.create_order(
        symbol=symbol,
        side=side,
        type=order_type,
        timeInForce=TIME_IN_FORCE_GTC,
        quantity=quantity)

        print(order)

    except Exception as e:
        return False
    
    return True


def on_open(ws):
    print("Opened connection.")

def on_close(ws):
    print("Closed connection.")

def on_message(ws, msg):
    json_msg = json.loads(msg)
    pprint.pprint(json_msg)

    # check if end of kline
    candle = json_msg['k']
    is_candle_closed = candle['x']
    close = candle['c']

    if is_candle_closed:
        global closes
        closes.append(float(close))
        print("Candle closed at {}".format(close))
        print(closes)

        if len(closes) > RSI_PERIOD:
            np_closes = np.array(closes)
            rsi = talib.RSI(np_closes, RSI_PERIOD)
            print("RSIs calculated so far: ")
            print(rsi)
            last_rsi = rsi[-1]
            print("Most recent RSI: {}".format(last_rsi))

            if last_rsi > RSI_OVERBOUGHT:
                print("Selling...")
                if in_position:
                    order_did_happen = order(TRADE_SYMBOL, SIDE_SELL, TRADE_AMOUNT, order_type=ORDER_TYPE_MARKET)
                    if order_did_happen:
                        in_position = False

                else:
                    print("Already sold.")

            elif last_rsi < RSI_OVERSOLD:
                if in_position:
                    print("Already bought.")
                else:
                    print("Buying...")
                    order_did_happen = order(TRADE_SYMBOL, SIDE_BUY, TRADE_AMOUNT, order_type=ORDER_TYPE_MARKET)
                    if order_did_happen:
                        in_position = False

ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_message=on_message)
ws.run_forever()