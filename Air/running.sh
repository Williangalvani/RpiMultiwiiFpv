#!/bin/sh
#raspivid -n -w 1920 -h 1080 -b 1000000 -t 0 -o -

last_file_sequence_number=0
last_file_sequence_number=$(ls -tr | grep file | tail -1 | sed -e s/[^0-9]//g)
new_file_sequence_number=$(($last_file_sequence_number+1))
new_file_name=file${new_file_sequence_number}.vid

raspivid -n -ex night -fps 30 -w 1280 -h 720 -b 1000000 -t 0 -o - | tee $new_file_name

