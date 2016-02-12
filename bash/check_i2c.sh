#!/bin/bash

GREP_FIND=`i2cdetect -y -r 1 | grep 77`

if $GREP_FIND; then 
  echo "NO BMP180 found"
else
  echo "BMP180 found"
fi

GREP_FIND2=`i2cdetect -y -r 1 | grep 6b`

if $GREP_FIND2; then 
  echo "NO GYRO found"
else
  echo "LSM9DS0 GYRO found"
fi

GREP_FIND3=`i2cdetect -y -r 1 | grep 1d`

if $GREP_FIND3; then 
  echo "NO ACCELEROMETER found"
else
  echo "LSM9DS0 ACCELEROMETER found"
fi
