# bairy

> Display data from Raspberry Pi.

Suppose you have a Raspberry Pi IoT-style device on a local network that measures and records data. `bairy` provides a framework to share the data across the local network. `bairy` has the ability to combine, centralize, and display results gathered from multiple devices.

## Install

This package requires at least Python 3.7. The following instructions work for Raspbian 10 running on a Raspberry Pi B+.

1. Install the dependencies for the `numpy`-`pandas`-`scipy` suite.

   ```sh
   sudo apt update
   sudo apt install libatlas-base-dev
   ```

1. Install this package with `pip3 install bairy`. If `pip3` is not recognized, try `python3 -m pip install bairy`.

1. Try out `bairy` with random configurations.

   ```sh
   # initialize bairy with sensors that give random readings
   bairy --set-random-configs
   # run the app
   bairy
   ```

1. Point your web browser to `localhost:8000/status`. The sensor readings update every second -- refresh your browser to get the latest reading.

1. To stop `bairy`, go back to your terminal and press CTRL + C. Simply run `bairy` again to continue recording data.

1. To remove stored data and configurations, run `bairy --remove all`. Run `bairy --help` to see all command line options.

## Details

### Configuration

Once your Raspberry Pi is equipped with sensors, `bairy` must be configured to be made aware of those sensors. As an example, run `bairy --configs-template` to create a file named `template_configs.json` which can be edited to include details about the sensors. After modifying the json file, add the configurations to `bairy` with `bairy --set-configs template_configs.json`. Run `bairy` to capture sensor readings.

### App endpoints

When `bairy` is run, several processes start. Through an asynchronous event loop, `bairy` reads the values of the sensors and writes them to a `data.csv` file. Concurrently, `bairy` serves a `FastAPI`-backed web app with which the user can interact. This web app can be accessed on the Raspberry Pi itself through the url `127.0.0.1:8000` or `0.0.0.0:8000` or `localhost:8000`.

The app includes various endpoints, described below. To navigate to the endpoint `/logs`, point your browser to `localhost:8000/logs`.

- `/data` Returns a streaming response of the `data.csv` file.
- `/logs` Displays the app logs as plaintext.
- `/status` Displays a json object showing active configurations and device status.
- `/experimental` Can be used to update `bairy` and reboot the Raspberry Pi. See the [app source](#bairy/device/app.py).
- `/table` Renders a Dash table showing recent data.
- `/plot` Renders a Dash plot showing averaged data.

### LAN access

The web app can be accessed on the LAN. When `bairy` is run in the command line, it will print its local IP address. This IP address might take the form `192.168.0.17`. To access the `bairy` web app on a different machine on the network, navigate to `192.168.0.17:8000/status`. Here `/status` can be replaced with any of the endpoints above.

### Run at startup

To enable `bairy` to run when the Raspberry Pi starts, follow the steps below. This is especially useful in _headless_ mode, that is, when the Raspberry Pi is not attached to a monitor. See the [official documentation](https://www.raspberrypi.org/documentation/linux/usage/systemd.md) for more information on working with `systemd` on Raspberry Pi.

1. Run `bairy -s` to create `bairy.service` file in the `/etc/systemd/system` directory.

1. Run `sudo systemctl start bairy.service` to check if the service works.

1. Run `sudo systemctl stop bairy.service` to stop the service works.

## Central `hub`

If you have several Raspberry Pis simulataneously collecting and sharing data, `bairy` allows you to merge and share the data through a common web app. This central `hub` can be run on one of the Raspberry Pis, or on an independent device.

## License

MIT
