"""Run app and read sensor data."""

from __future__ import annotations
import os
import sys
import json
import argparse
from multiprocessing import Process
from bairy.device import configs, utils, app, device, validate
from bairy.hub import configs as hub_configs, app as hub_app, request
from bairy import create_service


def check_startup():
  """Check systemd for bairy."""
  path = '/etc/systemd/system'
  if os.path.exists(path):
    d = os.listdir(path)
    d = [n.split('.')[0] for n in d]
    if 'bairy' not in d:
      print('bairy is not will run on startup. To enable this, see the README.')


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
      '-c',
      '--set-configs',
      type=str,
      nargs=1,
      dest='configs_path',
      help='set configs by passing path/to/configs.json',
      required=False)

  parser.add_argument(
      '-r',
      '--set-random-configs',
      action='store_true',
      help='set configs with random sensors',
      required=False)

  parser.add_argument(
      '-p',
      '--print-configs',
      action='store_true',
      help='print current configs',
      required=False)

  parser.add_argument(
      '-t',
      '--configs-template',
      action='store_true',
      help='create configs.json template',
      required=False)

  parser.add_argument(
      '-rm',
      '--remove',
      type=str,
      nargs=1,
      choices=['data', 'logs', 'configs', 'all'],
      help='remove saved data',
      required=False)

  parser.add_argument(
      '-d',
      '--print-data-path',
      action='store_true',
      help='print path to data directory',
      required=False)

  parser.add_argument(
      '-s',
      '--create-service',
      action='store_true',
      help='create bairy.service file for systemd',
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
  check_startup()

  if args.mode == 'device':
    if args.configs_path:
      configs.set_configs(args.configs_path[0])
    elif args.set_random_configs:
      configs.set_random_configs()
    elif args.print_configs:
      print(json.dumps(configs.load_configs().dict(), indent=4))
    elif args.configs_template:
      with open('template_configs.json', 'w') as f:
        f.write(json.dumps(validate.example_configs().dict(), indent=4))
        print('Created template_configs.json file.')

    elif args.remove:
      parse_remove(args.remove[0])
    elif args.print_data_path:
      print(configs.DATA_PATH)
    elif args.create_service:
      create_service.create_service_file()

    else:
      if not os.path.exists(configs.CONFIGS_PATH):
        raise FileNotFoundError('No configurations found! Run bairy --help')
      utils.print_local_ip_address()
      p = Process(target=app.run_app)
      p.start()
      device.run_device()

  elif args.mode == 'hub':
    if args.configs_path:
      hub_configs.set_ips(args.configs_path[0])
      request.validate_names()
    elif args.print_configs:
      print(json.dumps(hub_configs.load_ips(), indent=4))
    elif args.remove:
      raise NotImplementedError
    elif args.create_service:
      raise NotImplementedError
    else:
      if not os.path.exists(hub_configs.IP_PATH):
        raise FileNotFoundError('No IP addresses found! Run bairy --help')
      utils.print_local_ip_address()
      p = Process(target=hub_app.run_app)
      p.start()
      request.run_requests()

  else:
    assert args.mode == 'both'
    raise NotImplementedError


if __name__ == '__main__':
  main()
