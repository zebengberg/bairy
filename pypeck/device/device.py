"""Control IoT device by reading sensor values and writing data to disk."""

from __future__ import annotations
import os
import asyncio
from datetime import datetime
from pypeck.device.configs import DATA_PATH, DATE_FORMAT, load_configs, read_last_line
from pypeck.device.sensors import read_air, read_random


class Device:
  """A class to control IoT device."""

  def __init__(self):
    configs = load_configs()
    self.name: str = configs['name']
    self.sensors: list[str] = configs['sensors']
    self.update_interval: int = configs['update_interval']
    self.data: dict[str, int] | None = None
    self.create_data_file()

  def create_data_file(self):
    """Create data file if none exists and write column headers."""

    # taking an initial reading to get header values
    data = self.read_sensors()
    if data is None:
      raise ConnectionError('Unable to connect to sensor!')
    headers = data.keys()

    if not os.path.exists(DATA_PATH):
      headers = 'time,' + ','.join(headers) + '\n'
      with open(DATA_PATH, 'w') as f:
        f.write(headers)

    else:  # getting the last known reading
      with open(DATA_PATH) as f:
        last_line = read_last_line()
        values = last_line.split(',')[1:]
        values = [int(v) for v in values]
        self.data = dict(zip(headers, values))

  def read_sensors(self):
    """Read sensor values."""
    data: dict[str, int] = {}
    for sensor in self.sensors:
      if sensor == 'air':
        reading = read_air()
      elif sensor == 'random':
        if self.data is not None:
          prev_reading = self.data['random']
        else:
          prev_reading = None
        reading = read_random(prev_reading)
      else:
        raise NotImplementedError

      if reading is None:
        return None
      for k in reading:
        if k in data:
          raise KeyError('Duplicate key found!')
      data.update(reading)
    return data

  def alarm(self):
    """Sound an alarm if values exceed a threshold."""

  def write_data(self):
    """Create a data file if none exists and append data to end."""
    time = datetime.now().strftime(DATE_FORMAT)
    self.data = self.read_sensors()
    if self.data is not None:
      row = time + ',' + ','.join(str(v) for v in self.data.values()) + '\n'
      with open(DATA_PATH, 'a') as f:
        f.write(row)

  async def run(self):
    """Call write_data indefinitely."""
    while True:
      await asyncio.sleep(self.update_interval)
      self.write_data()


def run_device():
  """Create an instance of device and run foreever."""
  d = Device()
  loop = asyncio.get_event_loop()
  loop.create_task(d.run())
  loop.run_forever()
