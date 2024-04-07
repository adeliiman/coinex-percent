from datetime import datetime
from database import SessionLocal
from main import coinex, api
from setLogger import get_logger
import time, json, threading
from binance import ThreadedWebsocketManager


logger = get_logger(__name__)


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

class BinanceWs:
    def __init__(self):
        self.url = None

    def handle_socket_message(self, data):
        try:
            if coinex.bot == "Stop":
                self.twm.stop()
                logger.info("Websocket Closed.")
            # print(data)
            data = data['data']
            if 'k' in data.keys():
                data = data['k']
                symbol = data['s'].split("USDT")[0] # BTC
                interval = data['i']
                sym = symbol+"_"+interval # BTC_1m
                open_price = float(data['o'])
                close_price = float(data['c'])
                is_kline_closed = data['x']
                # print(sym, open_price, close_price, is_kline_closed)

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



    def ws(self):
        self.twm = ThreadedWebsocketManager()
        # start is required to initialise its internal loop
        self.twm.start()
        streams = []
        for symbol in coinex.symbols:
            for interval in coinex.percent.keys():
                streams.append(f"{symbol.lower()}usdt@kline_{interval}")
        # print(streams)
        self.twm.start_multiplex_socket(callback=self.handle_socket_message, streams=streams)
        

        self.twm.join()


bws = BinanceWs()


def schedule():
    
    try:
        ws = bws.ws()
        ws
    except Exception as e:
        logger.exception(msg=f"{e}")
    
        