from bairy.device.validate import random_configs
from bairy.device.device import initialize_device


def test_device():
  """Load random configs and text device."""
  d = random_configs()
  _, sensors = initialize_device(d)
  for s in sensors:
    r1 = s.read()
    assert len(r1.values()) == 1
    r1 = list(r1.values())[0]
    assert r1 is not None

    r2 = s.read()
    assert len(r2.values()) == 1
    r2 = list(r2.values())[0]
    assert r2 is not None

    assert abs(r1 - r2) < 5
