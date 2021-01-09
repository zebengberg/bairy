# pypeck

> Display data from Raspberry Pi.

Suppose you have a Raspberry Pi IoT-style devices on a local network that measures and records data. `pypeck` provides a framework to share the data across the local network. If you have many devices each gathering data, `pypeck` allows data to be shared with a single centralized hub which can combine and share the result.

## Install

This project can be run on both individual Raspberry Pi devices and a centralized hub (a machine that can function as a host).

### devices

The following instruction work for Raspbian running on a Raspberry Pi B+.

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

1. Create a `configs.json` file with the same format as the [test configs](#pypeck/device/test_config.json). Below is an example.

```json
{
  "name": "razzy",
  "location": "kitchen",
  "sensors": ["air", "random"],
  "update_interval": 5
}
```

This file should be located in the root directory of the project, at the same level as `setup.py`. This step can be skipped to run the device with a random sensor.

1. Register your configurations with the `device` module.

```sh
python3 -m pypeck.device.configs path/to/configs.json
```

This module can also be run with `--remove-configs`, `--remove-data`, `--remove-logs` instead of the `path/to/configs.json` argument above.

1. Run the main module to launch the web app and start collecting data.

```sh
python3 -m pypeck.device.app
```

Point your web browser in to `0.0.0.0:8000` to test the app. Other endpoints include:

- `0.0.0.0:8000/data`
- `0.0.0.0:8000/configs`
- `0.0.0.0:8000/logs`
- `0.0.0.0:8000/plot`
- `0.0.0.0:8000/table`

Take note of the IP address printed out to the terminal; you will need this for connection over your LAN.

1. Add the command

```sh
PYTHONPATH="path/to/pip/install/of/pypeck" \
            python3 -m pypeck.device.app &
```

to the `rc.local` file in order to run the app on startup in headless mode. Because this script will be executed as root, the variable `PYTHONPATH` needs to include any directories in which pip installs packages. See [here](#https://www.raspberrypi.org/documentation/linux/usage/rc-local.md).

1. Power your Raspberry Pi in headless mode and try to access an endpoint from another machine on the local network. If the IP address from the previous step is `192.168.xxx.yyy`, point your browser to `192.168.xxx.yyy:8000`. Try each of the endpoints listed above.

### hub

Follow the first two steps as for devices. That is, install this project and its dependencies. In addition, you will also need to know the IP addresses of all devices you intend to connect to the hub. These IP addresses should be stored in a `.txt` file.

1. Run `python -m pypeck.hub.configs path/to/addresses.txt`.

1.
