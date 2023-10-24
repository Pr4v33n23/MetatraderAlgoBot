from dataclasses import dataclass
import pandas as pd
from datetime import datetime
import MetaTrader5 as MT
import time
from tabulate import tabulate

from metatrader.model.order_type import OrderType


@dataclass
class EMACrossover:
    mt5: MT
    volume: float = 0.1
    symbol: str = "EURUSD"
    deviation: int = 20
    strategy_name: str = "ema_crossover"

    def get_data(self, symbol, timeframe, period):
        data = pd.DataFrame(self.mt5.copy_rates_from_pos(symbol, timeframe, 0, period))

        data["ema_10"] = data["close"].ewm(span=10).mean()
        data["ema_20"] = data["close"].ewm(span=20).mean()
        data["time"] = pd.to_datetime(data["time"], unit="s")

        return data

    def close_position(self, position, deviation=20, magic=12345):
        order_type_dict = {0: self.mt5.ORDER_TYPE_SELL, 1: self.mt5.ORDER_TYPE_BUY}

        price_dict = {
            0: self.mt5.symbol_info_tick(self.symbol).bid,
            1: self.mt5.symbol_info_tick(self.symbol).ask,
        }

        request = {
            "action": self.mt5.TRADE_ACTION_DEAL,
            "position": position["ticket"],  # select the position you want to close
            "symbol": self.symbol,
            "volume": self.volume,  # FLOAT
            "type": order_type_dict[position["type"]],
            "price": price_dict[position["type"]],
            "deviation": deviation,  # INTERGER
            "magic": magic,  # INTERGER
            "comment": self.strategy_name,
            "type_time": self.mt5.ORDER_TIME_GTC,
            "type_filling": self.mt5.ORDER_FILLING_FOK,
        }

        order_result = self.mt5.order_send(request)
        return order_result

    def close_positions(self, order_type):
        order_type_dict = {OrderType.Buy.value: 0, OrderType.Sell.value: 1}

        if self.mt5.positions_total() > 0:
            positions = self.mt5.positions_get()

            positions_df = pd.DataFrame(
                positions, columns=positions[0]._asdict().keys()
            )

            if order_type != "all":
                positions_df = positions_df[
                    (positions_df["type"] == order_type_dict[order_type])
                ]

            for i, position in positions_df.iterrows():
                order_result = self.close_position(position)

                print("order_result: ", order_result)

    def check_allowed_trading_hours(self):
        if 1 < datetime.now().hour < 23:
            return True
        else:
            return False

    def market_order(self, symbol, volume, order_type, deviation=20, magic=12345):
        order_type_dict = {
            OrderType.Buy.value: self.mt5.ORDER_TYPE_BUY,
            OrderType.Sell.value: self.mt5.ORDER_TYPE_SELL,
        }

        price_dict = {
            OrderType.Buy.value: self.mt5.symbol_info_tick(symbol).ask,
            OrderType.Sell.value: self.mt5.symbol_info_tick(symbol).bid,
        }

        print(f"Received Order:{order_type} | Symbol: {symbol} | Volume: {volume}")

        request = {
            "action": self.mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": volume,  # FLOAT
            "type": order_type_dict[order_type],
            "price": price_dict[order_type],
            "sl": 0.0,  # FLOAT
            "tp": 0.0,  # FLOAT
            "deviation": deviation,  # INTERGER
            "magic": magic,  # INTERGER
            "comment": self.strategy_name,
            "type_time": self.mt5.ORDER_TIME_GTC,
            "type_filling": self.mt5.ORDER_FILLING_FOK,
        }

        order_result = self.mt5.order_send(request)
        result_dict = order_result._asdict()
        for field in result_dict.keys():
            print("{}={}".format(field, result_dict[field]))
        return order_result

    def run_strategy(self):
        account_info = self.mt5.account_info()
        print(
                datetime.now(),
                "| Login: ",
                account_info.login,
                "| Balance: ",
                account_info.balance,
                "| Equity: ",
                account_info.equity,
        )

        while True:
            
            usd_positions=self.mt5.positions_get(group="*USD*")
            if usd_positions==None:
                print("No positions with group=\"*USD*\", error code={}".format(self.mt5.last_error()))
            elif len(usd_positions)>0:
                print("positions_get(group=\"*USD*\")={}".format(len(usd_positions)))
                # display these positions as a table using pandas.DataFrame
                df=pd.DataFrame(list(usd_positions),columns=usd_positions[0]._asdict().keys())
                df['time'] = pd.to_datetime(df['time'], unit='s')
                df.drop(['time_update', 'time_msc', 'time_update_msc', 'external_id'], axis=1, inplace=True)
                print(tabulate(df, headers="keys", tablefmt="psql"))

            num_positions = self.mt5.positions_total()

            if not self.check_allowed_trading_hours():
                self.close_positions("all")

            lookback_period = 100
            data = self.get_data(self.symbol, self.mt5.TIMEFRAME_M5, lookback_period)

            fast_ema = data["ema_10"].iloc[-1]
            slow_ema = data["ema_20"].iloc[-1]
            if fast_ema > slow_ema :
                self.close_positions(OrderType.Sell.value)
                if num_positions == 0 and self.check_allowed_trading_hours():
                    order_result = self.market_order(
                        self.symbol, self.volume, OrderType.Buy.value
                    )
                    print(order_result)

            elif fast_ema < slow_ema:
                self.close_positions(OrderType.Buy.value)

                if num_positions == 0 and self.check_allowed_trading_hours():
                    order_result = self.market_order(
                        self.symbol, self.volume, OrderType.Sell.value
                    )
                    print(order_result)

            time.sleep(1)
