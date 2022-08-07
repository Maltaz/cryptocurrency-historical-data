from typing import Dict, List, Optional, Any
import binance
import pandas as pd
import math
import os.path
import time
from binance.client import Client
from datetime import timedelta, datetime
from dateutil import parser
from tqdm import tqdm_notebook


class FetchCryptoCurrencyData:
    """An SDK for working with binance API and fetching cryptocurrency historical data.
    Full API documentation is available here: https://python-binance.readthedocs.io/en/latest/
    """

    def __init__(self):

        # CONSTANS
        self.api_key = 'Your Api Key'
        self.api_secret = 'Your Api Secret'
        self.bin_sizes = {"1m": 1, "5m": 5, "1h": 60, "1d": 1440}
        self.batch_size = 750

        # INITIALIZE
        self.binance_client: Optional[binance.client.Client] = None

        # GET
        self.wallet_crypto_details: Optional[List[dict]] = []
        self.wallet_crypto_change24: Optional[List[dict]] = []

    def main(self) -> bool:
        #TODO Refactor code to more "automation" style 
        if not self.initialize_binance():
            print("Failed to initialize binance client")
        else:
            return True
        return False

    def initialize_binance(self, binance_client_obj: Optional[binance.client.Client] = None) -> bool:
        """Initialize connection with Binance API.
        :param binance_client_obj:
        :return: True if successfully connected to API
        """
        if binance_client_obj:
            self.binance_client = binance_client_obj
        elif not binance_client_obj:
            self.binance_client = binance.Client(self.api_key, self.api_secret)
        return True

    def minutes_of_new_data(self, currency_symbol, kline_size, data, source) -> datetime:
        """Fetch old data from your csv file (if exist) and fetch newest data from Api
        :param currency_symbol:
        :param kline_size:
        :param data:
        :param source:
        :return: lastest saved data, newest data
        """
        if len(data) > 0:
            old = parser.parse(data["timestamp"].iloc[-1])
        elif source == "binance":
            old = datetime.strptime('1 Aug 2022', '%d %b %Y')
        if source == "binance":
            new = pd.to_datetime(self.binance_client.get_klines(symbol=currency_symbol, interval=kline_size)[-1][0],
                                 unit='ms')
        return old, new

    def get_historical_data(self, currency_symbol, kline_size, save=False):
        """Get needed cryptocurrency historical data and save to csv file.
        :param currency_symbol:
        :param kline_size:
        :param save:
        :return: Historical cryptocurrency data
        """
        filename = '%s-%s-data.csv' % (currency_symbol, kline_size)
        if os.path.isfile(filename):
            data_df = pd.read_csv(filename)
        else:
            data_df = pd.DataFrame()

        oldest_point, newest_point = self.minutes_of_new_data(currency_symbol, kline_size, data_df, source="binance")
        delta_min = (newest_point - oldest_point).total_seconds() / 60
        available_data = math.ceil(delta_min / self.bin_sizes[kline_size])

        if oldest_point == datetime.strptime('1 Aug 2022', '%d %b %Y'):
            print('Downloading all available %s data for %s. You have to wait..!' % (kline_size, currency_symbol))
        else:
            print('Downloading %d minutes of new data available for %s, i.e. %d instances of %s data.'
                  % (delta_min, currency_symbol, available_data, kline_size))

        klines = self.binance_client.get_historical_klines(currency_symbol, kline_size,
                                                           oldest_point.strftime("%d %b %Y %H:%M:%S"),
                                                           newest_point.strftime("%d %b %Y %H:%M:%S"))
        data = pd.DataFrame(klines,
                            columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_av',
                                     'trades', 'tb_base_av', 'tb_quote_av', 'ignore'])
        data['timestamp'] = pd.to_datetime(data['timestamp'], unit='ms')

        if len(data_df) > 0:
            temp_df = pd.DataFrame(data)
            data_df = data_df.append(temp_df)
        else:
            data_df = data

        data_df.set_index('timestamp', inplace=True)

        if save:
            data_df.to_csv(filename)
        print('All caught up..!')

        return data_df


test = FetchCryptoCurrencyData()
test.initialize_binance()
test.get_historical_data("BTCUSDT", "5m", True)
