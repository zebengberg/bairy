"""Run app and read sensor data."""

from __future__ import annotations
import os
import sys
import json
import argparse
from multiprocessing import Process
from bairy.device import configs, utils, app, device


def check_startup():
  """Check raspberry pi rc.local for bairy."""
  path = '/etc/rc.local'
  if os.path.exists(path):
    with open(path) as f:
      content = f.read()
    if 'bairy' not in content:
      print('INFO: bairy will not automatically run when the device first starts.')
      print('      To change this, add bairy to /etc/rc.local. See the README.')


def parse_args(args: list[str]):
  """Create argparse parser."""
  parser = argparse.ArgumentParser()
  parser.add_argument(
      'mode',
      type=str,
      nargs='?',
      choices=['device', 'hub', 'both'],
      help='set the mode in which bairy runs',
      default='device')

  parser.add_argument(
      '--set-configs',
      type=str,
      nargs=1,
      dest='configs_path',
      help='set configs by passing path/to/configs.json',
      required=False)

  parser.add_argument(
      '--set-random-configs',
      action='store_true',
      help='set configs with random sensors',
      required=False)

  parser.add_argument(
      '--print-configs',
      action='store_true',
      help='print current configs',
      required=False)

  parser.add_argument(
      '--configs-template',
      action='store_true',
      help='create configs.json template',
      required=False)

  parser.add_argument(
      '--remove',
      type=str,
      nargs=1,
      choices=['data', 'logs', 'configs', 'all'],
      help='remove saved data',
      required=False)

  parser.add_argument(
      '--print-data-path',
      action='store_true',
      help='print path to data directory',
      required=False)

  return parser.parse_args(args)


def parse_remove(arg: str):
  """Parse --remove flag."""

  if arg in ['data', 'all']:
    if os.path.exists(configs.DATA_PATH):
      os.remove(configs.DATA_PATH)
      print(f'Removed stored file at {configs.DATA_PATH}')
  if arg in ['logs', 'all']:
    if os.path.exists(configs.LOG_PATH):
      os.remove(configs.LOG_PATH)
      print(f'Removed stored file at {configs.LOG_PATH}')
  if arg in ['configs', 'all']:
    if os.path.exists(configs.CONFIGS_PATH):
      os.remove(configs.CONFIGS_PATH)
      print(f'Removed stored file at {configs.CONFIGS_PATH}')


def main():
  """Parse command line arguments and run actions."""

  args = parse_args(sys.argv[1:])

  if args.mode != 'device':
    raise NotImplementedError('Only implemented for device.')

  if args.configs_path:
    configs.set_configs(args.configs_path)
  elif args.set_random_configs:
    configs.set_random_configs()
  elif args.print_configs:
    print(json.dumps(configs.load_configs().dict(), indent=4))
  elif args.configs_template:
    with open('test.json', 'w') as f:
      f.write('hello')

  elif args.remove:
    parse_remove(args.remove[0])
  elif args.print_data_path:
    print(configs.DATA_PATH)

  else:
    assert args.mode == 'device'
    utils.print_local_ip_address()
    p = Process(target=app.run_app)
    p.start()
    device.run_device()


if __name__ == '__main__':
  main()
