from utils.factory import MetatraderFactory

metatrader = MetatraderFactory.get_metatrader()

metatrader.connect()
metatrader.disconnect()

