#!/usr/bin/env bash

set -e

modprobe slcan
slcan_attach -f -s4 -o -n can0 /dev/ttyACM0 #125 kBaud
slcand ttyACM0 can0
ifconfig can0 up

