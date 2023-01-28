from dash import Dash, dcc, html, Input, Output
from dash.dependencies import State

from stock.stock import Stock, validate_ticker
import plotly.graph_objs as go
import logging

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
    if validate_ticker(value):
        existing_options += [value]
    return existing_options


@app.callback(
    Output("time-series-chart", "figure"),
    Input("ticker", "value"))
def display_time_series(tickers):
    fig = go.Figure()
    tickers = _parse_tickers(tickers)
    for ticker in tickers:
        stock = Stock(ticker)
        data = stock.get_data()
        long_name = stock.long_name
        fig.add_trace(go.Scatter(x=data.index, y=data["Close"], mode="lines", name=long_name))
    fig.update_yaxes(tickprefix='$')
    fig.update_layout(title="Stock price analysis", xaxis_title="Date", yaxis_title="Price", hovermode="x")
    return fig


if __name__ == "__main__":
    app.run_server(debug=True)
