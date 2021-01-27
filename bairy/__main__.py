"""Run app and read sensor data."""

from __future__ import annotations
import os
import shutil
import sys
import json
import glob
import argparse
import asyncio
from multiprocessing import Process
from bairy.device import configs, utils, app, device, validate
from bairy.hub import configs as hub_configs, app as hub_app, request
from bairy import create_service, log_configs


def parse_args(args: list[str]):
  """Create argparse parser."""
  parser = argparse.ArgumentParser()
  parser.add_argument(
      'mode',
      type=str,
      nargs='?',
      choices=['device', 'hub'],
      help='set the mode in which bairy runs',
      default='device')

  parser.add_argument(
      '-c',
      '--set-configs',
      type=str,
      nargs=1,
      dest='path',
      help='set configs (or IP addresses in hub mode) by passing path/to/configs.json',
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
      choices=['data', 'logs', 'configs', 'all', 'entire'],
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


def parse_device_remove(arg: str):
  """Parse --remove flag under device mode."""
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
  if arg == 'entire':
    if os.path.exists(configs.DATA_DIR):
      shutil.rmtree(hub_configs.DATA_DIR)
      print(f'Removed entire directory {hub_configs.DATA_DIR}')


def parse_hub_remove(arg: str):
  """Parse --remove flag under hub mode."""
  if arg in ['data', 'all']:
    data_files = glob.glob(hub_configs.HUB_DATA_DIR + '/*.csv') + \
        glob.glob(hub_configs.BACKUP_DIR + '/*.csv')
    for f in data_files:
      os.remove(f)
      print(f'Removed stored file at {f}')
  if arg in ['logs', 'all']:
    if os.path.exists(hub_configs.LOG_PATH):
      os.remove(hub_configs.LOG_PATH)
      print(f'Removed stored file at {hub_configs.LOG_PATH}')
  if arg in ['configs', 'all']:
    if os.path.exists(hub_configs.IP_PATH):
      os.remove(hub_configs.IP_PATH)
      print(f'Removed stored file at {hub_configs.IP_PATH}')
  if arg == 'entire':
    shutil.rmtree(hub_configs.DATA_DIR)


def parse_device(args: argparse.Namespace):
  """Take actions under device mode."""
  if args.path:
    configs.set_configs(args.path[0])
  elif args.set_random_configs:
    configs.set_random_configs()
  elif args.print_configs:
    print(json.dumps(configs.load_device().dict(), indent=4))
  elif args.configs_template:
    with open('template_configs.json', 'w') as f:
      f.write(json.dumps(validate.example_configs().dict(), indent=4))
      print('Created template_configs.json file.')
  elif args.remove:
    parse_device_remove(args.remove[0])
  elif args.print_data_path:
    print(configs.DATA_PATH)
  elif args.create_service:
    create_service.create_service()
  else:
    if not os.path.exists(configs.CONFIGS_PATH):
      raise FileNotFoundError('No configurations found! Run bairy --help')

    print('#' * 65)
    print('LOCAL IP ADDRESS:', utils.get_local_ip_address())
    print('#' * 65)
    p = Process(target=app.run_app)
    p.start()
    asyncio.run(device.run_device())


def parse_hub(args: argparse.Namespace):
  """Take actions under hub mode."""
  if args.path:
    hub_configs.set_ips(args.path[0])
    request.validate_names()
  elif args.print_configs:
    print(json.dumps(hub_configs.load_ips(), indent=4))
  elif args.remove:
    parse_hub_remove(args.remove[0])
  elif args.create_service:
    create_service.create_service(True)
  elif args.print_data_path:
    print(hub_configs.HUB_DATA_DIR)
  elif args.configs_template or args.set_random_configs:
    raise NotImplementedError('Not available for hub mode.')
  else:
    if not os.path.exists(hub_configs.IP_PATH):
      raise FileNotFoundError('No IP addresses found! Run bairy --help')

    print('#' * 65)
    print('LOCAL IP ADDRESS:', utils.get_local_ip_address())
    print('#' * 65)
    p = Process(target=hub_app.run_app)
    p.start()

    ip_addresses = hub_configs.load_ips()
    if 'self' in ip_addresses:
      task = asyncio.gather(device.run_device(), request.run_requests())
      asyncio.run(task)
    else:
      asyncio.run(request.run_requests())


def main():
  """Parse command line arguments and run actions."""
  args = parse_args(sys.argv[1:])
  if args.mode == 'device':
    log_configs.configure_root_logging(configs.LOG_PATH)
    parse_device(args)
  else:
    assert args.mode == 'hub'
    log_configs.configure_root_logging(hub_configs.LOG_PATH)
    parse_hub(args)


if __name__ == '__main__':
  main()
