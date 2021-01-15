"""Test validate module."""

from bairy.device.validate import *


def test_sensor_configs():
  """Test various SensorConfigs models."""

  s = DigitalSensorConfigs(bcm_pin=17, header='random')
  assert s == DigitalSensorConfigs(**s.dict())

  s = RandomSensorConfigs(header='random')
  assert s == RandomSensorConfigs(**s.dict())

  s = AirSensorConfigs(i2c_address=0x12)
  assert s == AirSensorConfigs(**s.dict())


def test_device_configs():
  """Test DeviceConfigs model."""

  s1 = DigitalSensorConfigs(bcm_pin=17, header='random')
  s2 = RandomSensorConfigs(header='random')
  s3 = AirSensorConfigs(i2c_address=0x12)

  d = DeviceConfigs(
      name='razzy',
      location='garden',
      sensors=[s1, s2, s3],
      plot_axes={'foo': ['bar']},
      update_interval=17)

  assert d == DeviceConfigs(**d.dict())


def test_examples():
  """Use pydantic validator to test built in examples."""
  example_configs()
  random_configs()
