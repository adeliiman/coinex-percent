from fastapi import FastAPI , Depends
from starlette.background import BackgroundTasks
from sqlalchemy.orm import Session
import uvicorn
from models import  SettingAdmin, SignalAdmin, UserSymbolAdmin, ReportView, PercentAdmin
from database import get_db, engine, Base
from sqladmin import Admin
from setLogger import get_logger
from fastapi.responses import RedirectResponse
from utils import get_user_params
from contextlib import asynccontextmanager
import threading



logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(lifespan=lifespan)
admin = Admin(app, engine)

admin.add_view(ReportView)
admin.add_view(SettingAdmin)
admin.add_view(PercentAdmin)
admin.add_view(UserSymbolAdmin)
admin.add_view(SignalAdmin)


from main import coinex

@app.get('/run')
async def run(tasks: BackgroundTasks, db: Session=Depends(get_db)):

    get_user_params(db=db)
    coinex.bot = "Run"
    from binanceWebsocket import ws
    threading.Thread(target=ws).start()
    logger.info("Coinex started ... ... ...")
    return  RedirectResponse(url="/admin/home")


@app.get('/stop')
def stop():
    coinex.bot = "Stop"
    logger.info("Bingx stoped. ................")
    return  RedirectResponse(url="/admin/home")


@app.get('/closeAll')
def closeAll():
    from main import api
    res = api.closeAllPositions()
    logger.info("Close All Positions." + str(res))
    res = api.closeAllOrders()
    logger.info("Close All Orders." + str(res))
    return  RedirectResponse(url="/admin/home")


@app.get('/positions')
def get_positions(symbol:str):
    from main import api
    res = api.getPositions(symbol=symbol)
    logger.info(f"{res}")





@app.get('/')
async def index():
     return  RedirectResponse(url="/admin/home")



if __name__ == '__main__':
	uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)



