# bairy

> Display data from Raspberry Pi.

Suppose you have a Raspberry Pi IoT-style devices on a local network that measures and records data. `bairy` provides a framework to share the data across the local network. If you have many devices each gathering data, `bairy` allows data to be shared through a single centralized hub which can combine and display results.

## Install

This package requires at least Python 3.7. The following instruction work for Raspbian 10 running on a Raspberry Pi B+.

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

1. Point your browser to `0.0.0.0:8000/status`. Refreshing, you should see the random sensor readings change every second. Also try `0.0.0.0:8000\plot`.

1. Going back to your terminal, press CTRL + C to stop `bairy`. Simply run `bairy` again to continue recording data.

1. To remove stored data and random configurations, run `bairy --remove all`.

## Details

### Configuration

Once your Raspberry Pi is equipped with sensors, `bairy` must be configured to be made aware of those sensors. Run `bairy --help` to view some of the configuration options. As an example, run `bairy --configs-template` to create a file named `template_configs.json` as a template. This file can be edited to include details about the sensors on the Raspberry Pi. After modifying the json file, add the configurations to `bairy` with `bairy --set-configs template_configs.json`.

### App endpoints

When `bairy` is configured then run on a Raspberry Pi, several processes start. Through an asynchronous event loop, `bairy` reads the values of the sensors and writes them to a `data.csv` file. Concurrently, `bairy` serves a `FastAPI`-backed web app that the user can interactive with. This web app can be accessed on the Raspberry Pi itself through the address `127.0.0.1:8000` or `0.0.0.0:8000` or `localhost:8000`.

The app includes various endpoints, described below. To navigate to the endpoint `/logs`, point your browser to `0.0.0.0:8000/logs`.

- `/data` Returns a streaming response of the `data.csv` file.
- `/logs` Displays the app logs as plaintext.
- `/status` Displays a pretty-printed json showing active configurations and device status.
- `/experimental` Can be used to update `bairy` and reboot the Raspberry Pi. See the [app source](#bairy/device/app.py).
- `/table` Renders a Dash table showing recent data.
- `/plot` Renders a Dash plot showing averaged data.

### LAN access

The web app can be accessed on the LAN. When `bairy` is started in a command line, it will print its local IP address. This IP address might take the form `192.168.0.17`. To access the `bairy` web app on a different machine on the network, point your browser to `192.168.0.17:8000/status`. Here `/status` can be replaced with any of the endpoints above.

### Run on startup

To enable bairy to run when the Raspberry Pi starts, follow the steps below. This is especially useful in _headless_ mode, that is, when the Raspberry Pi is not attached to a monitor. See the [official documentation](#https://www.raspberrypi.org/documentation/linux/usage/systemd.md) for working with `systemd` on Raspberry Pi.

1. Run `bairy -s` to create the file `bairy.service`.

1. Copy the `bairy.service` file to the `systemd` directory.

   ```sh
   sudo cp bairy.service /etc/systemd/system/bairy.service
   ```

1. Run `sudo systemctl enable bairy.service` to enable it to run on startup.

## bairy hub

## License
