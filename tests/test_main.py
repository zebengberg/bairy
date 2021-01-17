"""Test __main__ argparse."""

import os
from bairy.__main__ import parse_args
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
  assert args.configs_path == ['fake_path']

  args = parse_args(['--remove', 'logs'])
  assert args.remove == ['logs']


def test_service():
  create_service.create_service()
