# Network state identifier of nodes
# Node is initializing
BOOTUP = 0x00
# Node is in pre-operational state
STOPPED = 0x04
# Node is in operational state
OPERATIONAL = 0x05
# Node is stopped
PRE_OPERATIONAL = 0x7f

# Commands from NMT master.
# Start node
ENTER_OPERATIONAL = 0x01
# Stop node
ENTER_STOPPED = 0x02
# Put node into pre-operational
ENTER_PRE_OPERATIONAL = 0x80
# Reset node
RESET_NODE = 0x81
# Reset communication on node
RESET_COMMUNICATION = 0x82

nodeId = 0

ID_NMT_SERVICE = 0x000
