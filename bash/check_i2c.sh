#!/usr/bin/bash

GREP_FIND=`i2cdetect -y -r 1 | grep -q 77`

if $GREP_FIND; then 
  echo "BMP180 found"
else
  echo "NO BMP180 found"
fi

GREP_FIND=`i2cdetect -y -r 1 | grep -q 6b`

if $GREP_FIND; then 
  echo "LSM9DS0 GYRO found"
else
  echo "NO GYRO found"
fi

GREP_FIND=`i2cdetect -y -r 1 | grep -q 1d`

if $GREP_FIND; then 
  echo "LSM9DS0 ACCELEROMETER found"
else
  echo "NO ACCELEROMETER found"
fi
