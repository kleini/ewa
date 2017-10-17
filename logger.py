import time
import can


def main():
    bus = can.interface.Bus('can0', bustype='socketcan')
    logger = can.Logger(None)
    notifier = can.Notifier(bus, [logger], timeout=0.1)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print('Shutdown')
        bus.shutdown()

if __name__ == '__main__':
    main()
