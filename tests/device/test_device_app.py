"""Test all device app endpoints."""

import os
from io import BytesIO
import pandas as pd
from fastapi.testclient import TestClient
from bairy.device.app import app
from bairy.device import validate, configs


client = TestClient(app)


def test_data_path_exists():
  """Confirm that the device has saved data."""
  assert os.path.exists(configs.DATA_PATH)


def test_all_endpoint_status():
  """Test all endpoints status code through openapi.json json."""
  r = client.get('/openapi.json')
  assert r.status_code == 200
  for k, v in r.json()['paths'].items():
    if 'get' in v:
      r = client.get(k)
      assert r.status_code == 200

  for e in ['plot', 'table']:
    r = client.get(e)
    assert r.status_code == 200


def test_root():
  """Test root endpoint."""
  r = client.get('/')
  # assert redirecting to plot
  assert 'plot' in r.url.split('/')


def test_data():
  """Test data endpoint."""
  r = client.get('/data')
  df = pd.read_csv(BytesIO(r.content))

  r = client.get('status')
  d = r.json()
  headers = d['latest_reading'].keys()
  n_rows = d['data_details']['n_rows']

  assert list(df.columns) == list(headers)
  assert len(df) == n_rows - 1  # don't want to count headers


def test_logs():
  """Test logs endpoint."""
  r = client.get('/logs')
  assert 'INFO' in r.text
  assert 'Uvicorn' in r.text


def test_status():
  """Test status endpoint."""
  r = client.get('/status')
  d = r.json()
  assert 'device_configs' in d
  assert 'data_details' in d
  assert 'latest_reading' in d
  assert 'time' in d['latest_reading']
  assert 'available_disk_space' in d
  assert 'bairy_version' in d
  assert 'ip_address' in d


def test_fake_endpoint():
  """Ensure a fake endpoint returns 404."""
  r = client.get('/fake')
  assert r.status_code == 404


def test_set_configs():
  """Test set-configs endpoint."""
  d = validate.random_configs().dict()
  r = client.post('/set-configs', json=d)
  assert r.status_code == 200


test_set_configs()
