from dataclasses import dataclass, asdict
from typing import Optional, ClassVar

import pandas as pd

from metatrader.model.order_status import OrderStatus
from metatrader.model.order_type import OrderType


@dataclass
class Position:
    open_datetime: str
    open_price: float
    order_type: str
    volume: int
    stop_loss: float
    take_profit: float
    comment: str
    close_datetime: Optional[str] = None
    close_price: Optional[float] = None
    profit: float = 0.0
    status: str = OrderStatus.Open.value

    def close_position(self, close_datetime: str, close_price: float):
        """
        The function updates the status of a position to "closed" and calculates the profit based on the
        close price and volume.

        :param close_datetime: The close_datetime parameter is a string that represents the date and
        time when the position was closed
        :type close_datetime: str
        :param close_price: The close_price parameter is the price at which the position is closed
        :type close_price: float
        """
        self.close_datetime = close_datetime
        self.close_price = close_price
        self.status = OrderStatus.Closed.value
        self.profit = (
            (self.close_price - self.open_price) * self.volume
            if self.order_type == OrderType.Buy.value
            else (self.open_price - self.close_price) * self.volume
        )

    def to_dict(self):
        """
        The function converts an object to a dictionary using the asdict() function.
        :return: The method `to_dict` is returning the result of calling the `asdict` function on
        `self`.
        """
        return asdict(self)


@dataclass
class Strategy:
    starting_balance: float
    positions: ClassVar[list[Position]] = []
    data: pd.DataFrame
    risk_percentage: float
    trading_allowed: bool = True

    def get_positions_df(self) -> pd.DataFrame:
        """
        The function `get_positions_df` returns a pandas DataFrame containing information about
        positions, including profit and cumulative profit.
        :return: a pandas DataFrame object.
        """
        df = pd.DataFrame([position.to_dict() for position in self.positions])
        df["pnl"] = df["profit"].cumsum() + self.starting_balance
        return df

    def add_position(self, position: Position) -> bool:
        """
        The function adds a position to a list and returns True.

        :param position: The parameter "position" is of type "Position". It is an object that represents
        a position
        :type position: Position
        :return: a boolean value, specifically True.
        """
        self.positions.append(position)
        return True

    def trade(self, drawdown: float, data: pd.Series):
        """
        The function checks if trading is allowed based on the drawdown and adds a position if allowed.

        :param drawdown: The "drawdown" parameter is a float value that represents the drawdown level at
        which the trade should be executed. It is used to determine if a trade should be made based on
        the current signal and the drawdown level
        :type drawdown: float
        :param data: The `data` parameter is a pandas Series object that contains the trading data for a
        specific time period. It typically includes information such as the time, close price, and any
        other relevant data for making trading decisions
        :type data: pd.Series
        """
        self.trading_allowed = True
        if data.signal == drawdown:
            for position in self.positions:
                if (
                    position.status == OrderStatus.Open.value
                    and position.comment == drawdown
                ):
                    self.trading_allowed = False
                    break
            if self.trading_allowed:
                volume = 0
                if len(self.positions) == 0:
                    volume = int(
                        (self.starting_balance * self.risk_percentage) / data.close
                    )
                else:
                    df = self.get_positions_df()
                    volume = int((df["pnl"].iat[-1] * self.risk_percentage) / data.close)
                self.add_position(
                    Position(
                        data.time,
                        data.close,
                        OrderType.Buy.value,
                        volume,
                        0.0,
                        0.0,
                        drawdown,
                    )
                )

    def run(self):
        """
        The function iterates through a dataset, performs trades based on certain conditions, and closes
        positions if the drawdown is zero.
        :return: the result of calling the method `get_positions_df()` on the object `self`.
        """
        for i, data in self.data.iterrows():
            self.trade(">10% dd", data)
            self.trade(">15% dd", data)
            self.trade(">20% dd", data)
            self.trade(">25% dd", data)
            self.trade(">30% dd", data)

            if data.drawdown == 0.0:
                for position in self.positions:
                    if position.status == OrderStatus.Open.value:
                        position.close_position(data.time, data.close)
        return self.get_positions_df()

    def calculate_volume(
        self, pnl: float, risk_percentage: float, open_price: float
    ) -> int:
        return int((pnl * risk_percentage) / open_price)
