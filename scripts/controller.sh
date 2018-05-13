#!/usr/bin/env bash

while true
do
    ~/tmp/winde/CANopenSocket/canopencomm/canopencomm 7 write 0x2110 1 u32 $((RANDOM % 15000))
    sleep 0.001
done

