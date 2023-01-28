from typing import Optional, Dict

import yfinance as yf
from datetime import datetime, timedelta
import pandas as pd
import logging

logger = logging.getLogger(__name__)

DATETIME_FORMAT = "%Y-%m-%d"
LONG_NAME = "long_name"


class Stock:

    def __init__(self, ticker: str, start: Optional[datetime] = None, end: Optional[datetime] = None) -> None:
        self.ticker = ticker
        self.start = start if start else self._default_start()
        self.end = end if end else self._default_end()
        self.info = _download_info(self.ticker)
        self.long_name = self.info["longName"]
        self._data = None

    def get_data(self) -> pd.DataFrame:
        if not self._data:
            self._download_data()
            # self._transform_data()
        return self._data

    def _transform_data(self) -> None:
        # self._data["long_name"] = self.long_name
        self._data.index = self._data.index.date

    def _download_data(self) -> None:
        self._data = self._download_data_from_yahoo(self.start, self.end)

    def _download_data_from_yahoo(self, start, end) -> pd.DataFrame:
        if isinstance(start, datetime):
            start = start.strftime(DATETIME_FORMAT)
        if isinstance(end, datetime):
            end = end.strftime(DATETIME_FORMAT)
        return yf.download(self.ticker, start=start, end=end)

    @staticmethod
    def _default_start() -> datetime:
        return datetime.utcnow() - timedelta(days=365)  # A year ago

    @staticmethod
    def _default_end() -> datetime:
        return datetime.today()


def _download_info(ticker) -> dict:
    return yf.Ticker(ticker).info


def validate_ticker(ticker) -> bool:
    try:
        info = _download_info(ticker)
        if info:
            return True
    except Exception:
        pass
    logger.error(f"Invalid ticker '{ticker}'")
    return False


if __name__ == "__main__":
    stock = Stock("AMZN")
    data = stock.get_data()
    print(data.head())
