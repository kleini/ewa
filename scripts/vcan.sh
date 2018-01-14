#!/usr/bin/env bash

modprobe vcan
ip link add dev can1 type vcan
ip link set up can1

ip link show

