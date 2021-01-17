"""Validate configs with pydantic. Sensor fields are chosen so that
d -> Device(**d.dict()) is an involution."""


# cannot use __future__ annotations with pydantic
from typing import List, Union
from pydantic import BaseModel, validator


class AirSensorConfigs(BaseModel):
  sensor_type: str = 'air'
  i2c_address: int

  @validator('sensor_type')
  def check_sensor_type(cls, value: str):
    assert value == 'air'
    return value


class DigitalSensorConfigs(BaseModel):
  sensor_type: str = 'digital'
  bcm_pin: int
  header: str

  @validator('sensor_type')
  def check_sensor_type(cls, value: str):
    assert value == 'digital'
    return value


class RandomSensorConfigs(BaseModel):
  sensor_type: str = 'random'
  header: str

  @validator('sensor_type')
  def check_sensor_type(cls, value: str):
    assert value == 'random'
    return value


class DeviceConfigs(BaseModel):
  """A Class holding configuration fields of the device."""
  name: str
  sensors: List[Union[AirSensorConfigs,
                      DigitalSensorConfigs,
                      RandomSensorConfigs]]
  update_interval: int


def random_configs():
  """Return a device with a random sensor."""
  s1 = RandomSensorConfigs(sensor_type='random', header='random1')
  s2 = RandomSensorConfigs(sensor_type='random', header='random2')
  s3 = RandomSensorConfigs(sensor_type='random', header='random3')
  d = DeviceConfigs(
      name='random sensors',
      sensors=[s1, s2, s3],
      update_interval=1)
  assert d == DeviceConfigs(**d.dict())
  return d


def example_configs():
  """Return an example of valid configs as json."""
  s1 = AirSensorConfigs(sensor_type='air', i2c_address=0x12)
  s2 = DigitalSensorConfigs(sensor_type='digital',
                            bcm_pin=17, header='ir_state')
  s3 = DigitalSensorConfigs(sensor_type='digital',
                            bcm_pin=27, header='sound_state')
  d = DeviceConfigs(
      name='example sensors',
      sensors=[s1, s2, s3],
      update_interval=1)
  assert d == DeviceConfigs(**d.dict())
  return d
