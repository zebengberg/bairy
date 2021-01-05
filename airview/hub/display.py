"""Display gathered data."""

import os
import pandas as pd
from dash import Dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
from airview.hub.request import DATA_DIR, get_data_once, get_devices

from fastapi import FastAPI
import uvicorn
from starlette.middleware.wsgi import WSGIMiddleware


USE_CACHED = True
if USE_CACHED:
  devices = get_devices()
else:
  devices = get_data_once()

for d in devices:
  path = os.path.join(DATA_DIR, d['name'] + '.csv')
  # adding new key to device dict
  d['df'] = pd.read_csv(path)


css = 'https://stackpath.bootstrapcdn.com/bootswatch/4.5.2/united/bootstrap.min.css'
app = Dash(external_stylesheets=[css])

# TODO: show alarm thresholds
# TODO: combine separate dfs into one?
df = devices[0]['df']
fig = px.line(df, x='time', y=['air', 'temp'], title='Sensor Readings')

app.layout = html.Div(children=[
    html.H1(children='airview'),
    html.Div(children='Displaying IoT data from Raspberry Pi.'),
    dcc.Graph(id='plot', figure=fig)
])

if __name__ == '__main__':
  # app.run_server(debug=True, host='127.0.0.1', port=8000)
  server = FastAPI()
  server.mount('/', WSGIMiddleware(app.server))
  uvicorn.run(server, host='0.0.0.0', port=8000)
