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

# CANopen

## PDO

### Transmission type

 * 0 acyclic synchronous
 * 1...240 cyclic synchronous
 * 241...251 reserved
 * 252 synchronous RTR only
 * 253 asynchronous RTR only
 * 254...255 asynchronous: transmit if one value of the PDO changed

