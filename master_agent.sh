#!/bin/bash
for i in {1..150};
do 
    echo "ITER $i"
    #java homework_1
    python self_playing_agent.py;
    python AI_hw_vikas.py; 
    sleep 1
done
