# pypeck

> Display data from Raspberry Pi.

Suppose you have several Raspberry Pi IoT-style devices on a local network. Each device has one or more sensors which measure and record data. `pypeck` provides a framework for these devices to report data to a single centralized hub, which in turn can share the data with users across the local network.

## Install

This project is intended to run on both individual Raspberry Pi devices and a centralized hub (a machine that can function as a host). All of these must be configured.

### devices

The easiest way to install the dependencies needed for this package is with Docker. Instructions are available for [Docker installation](#https://docs.docker.com/engine/install/debian/#install-using-the-convenience-script) on Raspbian.

1. Install docker. Add your non-root user to the Docker group to avoid constantly needing administrator privileges.

```sh
sudo usermod -aG docker $USER
```

1. Clone this repository.

```sh
git clone http://github.com/zebengberg/pypeck
```

1. Create a `configs.json` file with the same format as the [test configs](#pypeck/device/test_config.json).

```json
{
  "name": "test",
  "location": "test",
  "sensors": [
    { "name": "air", "pin": -1 },
    { "name": "temp", "pin": -1 }
  ],
  "update_interval": 1
}
```

This file should be in the root directory of the project, at the same level as `Dockerfile`.

1. Build the docker image.

```sh
docker build -t pypeck-device .
```

You will need to rebuild if you modify the `configs.json` file.

1. Run the docker image to confirm it works.

```sh
docker run -t pypeck-device
```

Point your web browser to `0.0.0.0:8000` to test the webapp. Other endpoints include:

- `0.0.0.0:8000/data`
- `0.0.0.0:8000/configs`
- `0.0.0.0:8000/logs`

1. Add the docker run command to `rc.local` to run on startup in headless mode. See [here](#https://www.raspberrypi.org/documentation/linux/usage/rc-local.md).

```sh
docker run -d pypeck-device
```

1. Power your Raspberry Pi in headless mode and try to access an endpoint from another machine on the local network. If the IP address from the previous step is `192.168.xxx.yyy`, point your browser to `192.168.xxx.yyy:8000`. Try each of the endpoints defined in the [app](#pypeck/device/app.py).
