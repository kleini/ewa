#!/usr/bin/env bash

COUNTER=0
while true
do
    # throttle command
    ~/tmp/winde/CANopenSocket/canopencomm/canopencomm 7 write 0x3216 0 i32 $((RANDOM % 15000))
    let COUNTER++
    if [ $COUNTER -eq 100 ]; then
        # rpm 0-5000
        ~/tmp/winde/CANopenSocket/canopencomm/canopencomm 7 write 0x3207 0 i32 $((RANDOM % 5000))
        # motor temperature 0.1 degree
        ~/tmp/winde/CANopenSocket/canopencomm/canopencomm 7 write 0x320b 0 i32 $((RANDOM % 1000))
        # controller temperature 0.1 degree
        ~/tmp/winde/CANopenSocket/canopencomm/canopencomm 7 write 0x322a 0 i32 $((RANDOM % 1000))
        # voltage 0.01 volts
        ~/tmp/winde/CANopenSocket/canopencomm/canopencomm 7 write 0x324d 0 i32 $((RANDOM % 10000))
        COUNTER=0
    fi
    sleep 0.5
done

