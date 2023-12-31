from dataclasses import dataclass

from decouple import config

from  metatrader.config.config import ConfigMetatrader


@dataclass
class MetatraderFactory:
    @staticmethod
    def get_metatrader(path=None):
        try:
            METATRADER_ID = config("METATRADER_ID", cast=int)
            METATRADER_PASSWORD = config("METATRADER_PASSWORD", cast=str)
            METATRADER_SERVER = config("METATRADER_SERVER", cast=str)
            if path:
                return ConfigMetatrader(
                    METATRADER_ID, METATRADER_PASSWORD, METATRADER_SERVER, path
                )
            else:
                return ConfigMetatrader(
                    METATRADER_ID, METATRADER_PASSWORD, METATRADER_SERVER
                )
        except ConnectionError as e:
            print(f"Failed to get metatrader connection, error: {e}")
            raise ConnectionError("Failed to get metatrader connection,", e) from e
