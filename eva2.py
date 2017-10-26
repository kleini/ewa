import argparse
import canopen
import time


def main():
    parser = argparse.ArgumentParser(description='EVA')
    parser.add_argument('dev', metavar='<CAN device name>', help='CAN device name')
    parser.add_argument('-i', default=42, type=int, choices=range(1, 3), required=False, help='canopen Node ID')
    args = parser.parse_args()

    print('Starting EVA')

    network = canopen.Network()

    network.connect(bustype='socketcan', channel=args.dev)

    node = network.add_node(args.i, 'CO4011A0.eds')

    other = network.add_node(7, 'CO4011A0.eds')
    other.nmt.wait_for_heartbeat()
    other.nmt.state = 'PRE-OPERATIONAL'

    #network.scanner.search()
    #time.sleep(0.05)
    #for node_id in network.scanner.nodes:
    #    print("Found node %d!" % node_id)
    print("Test %s" % (node.object_dictionary[0x1017]))
    print("Test2 %s" % (other.sdo[0x1017].raw))
    print("Device %s" % (other.sdo['DeviceName'].raw))
    print("Vendor ID %s" % (other.sdo[0x1018][1].raw))
    print("Heartbeat %d" % (other.sdo['Producer Heartbeat Time'].raw))
    other.sdo['Producer Heartbeat Time'].raw = 1000

    #other.pdo.read()
    #other.pdo.tx[1].clear()
    #other.pdo.tx[1].add_variable('Producer Heartbeat Time')
    #other.pdo.tx[1].trans_type = 254
    #other.pdo.tx[1].event_timer = 10
    #other.pdo.tx[1].enabled = True
    #other.pdo.save()

    network.sync.start(0.1)
    other.nmt.state = 'OPERATIONAL'

    time.sleep(10)

    network.disconnect()



if __name__ == '__main__':
    sys.exit(main())
