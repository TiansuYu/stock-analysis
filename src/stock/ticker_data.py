from __future__ import annotations

import logging
from datetime import datetime, timedelta
from functools import cached_property

import pandas as pd
import yfinance as yf
from pydantic import BaseModel, Field, computed_field, model_validator, field_validator, ConfigDict

logger = logging.getLogger(__name__)

DATETIME_FORMAT = "%Y-%m-%d"
LONG_NAME = "longName"


def _default_start() -> datetime:
    return datetime.utcnow() - timedelta(days=365)  # A year ago


def _default_end() -> datetime:
    return datetime.today()


class TickerData(BaseModel):
    ticker: str = Field(frozen=True)
    start: datetime = Field(default_factory=_default_start)
    end: datetime = Field(default_factory=_default_end)

    model_config = ConfigDict(revalidate_instances="always",
                              arbitrary_types_allowed=True)

    @computed_field(repr=False)
    @cached_property
    def data(self) -> pd.DataFrame:
        _data = self._download_data()
        return self._transform_data(_data)

    @computed_field(repr=False)
    @cached_property
    def info(self) -> dict:
        return TickerData._get_info(self.ticker)

    @computed_field
    @cached_property
    def long_name(self) -> str:
        return self.info.get(LONG_NAME)

    @model_validator(mode="after")
    def start_should_be_before_end(self) -> TickerData:
        if self.start >= self.end:
            raise ValueError("Start date should be before end date")
        return self

    @field_validator("ticker")
    @classmethod
    def validate_ticker(cls, v: str) -> str:
        assert v is not None, "Ticker cannot be None!"
        assert cls._get_info(v), f"Could not find ticker '{v}' on Yahoo Finance!"
        return v

    @staticmethod
    def _transform_data(data: pd.DataFrame) -> pd.DataFrame:
        _data = data.copy()
        _data.index = _data.index.date
        return _data

    def _download_data(self) -> pd.DataFrame:
        start = self.start.strftime(DATETIME_FORMAT)
        end = self.end.strftime(DATETIME_FORMAT)
        return yf.download(self.ticker, start=start, end=end)

    @classmethod
    def _get_info(cls, ticker: str) -> dict:
        return yf.Ticker(ticker).info
