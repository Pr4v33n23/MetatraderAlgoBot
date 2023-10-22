from dataclasses import dataclass
from typing import Optional

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
                print(f"Failed to connect to Metatrader, Error: {mt5.last_error()}")
                raise Exception("Failed to connect to Metatrader.")
        elif not mt5.initialize():
            print(f"Failed to connect to Metatrader, Error: {mt5.last_error()}")
            raise Exception("Failed to connect to Metatrader.")
        elif not mt5.login(
            self.metatrader_login_id,
            self.metatrader_login_password,
            self.metatrader_login_server,
        ):
            print(f"Failed to connect to Metatrader, Error: {mt5.last_error()}")
            raise Exception("Failed to connect to Metatrader.")
        else:
            print("Connected to Metatrader successfully.")
            return mt5
        
    def disconnect(self):
        is_connected = mt5.initialize()
        if not is_connected:
            print(f"Cannot disconnect unopened connection, Error: {mt5.last_error()}")
            raise Exception(f"Cannot disconnect unopened connection.")
        else:
            mt5.shutdown()
            print("Disconnected from Metatrader.")

