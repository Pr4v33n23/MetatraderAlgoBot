from dataclasses import dataclass
from typing import Optional
from logging import info, error
import MetaTrader5 as mt5


@dataclass
class ConfigMetatrader:
    metatrader_login_id: int
    metatrader_login_password: str
    metatrader_login_server: str
    metatrader_login_terminal_path: Optional[str] = None

    def connect(self):
        if self.metatrader_login_terminal_path:
            if not mt5.initialize(self.metatrader_login_terminal_path):
                error(f"Failed to connect to Metatrader, Error: {mt5.last_error()}")
                raise Exception("Failed to connect to Metatrader")
        elif not mt5.initialize():
            error(f"Failed to connect to Metatrader, Error: {mt5.last_error()}")
            raise Exception("Failed to connect to Metatrader")
        elif not mt5.login(
            self.metatrader_login_id,
            self.metatrader_login_password,
            self.metatrader_login_server,
        ):
            error(f"Failed to connect to Metatrader, Error: {mt5.last_error()}")
            raise Exception("Failed to connect to Metatrader")
        else:
            info("Connected to Metatrader successfully.")
            return mt5

    def disconnect(self):
        is_connected = mt5.initialize()
        if not is_connected:
            error(f"Cannot disconnect unopened connection, Error: {mt5.last_error()}")
            raise Exception(f"Cannot disconnect unopened connection")
        else:
            mt5.shutdown()
