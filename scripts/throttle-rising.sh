#!/usr/bin/env bash

for I in $(seq 0 100 12351)
do
    ~/tmp/winde/CANopenSocket/canopencomm/canopencomm 7 write 0x3216 0 i32 $I
    sleep 0.1
done
for I in $(seq 12300 -100 0)
do
    ~/tmp/winde/CANopenSocket/canopencomm/canopencomm 7 write 0x3216 0 i32 $I
    sleep 0.1
done

