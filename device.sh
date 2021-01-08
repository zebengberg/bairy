#!/bin/bash

python3 -m pypeck.device.device &
python3 -m pypeck.device.app

trap 'kill $(jobs -p)' EXIT