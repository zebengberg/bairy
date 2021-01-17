"""Test all hub app endpoints."""

from fastapi.testclient import TestClient
from bairy.hub.app import app
from bairy.hub.request import validate_names
from bairy.hub.configs import load_ips


client = TestClient(app)


def test_ip_addresses_exists():
  """Confirm that the hub has stored ip addresses."""
  load_ips()
  validate_names()


def test_all_endpoint_status():
  """Test all endpoints status code through openapi.json json."""
  r = client.get('/openapi.json')
  assert r.status_code == 200
  for e in r.json()['paths'].keys():
    r = client.get(e)
    assert r.status_code == 200

  for e in ['plot']:
    r = client.get(e)
    assert r.status_code == 200
