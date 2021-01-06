"""Basic app endpoint testing."""

from io import BytesIO
import json
import pandas as pd
from fastapi.testclient import TestClient
from pypeck.device.app import app


client = TestClient(app)


def test_root():
  """Test root endpoint."""
  print('Testing / ...')
  r = client.get('/')
  assert r.status_code == 200
  print('Root response received:', r.json())


def test_data():
  """Test data endpoint."""
  print('Testing /data ...')
  r = client.get('/data')
  assert r.status_code == 200
  df = pd.read_csv(BytesIO(r.content))
  print('The first few rows of the data response as a pandas DataFrame:')
  print(df.head(10))


def test_logs():
  """Test logs endpoint."""
  print('Testing /logs ...')
  r = client.get('/logs')
  assert r.status_code == 200
  print('The final few rows of the log response:')
  for l in r.text.split('\n')[-10:]:
    print(l)


def test_configs():
  """Test configs endpoint."""
  print('Testing /configs ...')
  r = client.get('/configs')
  assert r.status_code == 200
  print('The response as json:')
  formatted = json.dumps(r.json(), indent=2)
  print(formatted)


if __name__ == '__main__':
  try:
    test_root()
    test_data()
    test_logs()
    test_configs()
  except FileNotFoundError as e:
    raise FileNotFoundError('Create data before testing the endpoints!') from e

  print('All tests pass.')
