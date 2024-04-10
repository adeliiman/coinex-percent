from sqlalchemy.orm import Session
from models import Setting, UserSymbols, Percent
from datetime import datetime, timedelta
from setLogger import get_logger
import concurrent.futures
from main import coinex
import time, asyncio, requests, schedule


logger = get_logger(__name__)



def get_user_params(db: Session):
    try:
        user = db.query(Setting).first()
        user_symbols = db.query(UserSymbols).all()
        percent = db.query(Percent).all()

        coinex.leverage = user.leverage
        coinex.exit_percent = user.exit_percent / 100
        coinex.trade_value = float(user.trade_value)
        
        coinex.symbols = []
        for symbol in user_symbols:
            coinex.symbols.append(symbol.symbol)

        coinex.percent = {}
        for per in percent:
            coinex.percent[per.timeframe] = per.percent / 100


            
    except Exception as e:
        logger.exception(msg="get_user_params" + str(e))



