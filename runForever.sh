#!/bin/bash
#This script run every 15 seconds
while (sleep 15 && python /home/mathieu/Projects/Oasis/domotik/dataFetcher.py) &
do
  wait $!
done