
#!/usr/bin/env python

import time, random, json, threading
from datetime import datetime
from database import SessionLocal
from binance.lib.utils import config_logging
from binance.websocket.cm_futures.websocket_client import CMFuturesWebsocketClient
from main import coinex, api
from setLogger import get_logger


logger = get_logger(__name__)
# proxies = { 'https': 'http://127.0.0.1:2081' }

def place_order(symbol, side):
    res = api.adjust_leverage(market=symbol+"USD", leverage=coinex.leverage, position_type=side)
    logger.info(f"{res}")
    res = api.put_market_order(market=symbol+"USD", side=side, amount=coinex.trade_value)
    logger.info(f"{res}")
    logger.info(msg=f"place order: {symbol}---{side}---{coinex.trade_value}")
    #
    from models import Signal
    signal = Signal()
    signal.symbol = symbol
    signal.side = side
    signal.qty = coinex.trade_value
    # signal.time = datetime.fromtimestamp(time_/1000)
    signal.time = datetime.now().strftime('%y-%m-%d %H:%M:%S')
    db = SessionLocal()
    db.add(signal)
    db.commit()
    db.close()
    logger.info(f"load to sqlite. {symbol}---{side}---{datetime.now().strftime('%y-%m-%d %H:%M:%S')}")

def close_order(symbol):
    data = api.query_position_pending(market=symbol+"USD")
    print(data)
    if data['data']:
        data = data['data'][0]
        position_id = data['position_id']
        res = api.close_market(market=symbol+"USD", position_id=position_id)
        logger.info(f"{res}")
        logger.info(f"close order: {symbol}")


def message_handler(_, message):
    try:
        data = json.loads(message)
        if 'k' in data.keys():
            data = data['k']
            print(data)
            symbol = data['s'].split("USD_")[0] # BTC
            interval = data['i']
            sym = symbol+"_"+interval # BTC_1m
            open_price = float(data['o'])
            close_price = float(data['c'])
            is_kline_closed = data['x']

            if is_kline_closed:
                coinex.kline[sym] = True

            if coinex.kline.get(sym):
                delta = (close_price - open_price) / open_price # 0.05

                if delta > coinex.percent.get(interval) and not coinex.position.get(sym):
                    coinex.position[sym] = "Long"
                    threading.Thread(target=place_order, kwargs={'symbol':symbol, 'side':2}).start()

                elif -1*delta > coinex.percent.get(interval) and not coinex.position.get(sym):
                    coinex.position[sym] = "Short"
                    threading.Thread(target=place_order, kwargs={'symbol':symbol, 'side':1}).start()

                if coinex.position.get(sym) == "Long":
                    coinex.pivot[sym] = max(close_price, coinex.pivot[sym]) if coinex.pivot.get(sym) else close_price

                    if ((coinex.pivot[sym] - close_price) / close_price) > coinex.exit_percent:
                        del coinex.kline[sym]
                        del coinex.position[sym]
                        del coinex.pivot[sym]
                        #
                        threading.Thread(target=close_order, kwargs={'symbol':symbol}).start()
                        print("Close Long .................")
                elif coinex.position.get(sym) == "Short":
                    coinex.pivot[sym] = min(close_price, coinex.pivot[sym]) if coinex.pivot.get(sym) else close_price

                    if ((close_price - coinex.pivot[sym]) / coinex.pivot[sym]) > coinex.exit_percent:
                        del coinex.kline[sym]
                        del coinex.position[sym]
                        del coinex.pivot[sym]
                        #
                        threading.Thread(target=close_order, kwargs={'symbol':symbol}).start()
                        print("Close Short ...........")
    except Exception as e:
        logger.exception(msg=f"{e}")



def ws():
    def job():
        for symbol in coinex.symbols:
            for interval in coinex.percent.keys():
                my_client.kline(symbol=f"{symbol.lower()}usd_perp",id=random.randint(1, 99999),interval=interval)
    
    def on_close(self):
        if coinex.bot == "Run":
            job()
            logger.info("re run socket ... ... ... ... ... ...")

    my_client = CMFuturesWebsocketClient(on_message=message_handler, on_close=on_close)
    from main import coinex
    job()
    from main import coinex
    while True:
        time.sleep(1)
        if coinex.bot == "Stop":
            my_client.stop()
            my_client.unsubscribe(stream='kline')
            break

    