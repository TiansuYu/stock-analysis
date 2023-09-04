import logging

import plotly.graph_objs as go
from dash import Dash, dcc, html, Input, Output
from dash.dependencies import State
from pydantic import ValidationError

from src.constants import XAXIS_CONFIG
from stock.ticker_data import TickerData

logger = logging.getLogger(__name__)
app = Dash(__name__)

EXTRA_OPTION = "extra_option"
OPTIONS = "options"
TICKER = "ticker"
PREDEFINED_TICKERS = ["AMZN", "META", "NFLX", "TSLA", "IVV", "EXXT.F"]

app.layout = html.Div([
    html.H4('Auth: Tiansu Yu'),
    dcc.Graph(id="time-series-chart"),
    html.P("Select stock:"),
    dcc.Dropdown(
        id=TICKER,
        options=PREDEFINED_TICKERS,
        value="IVV",
        clearable=False,
        multi=True,
    ),
    dcc.Input(
        id=EXTRA_OPTION,
        type="text",
        placeholder="Add an extra stock ticker",
        debounce=True,
    )
])


def _parse_tickers(tickers):
    if isinstance(tickers, list):
        return tickers
    elif isinstance(tickers, str):
        return [tickers]
    else:
        raise TypeError(f"Unrecognized type '{tickers.type}' for tickers '{tickers}'.")


@app.callback(
    Output(TICKER, OPTIONS),
    [Input(EXTRA_OPTION, "value")],
    [State(TICKER, OPTIONS)])
def update_options(value, existing_options):
    try:
        TickerData.validate_ticker(value)
        existing_options += [value]
    except (AssertionError, ValidationError):
        logger.warning(f"Invalid ticker '{value}'")
    return existing_options


@app.callback(
    Output("time-series-chart", "figure"),
    Input("ticker", "value"))
def display_time_series(tickers):
    fig = go.Figure()
    tickers = _parse_tickers(tickers)
    for ticker in tickers:
        ticker_data = TickerData(ticker=ticker)
        fig.add_trace(
            go.Scatter(x=ticker_data.data.index, y=ticker_data.data["Close"], mode="lines", name=ticker_data.long_name))
    fig.update_yaxes(tickprefix='$')
    fig.update_layout(title="Stock price analysis", xaxis_title="Date", yaxis_title="Price", hovermode="x",
                      xaxis=XAXIS_CONFIG)
    return fig


if __name__ == "__main__":
    app.run_server(debug=True)
