"""Read and define addresses and paths for the hub."""


import os
import sys
import glob


# creating data directory within module
MODULE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(MODULE_DIR, 'data')
IP_PATH = os.path.join(DATA_DIR, 'ip_addresses.txt')
LOG_PATH = os.path.join(DATA_DIR, 'app.logs')
UPDATE_INTERVAL = 60 * 60  # update every hour
if not os.path.exists(DATA_DIR):
  os.mkdir(DATA_DIR)


def set_addresses(path: str):
  pass


def read_ips():
  pass


if __name__ == '__main__':
  if len(sys.argv) < 2:
    raise ValueError('Expected path/to/ip_addresses.txt as additional arg!')
  arg = sys.argv[1]
  if arg == '--remove-addresses':
    os.remove(IP_PATH)
    print('Removed stored ip_addresses.txt')
  elif arg == '--remove-data':
    for f in glob.glob(DATA_DIR + '*.csv'):
      os.remove(f)
    print('Removed all stored data.')
  elif arg == '--remove-logs':
    os.remove(LOG_PATH)
    print('Removed stored app.logs')

  else:
    set_addresses(arg)
    print('Successfully set IP addresses')
