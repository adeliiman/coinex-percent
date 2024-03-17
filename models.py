
from sqlalchemy import Column,Integer,Numeric,String, DateTime, Boolean, Float
from database import Base
from sqladmin import Admin, ModelView
from sqladmin import BaseView, expose
import wtforms




class Setting(Base):
    __tablename__ = "setting"
    id = Column(Integer,primary_key=True)  
    leverage = Column(Integer, default=10)
    exit_percent = Column(Float, default=1)
    trade_value = Column(Integer, default=50)


class SettingAdmin(ModelView, model=Setting):
    #form_columns = [User.name]
    column_list = [Setting.leverage, Setting.exit_percent,
                    Setting.trade_value]
    name = "Setting"
    name_plural = "Setting"
    icon = "fa-solid fa-user"
    # form_args = dict( )
    # form_overrides =  dict(timeframe=wtforms.SelectField, use_symbols=wtforms.SelectField,
    #                        margin_mode=wtforms.SelectField)
    # form_overrides = dict(exit_percent=dict(label="%"))
    # async def on_model_change(self, data, model, is_created):
    #     # Perform some other action
    #     #print(data)
    #     pass

    # async def on_model_delete(self, model):
    #     # Perform some other action
    #     pass



class Signal(Base):
    __tablename__ = "signals"

    id = Column(Integer,primary_key=True,index=True)
    symbol = Column(String)
    side = Column(String)
    price = Column(Float)
    time = Column(String)
    qty = Column(String)

class SignalAdmin(ModelView, model=Signal):
    column_list = [Signal.id, Signal.symbol, Signal.side, Signal.price, Signal.time, Signal.qty]
    column_searchable_list = [Signal.symbol, Signal.side, Signal.time, Signal.price, Signal.qty]
    #icon = "fa-chart-line"
    icon = "fas fa-chart-line"
    column_sortable_list = [Signal.id, Signal.time, Signal.price, Signal.symbol, Signal.side, Signal.qty]
    # column_formatters = {Signal.level0 : lambda m, a: round(m.level0,4),
    #                      Signal.level1 : lambda m, a: round(m.level1,4),
    #                      Signal.level2 : lambda m, a: round(m.level2,4),
    #                      Signal.level3 : lambda m, a: round(m.level3,4),
    #                      Signal.SLPrice : lambda m, a:round(m.SLPrice,4)}
    
    async def on_model_change(self, data, model, is_created):
        # Perform some other action
        #print(data)
        pass


class UserSymbols(Base):
    __tablename__ = "user-symbols"
    id = Column(Integer,primary_key=True)
    symbol = Column(String)

class UserSymbolAdmin(ModelView, model=UserSymbols):
    column_list = [UserSymbols.id, UserSymbols.symbol
                   ]
    name = "symbol"
    name_plural = "User Symbols"
    icon = "fa-sharp fa-solid fa-bitcoin-sign"
    column_sortable_list = [UserSymbols.symbol, UserSymbols.id]
    column_searchable_list = [UserSymbols.symbol, UserSymbols.id]
    page_size = 100
    form_overrides = dict(symbol=wtforms.StringField, position_side=wtforms.SelectField)
    form_args = dict(symbol=dict(validators=[wtforms.validators.regexp('.+[A-Z]')], label="symbol(BTC)"),
                     )
    
    # async def on_model_change(self, data, model, is_created):
    #     print(is_created)
    #     from database import SessionLocal
    #     db = SessionLocal()
    #     symbol = db.query(Symbols).order_by(Symbols.id.desc()).first()
    #     symbol.test = "iman"
    #     db.commit()

class Percent(Base):
    __tablename__ = "percent"
    id = Column(Integer,primary_key=True)  
    timeframe = Column(String, default='1h')
    percent = Column(Float, default=5)


class PercentAdmin(ModelView, model=Percent):
    #form_columns = [User.name]
    column_list = [Percent.timeframe, Percent.percent,
                    ]
    name = "Percent"
    name_plural = "Percent"
    icon = "fa-solid fa-user"
    # form_args = dict( )
    form_overrides =  dict(timeframe=wtforms.SelectField)
    form_args = dict(timeframe=dict(default="1h", choices=["1m", "3m","5m", "15m", "30m", "1h", "2h", "4h", "12h", "1d"], label="timeframe"),
                     )
    # async def on_model_change(self, data, model, is_created):
    #     # Perform some other action
    #     #print(data)
    #     pass

    # async def on_model_delete(self, model):
    #     # Perform some other action
    #     pass

class ReportView(BaseView):
    name = "Home"
    icon = "fas fa-house-user"

    @expose("/home", methods=["GET"])
    async def report_page(self, request):
        from main import coinex
        return await self.templates.TemplateResponse(name="base1.html", request=request, context={"request":request, "status":coinex.bot})



