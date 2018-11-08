#!/usr/bin/env bash

while true
do
    ~/tmp/winde/CANopenSocket/canopencomm/canopencomm 7 write 0x3216 0 i32 $((RANDOM % 15000))
    sleep 0.001
done

