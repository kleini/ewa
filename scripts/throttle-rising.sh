#!/usr/bin/env bash

for I in $(seq 0 100 12351)
do
    # throttle command
    ~/tmp/winde/CANopenSocket/canopencomm/canopencomm 7 write 0x3216 0 i32 $I
    sleep 0.1
done

