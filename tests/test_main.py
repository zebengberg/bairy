"""Test __main__ functions."""

import os
from bairy.__main__ import parse_args, parse_device, parse_hub
from bairy import create_service


def test_parser():
  """Test argparse command line arguments."""
  args = parse_args(['--print-configs'])
  assert args.print_configs

  args = parse_args(['--print-data-path'])
  assert args.print_data_path

  args = parse_args(['--create-service'])
  assert args.create_service

  args = parse_args(['--set-random-configs'])
  assert args.set_random_configs

  args = parse_args(['--set-configs', 'fake_path'])
  assert args.path == ['fake_path']

  args = parse_args(['--remove', 'logs'])
  assert args.remove == ['logs']


def test_service():
  """Test create_service()."""
  create_service.create_service()


def test_main():
  """Simulate several main flags."""
  args = parse_args(['-p'])
  parse_device(args)
  parse_hub(args)

  args = parse_args(['-d'])
  parse_device(args)
  parse_hub(args)

  args = parse_args(['-t'])
  parse_device(args)
  os.remove('template_configs.json')

  try:
    args = parse_args(['-rm foo'])
    parse_device(args)
    parse_hub(args)
  except SystemExit:
    pass
  else:
    raise ValueError
