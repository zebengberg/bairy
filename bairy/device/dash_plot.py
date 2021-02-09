"""Create dash plot for /plot endpoint."""

from __future__ import annotations
import os
import logging
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
  print(time_period)

  # avoiding errors before any data is captured
  if not os.path.exists(configs.DATA_PATH):
    return go.Figure()

  try:
    fig = go.Figure()
    # see https://plotly.com/python/discrete-color/
    colors = iter(px.colors.qualitative.Bold)
    df = preprocess.preprocess_df(time_period)
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
        fig.add_trace(go.Scatter(
            x=df['time'],
            y=df[col],
            name=col,
            opacity=opacity,
            line={'color': next(colors)},
            yaxis=yaxis
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

  except (KeyError, FileNotFoundError) as e:
    logging.warning(e)
    return go.Figure()


css = 'https://codepen.io/chriddyp/pen/bWLwgP.css'
dash_plot = Dash(
    requests_pathname_prefix='/plot/',
    external_stylesheets=[css]
)
dash_plot.layout = html.Div(children=[
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
    dcc.Graph(id='plot_day', figure=create_fig('day')),
    dcc.Graph(id='plot_week', figure=create_fig('week')),
    dcc.Graph(id='plot_all', figure=create_fig('all')),

    # for plot update callback
    # see https://dash.plotly.com/live-updates
    dcc.Interval(
        id='interval-component',
        interval=60 * 1000,  # in milliseconds
        n_intervals=0  # an unused counter
    )
])


# @dash_plot.callback(
#     Output('plot_day', 'figure'),
#     Input('interval-component', 'n_intervals')
# )
# def serve_plot_day(n_intervals: int):
#   """Dynamically serve dash_plot.layout."""
#   logging.info('n_intervals: %s', n_intervals)
#   return create_fig('day')


# @dash_plot.callback(
#     Output('plot_week', 'figure'),
#     Input('interval-component', 'n_intervals')
# )
# def serve_plot_week(_):
#   """Dynamically serve dash_plot.layout."""
#   return create_fig('week')


# @dash_plot.callback(
#     Output('plot_all', 'figure'),
#     Input('interval-component', 'n_intervals')
# )
# def serve_plot_all(_):
#   """Dynamically serve dash_plot.layout."""
#   return create_fig('all')
