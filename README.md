# pypeck

> Display data from Raspberry Pi.

Suppose you have several Raspberry Pi IoT-style devices on a local network. Each device has one or more sensors which measure and record data. `pypeck` provides a framework for these devices to report data to a single centralized hub, which in turn can share the data with users across the local network.

## install

Clone and install with pip.

```sh
git clone https://github.com/zebengberg/pypeck
pip install pypeck
```

## usage

The individual Raspberry Pi devices and the centralized hub (a machine that can function as a host) must be configured.

### devices

For each Raspberry Pi, do the following.

1. Create a `configs.json` file with the same format as the [test configs](#pypeck/device/test_config.json).
1. Run `python -m pypeck.device.configs path/to/your/config.json` to copy your configurations into the data directory (`~/pypeck_data/device/config.json`). To run device in _test mode_, skip this step.
1. Run processes in background.

```sh
python -m pypeck.device.device &
python -m pypeck.device.app &
```

1. How to kill them?
