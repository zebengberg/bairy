"""Dash app to plot device data."""

import os
import glob
import pandas as pd
from dash import Dash
from bairy.hub.configs import DATA_DIR, load_ips
from bairy.device.configs import DATA_DIR as DEVICE_DATA_DIR


def load_data():
  """Load cached data."""
  ip_addresses = load_ips()
  dfs = []
  if 'self' in ip_addresses:
    path = os.path.join(DEVICE_DATA_DIR, 'data.csv')
    dfs.append(pd.load_csv(path))
  for f in glob.glob(DATA_DIR + '*.csv'):
    dfs.append(pd.load_csv(f))

  dfs = [df['pm_2.5'] for df in dfs]
  return dfs


def serve_plot():
  """Serve dash app plot."""
  dfs = load_data()


css = 'https://codepen.io/chriddyp/pen/bWLwgP.css'
dash_plot = Dash(requests_pathname_prefix='/plot/', external_stylesheets=[css])
dash_plot.layout = serve_plot
