# pypeck

> Display data from Raspberry Pi.

Suppose you have several Raspberry Pi IoT-style devices on a local network. Each device has one or more sensors which measure and record data. `pypeck` provides a framework for these devices to report data to a single centralized hub, which in turn can share the data with users across the local network.

## Install

This project is intended to run on both individual Raspberry Pi devices and a centralized hub (a machine that can function as a host). All of these must be configured.

### devices

The following instruction work for Raspbian 10.

1. Install the dependencies for the `numpy`-`pandas`-`scipy` suite.

```sh
sudo apt update
sudo apt install libatlas-base-dev
```

1. Clone this repository and cd into it. Install with pip.

```sh
git clone http://github.com/zebengberg/pypeck
cd pypeck
pip3 install .
```

1. Create a `configs.json` file with the same format as the [test configs](#pypeck/device/test_config.json).

```json
{
  "name": "test",
  "location": "test",
  "sensors": ["random"],
  "update_interval": 1
}
```

This file should be located in the root directory of the project, at the same level as `setup.py`. This step can be skipped to run the device in `test_mode`.

1. Run the shell script with `$ ./device.sh`. Point your web browser in to `0.0.0.0:8000` to test the webapp. Other endpoints include:

- `0.0.0.0:8000/data`
- `0.0.0.0:8000/configs`
- `0.0.0.0:8000/logs`
- `0.0.0.0:8000/plot`

1. Add this shell script to the `rc.local` to run on startup in headless mode. See [here](#https://www.raspberrypi.org/documentation/linux/usage/rc-local.md).

1. Power your Raspberry Pi in headless mode and try to access an endpoint from another machine on the local network. If the IP address from the previous step is `192.168.xxx.yyy`, point your browser to `192.168.xxx.yyy:8000`. Try each of the endpoints defined in the [app](#pypeck/device/app.py).
