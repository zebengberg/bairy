"""Display gathered data."""

import os
import pandas as pd
from dash import Dash
import dash_core_components as dcc
import dash_html_components as html
import plotly
import plotly.express as px
# from bairy.hub.request import DATA_DIR, get_data_once, get_devices

from fastapi import FastAPI
import uvicorn
from starlette.middleware.wsgi import WSGIMiddleware


def build_dash_app(px_fig: plotly.graph_objects.Figure):
  """Build dash app to bundle through WSGIMiddleware."""
  css = 'https://stackpath.bootstrapcdn.com/bootswatch/4.5.2/united/bootstrap.min.css'
  dash_app = Dash(__name__, requests_pathname_prefix='/dash/',
                  external_stylesheets=[css])

  dash_app.layout = html.Div(children=[
      html.H1(children='bairy'),
      html.Div(children='Display data from Raspberry Pi.'),
      dcc.Graph(id='plot', figure=px_fig)
  ])


# USE_CACHED = False
# RUN_AS_DEVICE = True

# if RUN_AS_DEVICE:
#   DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'device', 'data')
#   path = os.path.join(DATA_DIR, 'data.csv')
#   devices = [{'name': 'test', 'df': pd.read_csv(path)}]
# else:
#   if USE_CACHED:
#     devices = get_devices()
#   else:
#     devices = get_data_once()

#   for d in devices:
#     path = os.path.join(DATA_DIR, d['name'] + '.csv')
#     # adding new key to device dict
#     d['df'] = pd.read_csv(path)


# TODO: show alarm thresholds
# TODO: combine separate dfs into one?
# df = devices[0]['df']
# fig = px.line(df, x='time', y=['air', 'temp'], title='Sensor Readings')


# if __name__ == '__main__':
#   # app.run_server(debug=True, host='127.0.0.1', port=8000)
#   server = FastAPI()
#   server.mount('/', WSGIMiddleware(app.server))
#   uvicorn.run(server, host='0.0.0.0', port=8000)
