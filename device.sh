#!/bin/bash

python -m pypeck.device.device &
python -m pypeck.device.app

trap 'kill $(jobs -p)' EXIT