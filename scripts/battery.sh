#!/usr/bin/env bash

DEV=$1

while true
do
    # Minimum 2.6V + random * 0.95V
    printf -v VOLTAGE '%04x' $(((RANDOM % 2850) + 7800))

    # H:voltage*100 H:current H:energy B:tmp B:defect_cell_count
    cansend $DEV 137#${VOLTAGE}$(printf '%04x' $((RANDOM % 500 + 1)))$(printf '%04x' $((RANDOM % 201)))0000

    # H:min_voltage*100 B:min_cell_address H:max_voltage*100 B:max_cell_address B: B:cell_count
    cansend $DEV 138#$(printf '%04x' $((RANDOM % 95 + 260)))$(printf '%02x' $((RANDOM % 30 + 1)))$(printf '%04x' $((RANDOM % 95 + 260)))$(printf '%02x' $((RANDOM % 30 + 1)))001e

    # temperature: B:average B:max B:min B:reserved B:reserved B:reserved B:min_cell_address B:max_cell_address
    cansend $DEV 139#$(printf '%02x' $((RANDOM % 40)))$(printf '%02x' $((RANDOM % 40)))$(printf '%02x' $((RANDOM % 40)))000000$(printf '%02x' $((RANDOM % 30 + 1)))$(printf '%02x' $((RANDOM % 30 + 1)))

    # H:low_limit H:current_limit H:capacity*10 H:charge_level*10
    cansend $DEV 13a#0000000007d0$(printf '%04x' $((RANDOM % 1001)))

    # Data of every cell
    for I in $(seq 1 30)
    do
        # B:address H:voltage B:temperature
        cansend $DEV 13b#$(printf '%02x' $I)$(printf '%04x' $((RANDOM % 95 + 260)))$(printf '%02x' $((RANDOM % 40)))
    done
    sleep 1
done
