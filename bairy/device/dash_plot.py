"""Create dash plot for /plot endpoint."""

from __future__ import annotations
import os
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import plotly.io as pio
from dash import Dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
from bairy.device import configs, preprocess


pio.templates.default = 'plotly_white'


def create_fig(time_period: str = 'all'):
  """Create plotly figure using one or two y-axes."""

  data_path = configs.PREPROCESSED_DATA_PATHS[time_period]
  # avoiding errors before any data is captured
  if not os.path.exists(data_path):
    return go.Figure()

  fig = go.Figure()
  # see https://plotly.com/python/discrete-color/
  colors = iter(px.colors.qualitative.Bold)
  df = pd.read_csv(data_path)
  sensor_headers, sensor_units = preprocess.determine_plot_configs()

  for i, (key, cols) in enumerate(sensor_headers.items()):
    unit = sensor_units[key]
    if len(sensor_headers) == 2 and i == 0:
      side = 'right'
      opacity = 0.3
    else:
      side = 'left'
      opacity = 1.0

    yaxis = 'y' if i == 0 else 'y2'
    yaxis_layout = 'yaxis' if i == 0 else 'yaxis2'
    layout_params = {yaxis_layout: {'title': unit, 'side': side}}
    if i == 1:
      layout_params[yaxis_layout]['overlaying'] = 'y'

    for col in cols:
      # making some traces traces hidden
      if col in ['random3', 'pm_1.0', 'motion', 'sound']:
        visible = 'legendonly'
      else:
        visible = None

      fig.add_trace(go.Scatter(
          x=df['time'],
          y=df[col],
          name=col,
          opacity=opacity,
          line={'color': next(colors)},
          yaxis=yaxis,
          visible=visible
      ))

    fig.update_layout(**layout_params)

  # threshold for pm2.5
  if 'air' in sensor_headers and df['pm_2.5'].max() > 40:
    yaxis = 'y2' if len(sensor_headers) == 2 else 'y'
    fig.add_trace(go.Scatter(
        x=df['time'],
        y=[35] * len(df),
        name='pm_2.5 safe threshold',
        yaxis=yaxis,
        line={'dash': 'dot', 'color': next(colors)}
    ))

  name = configs.load_device().name
  if time_period == 'day':
    title = f'{name} data over last 24 hours'
  elif time_period == 'week':
    title = f'{name} data over last 7 days'
  else:
    title = f'{name} data over entire runtime'

  fig.update_layout(height=800, title=title)
  fig.layout.xaxis.rangeslider.visible = True
  fig.layout.yaxis.fixedrange = False
  return fig


css = 'https://codepen.io/chriddyp/pen/bWLwgP.css'
plot = Dash(
    __name__,
    requests_pathname_prefix='/plot/',
    external_stylesheets=[css]
)
plot.layout = html.Div(children=[
    # title and links
    html.Div(children=[
        html.H1(children='bairy', style={'fontWeight': 'bold'}),
        html.H3(children='Display sensor data from Raspberry Pi.'),
        html.A(
            'about bairy',
            href='https://github.com/zebengberg/bairy',
            style={'margin': '20px'}
        ),
        html.A(
            'table',
            href='/table',
            style={'margin': '20px'}
        )
    ]),

    # three plots
    dcc.Graph(id='plot_day'),
    dcc.Graph(id='plot_week'),
    dcc.Graph(id='plot_all'),

    # for plot update callback
    # see https: // dash.plotly.com/live-updates
    dcc.Interval(
        id='interval-component',
        interval=5 * 60 * 1000,  # 5 minutes
    )
])


@plot.callback(
    Output('plot_day', 'figure'),
    Input('interval-component', 'n_intervals')
)
def serve_plot_day(_):
  """Dynamically serve dash_plot.layout."""
  return create_fig('day')


@plot.callback(
    Output('plot_week', 'figure'),
    Input('interval-component', 'n_intervals')
)
def serve_plot_week(_):
  """Dynamically serve dash_plot.layout."""
  return create_fig('week')


@plot.callback(
    Output('plot_all', 'figure'),
    Input('interval-component', 'n_intervals')
)
def serve_plot_all(_):
  """Dynamically serve dash_plot.layout."""
  return create_fig('all')
