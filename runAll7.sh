#!/bin/bash
cd /home/buzz/Documents/cosc364/cosc364assignment/
konsole --hold --new-tab -p tabtitle='Router 1' -e $SHELL -c "python3 rip_demon.py config1.json" &
konsole --hold --new-tab -p tabtitle='Router 2' -e $SHELL -c "python3 rip_demon.py config2.json" &
konsole --hold --new-tab -p tabtitle='Router 3' -e $SHELL -c "python3 rip_demon.py config3.json" &
konsole --hold --new-tab -p tabtitle='Router 4' -e $SHELL -c "python3 rip_demon.py config4.json" &
konsole --hold --new-tab -p tabtitle='Router 5' -e $SHELL -c "python3 rip_demon.py config5.json" &
konsole --hold --new-tab -p tabtitle='Router 6' -e $SHELL -c "python3 rip_demon.py config6.json" &
konsole --hold --new-tab -p tabtitle='Router 7' -e $SHELL -c "python3 rip_demon.py config7.json" &

exit 0