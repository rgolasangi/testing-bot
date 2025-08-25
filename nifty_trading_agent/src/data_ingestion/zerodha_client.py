from kiteconnect import KiteConnect
from ..utils.config_manager import config
from ..utils.logger import logger

class ZerodhaClient:
    def __init__(self):
        self.api_key = config.get("zerodha.api_key")
        self.api_secret = config.get("zerodha.api_secret")
        self.redirect_url = config.get("zerodha.redirect_url")
        self.kite = KiteConnect(api_key=self.api_key)
        self.access_token = None
        logger.info("ZerodhaClient initialized.")

    def generate_session(self, request_token):
        try:
            data = self.kite.generate_session(request_token, api_secret=self.api_secret)
            self.access_token = data["access_token"]
            self.kite.set_access_token(self.access_token)
            logger.info(f"Zerodha session generated. Access Token: {self.access_token}")
            return True
        except Exception as e:
            logger.error(f"Error generating Zerodha session: {e}")
            return False

    def set_access_token(self, access_token):
        self.access_token = access_token
        self.kite.set_access_token(self.access_token)
        logger.info("Zerodha access token set.")

    def get_login_url(self):
        return self.kite.login_url()

    def get_historical_data(self, instrument_token, from_date, to_date, interval):
        try:
            data = self.kite.historical_data(instrument_token, from_date, to_date, interval)
            logger.info(f"Fetched historical data for {instrument_token} from {from_date} to {to_date}")
            return data
        except Exception as e:
            logger.error(f"Error fetching historical data: {e}")
            return None

    def get_quote(self, instrument_token):
        try:
            data = self.kite.quote(instrument_token)
            logger.info(f"Fetched quote for {instrument_token}")
            return data
        except Exception as e:
            logger.error(f"Error fetching quote: {e}")
            return None

    def get_ohlc(self, instrument_token):
        try:
            data = self.kite.ohlc(instrument_token)
            logger.info(f"Fetched OHLC for {instrument_token}")
            return data
        except Exception as e:
            logger.error(f"Error fetching OHLC: {e}")
            return None

    def get_instruments(self, exchange=None):
        try:
            if exchange:
                data = self.kite.instruments(exchange=exchange)
                logger.info(f"Fetched instruments for exchange: {exchange}")
            else:
                data = self.kite.instruments()
                logger.info("Fetched all instruments.")
            return data
        except Exception as e:
            logger.error(f"Error fetching instruments: {e}")
            return None

    def place_order(self, variety, exchange, tradingsymbol, transaction_type, quantity, product, order_type, price=None, trigger_price=None):
        try:
            order_id = self.kite.place_order(variety=variety, 
                                            exchange=exchange,
                                            tradingsymbol=tradingsymbol,
                                            transaction_type=transaction_type,
                                            quantity=quantity,
                                            product=product,
                                            order_type=order_type,
                                            price=price,
                                            trigger_price=trigger_price)
            logger.info(f"Order placed successfully. Order ID: {order_id}")
            return order_id
        except Exception as e:
            logger.error(f"Error placing order: {e}")
            return None

    def get_orders(self):
        try:
            orders = self.kite.orders()
            logger.info("Fetched all orders.")
            return orders
        except Exception as e:
            logger.error(f"Error fetching orders: {e}")
            return None

    def get_positions(self):
        try:
            positions = self.kite.positions()
            logger.info("Fetched all positions.")
            return positions
        except Exception as e:
            logger.error(f"Error fetching positions: {e}")
            return None

    def get_holdings(self):
        try:
            holdings = self.kite.holdings()
            logger.info("Fetched all holdings.")
            return holdings
        except Exception as e:
            logger.error(f"Error fetching holdings: {e}")
            return None

    def get_margins(self, segment=None):
        try:
            margins = self.kite.margins(segment=segment)
            logger.info(f"Fetched margins for segment: {segment}")
            return margins
        except Exception as e:
            logger.error(f"Error fetching margins: {e}")
            return None

    def get_gtt_orders(self):
        try:
            gtt_orders = self.kite.get_gtt_orders()
            logger.info("Fetched GTT orders.")
            return gtt_orders
        except Exception as e:
            logger.error(f"Error fetching GTT orders: {e}")
            return None

    def place_gtt_order(self, tradingsymbol, exchange, transaction_type, instrument_token, trigger_price, quantity, price, order_type, product):
        try:
            gtt_id = self.kite.place_gtt(
                tradingsymbol=tradingsymbol,
                exchange=exchange,
                transaction_type=transaction_type,
                instrument_token=instrument_token,
                trigger_price=trigger_price,
                quantity=quantity,
                price=price,
                order_type=order_type,
                product=product
            )
            logger.info(f"GTT order placed successfully. GTT ID: {gtt_id}")
            return gtt_id
        except Exception as e:
            logger.error(f"Error placing GTT order: {e}")
            return None

    def get_option_chain(self, exchange, tradingsymbol):
        # KiteConnect does not have a direct option chain method. 
        # This would typically involve fetching all instruments for the exchange
        # and then filtering for options related to the tradingsymbol.
        # For a real-world scenario, you might need to use a third-party data provider
        # or parse data from a web source if Zerodha's API doesn't provide it directly.
        logger.warning("KiteConnect does not have a direct option chain method. Implement custom logic.")
        return []




