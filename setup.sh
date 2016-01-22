#!/bin/bash

#used to setup the beaglebone environment after a fresh clone of this repo

#ONLY RUN ON A BEAGLEBON RUNNING DEBIAN

WORKING_DIR=$PWD

#ensure root permisions
if [ "$EUID" -ne 0 ]
  then echo "Please run as root"
  exit
fi

#setup the required Debian packages
apt-get update
apt-get upgrade
apt-get install -y git gpsd gpsd-clients python-gps python python-dev python-setuptools build-essential python-smbus

#install pip modules
pip install pyserial
pip install Adafruit_BBIO

#instantiate the needed git submodules
git pull --recurse-submodules
git submodule update --recursive

#install Adafruit altimeter module 
cd Adafruit_Python_BMP
python setup.py install
cd $WORKING_DIR

#TODO create the install script for LSM9DS0 and BMP180 wrappers

#install the Accelerometer module
cd LSM9DS0_Python_lib
python setup.py install
cd $WORKING_DIR

#setup the gpsd to listen to the correct USART port
cd python
python initial_uart_setup.py
#gpsd -n /dev/ttyO0 -F /var/run/gpsd.sock
gpsd -n /dev/ttyO1 -F /var/run/gpsd.sock
#gpsd -n /dev/ttyO2 -F /var/run/gpsd.sock
#gpsd -n /dev/ttyO3 -F /var/run/gpsd.sock
cd $WORKING_DIR

exit
