# EVA

Software for running an electric powered winch for paragliding. Designed for running on a normal Raspberry Pi with
ordinal touchscreen.

## Development

The used Kivy library runs on desktop display servers too, but needs some additional configuration. Use

    ./dev -- -d -i 3 can0

for starting the application for testing during development. Furthermore the development starter currently uses Python2
because Kivy is broken on Ubuntu 17.10 with Python3.

## Runtime

For running on the Raspberry Pi start it with this command:

    ./eva -- -i 3 can0

The runtime starter uses Python3.

## Display

The display utilizes multiple pages using a Kivy PageLayout.

# Install Guide

Start with Raspbian Stretch lite image.

## raspi-config

* hostname eva
* timezone Europe/Berlin
* keyboard: German
* enable SSH
* enable I²C

## Basic configuration

Copy SSH key.

## /etc/network/interfaces.d/eth0

    auto eth0
    iface eth0 inet static
        address 192.168.168.37
        netmask 255.255.255.0
        gateyway 192.168.168.1

## Packages

* nix

## s-usv

Use the correct version for the used version of the hardware:
[Download](https://shop.olmatic.de/de/content/7-downloads) 

    /opt/susvd/susvd -start

# CANopen

## PDO

### Transmission type

 * 0 acyclic synchronous
 * 1...240 cyclic synchronous
 * 241...251 reserved
 * 252 synchronous RTR only
 * 253 asynchronous RTR only
 * 254...255 asynchronous: transmit if one value of the PDO changed

