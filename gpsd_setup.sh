#!/bin/bash

#setup the gpsd to listen to the correct USART port
gpsd -n /dev/ttyO2 -F /var/run/gpsd.sock

exit
