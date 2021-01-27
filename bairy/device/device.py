"""Control IoT device by reading sensor values and writing data to disk."""

from __future__ import annotations
import os
import asyncio
from datetime import datetime
from bairy.device.validate import DeviceConfigs
from bairy.device.configs import DATA_PATH, load_device
from bairy.log_configs import DATE_FORMAT
from bairy.device.sensor import Sensor


def read_sensors(sensors: list[Sensor]):
  """Read sensor values."""
  data: dict[str, int | None] = {}
  for s in sensors:
    reading = s.read()
    for k in reading:
      if k in data:
        raise KeyError('Duplicate key found!')
    data.update(reading)
  return data


def write_data(data: dict[str, int | None]):
  """Create a data file if none exists and append data to end."""
  time = datetime.now().strftime(DATE_FORMAT)
  values_as_str = [str(v) if v is not None else '' for v in data.values()]
  row = time + ',' + ','.join(values_as_str) + '\n'
  with open(DATA_PATH, 'a') as f:
    f.write(row)


def create_data_file(sensors: list[Sensor]):
  """Create data file if none exists and write column headers, or return most recent data."""

  # taking an initial reading to get header values
  data = read_sensors(sensors)
  headers = data.keys()

  if not os.path.exists(DATA_PATH):
    headers = 'time,' + ','.join(headers) + '\n'
    with open(DATA_PATH, 'w') as f:
      f.write(headers)


def initialize_device(device: DeviceConfigs | None = None):
  """Helper function for run device."""
  if device is None:
    device = load_device()
  sensors = [Sensor(s) for s in device.sensors]
  create_data_file(sensors)
  return device, sensors


async def run_device():
  """Run device indefinitely."""
  device, sensors = initialize_device()

  async def run():
    while True:
      data = read_sensors(sensors)
      write_data(data)
      await asyncio.sleep(device.update_interval)

  return await asyncio.create_task(run())
