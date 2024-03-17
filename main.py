import json, time, requests
from models import Signal
import concurrent.futures
from database import SessionLocal
import random, schedule
import threading
from datetime import datetime
from database import SessionLocal
from lib import CoinexPerpetualApi


from setLogger import get_logger
logger = get_logger(__name__)


with open('config.json') as f:
    config = json.load(f)


access_id = config['access_id']
secret_key = config['secret_key']
api = CoinexPerpetualApi(access_id, secret_key)


class Coinex:
	bot: str = 'Stop' # 'Run'
	leverage: int 
	exit_percent: float # 1/100
	trade_value: int
	symbols: list = []
	percent: dict = {} # {'1d': 10/100}
	position: dict = {} # {'BTC_1m': True/False}
	pivot: dict = {} # {'BTC_1m': 1234}
	kline: dict = {} # {'BTC_1m': True/False}
    

coinex = Coinex()




