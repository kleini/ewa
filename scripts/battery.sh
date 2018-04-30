#!/usr/bin/env bash

DEV=$1

# H:voltage*100 H:current H:energy B:tmp B:defect_cell_count
cansend $DEV 137#26f1000100c80000

# H:min_voltage*100 B:min_cell_address H:max_voltage*100 B:max_cell_address B: B:cell_count
cansend $DEV 138#010417016311001e

# temperature: B:average B:max B:min B:reserved B:reserved B:reserved B:min_cell_address B:max_cell_address
cansend $DEV 139#1413150000000d0e

# H:low_limit H:current_limit H:capacity*10 H:charge_level*10
cansend $DEV 13a#0000000007d003e7

# B:address H:voltage B:temperature
cansend $DEV 13b#01014014

