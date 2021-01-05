"""Control IoT device by reading sensor values and writing data to disk."""

import os
import asyncio
from random import randint
from datetime import datetime
from itertools import cycle
from airview.device.configs import DATA_PATH, CONFIGS, DATE_FORMAT


class Device:
  """A class to control IoT device."""

  def __init__(self):
    self.name: str = CONFIGS['name']
    self.sensors: list[dict[str, str]] = CONFIGS['sensors']
    self.create_data_file()
    self.update_interval: int = CONFIGS['update_interval']
    self.test_mode = self.name == 'test'
    self.test_reading = [randint(0, 1023) for _ in self.sensors]

  def create_data_file(self):
    """Create data file if none exists and write column headers."""
    headers = [s['name'] for s in self.sensors]
    headers = 'time,' + ','.join(headers) + '\n'
    if not os.path.exists(DATA_PATH):
      with open(DATA_PATH, 'w') as f:
        f.write(headers)

  def read_sensors(self):
    """Read sensor values."""
    if self.test_mode:
      self.test_reading = [v + randint(-3, 3) for v in self.test_reading]
      # clipping to 0, 1023 range
      self.test_reading = [max(min(v, 1023), 0) for v in self.test_reading]
      return self.test_reading
    raise NotImplementedError

  def alarm(self):
    """Sound an alarm if values exceed a threshold."""

  def write_data(self):
    """Create a data file if none exists and append data to end."""
    time = datetime.now().strftime(DATE_FORMAT)
    values = self.read_sensors()
    row = time + ',' + ','.join(str(v) for v in values) + '\n'
    with open(DATA_PATH, 'a') as f:
      f.write(row)

  async def run(self):
    """Call write_data indefinitely."""
    for i in cycle(r'-\|/'):
      await asyncio.sleep(self.update_interval)
      print('\r', i, sep='', end='', flush=True)
      self.write_data()


if __name__ == '__main__':
  d = Device()
  loop = asyncio.get_event_loop()
  loop.create_task(d.run())
  loop.run_forever()
