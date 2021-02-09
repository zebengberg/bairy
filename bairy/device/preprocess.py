"""Preprocess data for Plotly/Dash."""

from __future__ import annotations
import itertools
import asyncio
import pandas as pd
from bairy.device import configs


def determine_plot_configs():
  """Determine plotly axes and variables configurations."""

  d = configs.load_device()
  # the order of the dictionaries below matter for plot tracing
  # order is least important to most important
  sensor_headers: dict[str, list[str]] = {'random': [],
                                          'digital': [],
                                          'air': []}
  sensor_units = {'random': 'random',
                  'digital': 'intensity',
                  'air': 'micrograms / cubic meter'}

  for s in d.sensors:
    if s.sensor_type == 'air':
      sensor_headers['air'] += ['pm_1.0', 'pm_2.5', 'pm_10']
    else:
      sensor_headers[s.sensor_type].append(s.header)

  # cleanup dictionaries
  empties = [k for k in sensor_headers.keys() if sensor_headers[k] == []]
  for k in empties:
    del sensor_headers[k]
    del sensor_units[k]

  # keeping at most two types of headers
  if len(sensor_headers) == 3:
    del sensor_headers['random']
    del sensor_units['random']

  return sensor_headers, sensor_units


def preprocess_df(time_period: str = 'all'):
  """Preprocess pandas DataFrame."""
  df = pd.read_csv(configs.DATA_PATH)

  df = df.set_index('time')
  df.index = pd.to_datetime(df.index)

  sensor_headers, _ = determine_plot_configs()
  cols_to_keep = [col for key in sensor_headers for col in sensor_headers[key]]
  df = df[cols_to_keep]

  if time_period == 'day':
    start = pd.Timestamp.now() - pd.Timedelta('1 day')
    df = df[df.index > start]
  elif time_period == 'week':
    start = pd.Timestamp.now() - pd.Timedelta('7 days')
    df = df[df.index > start]

  df = resample_df(df)
  return df.reset_index()  # move time back as a column


def resample_df(df):
  """Smooth and condense df by resampling."""
  # 60 has many divisors
  rules = ['1T', '2T', '3T', '4T', '5T', '6T', '10T', '20T', '30T', '1H']

  if len(df) > 300:  # only resample if df large enough
    for r in rules:
      df = df.resample(r).mean()
      if len(df) < 5000:
        break

  # smoothing even more
  df = df.rolling(7, center=True, min_periods=1).mean()
  return df


async def run_preprocess():
  """Run preprocessing indefinitely."""

  time_periods = list(configs.PREPROCESSED_DATA_PATHS.keys())

  async def run():
    for time_period in itertools.cycle(time_periods):
      df = preprocess_df(time_period)
      df.to_csv(configs.PREPROCESSED_DATA_PATHS[time_period])
      await asyncio.sleep(60)

  return await asyncio.create_task(run())
